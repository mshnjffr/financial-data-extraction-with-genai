import os
import json
import requests
import logging
from typing import Dict, Optional, Any, List
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ApiCredentials:
    """Class to hold API credentials"""
    access_token: str
    models_endpoint: str
    chat_completions_endpoint: str
    x_requested_with: Optional[str] = None

class ApiClient:
    """Client for interacting with the Cody API"""
    
    def __init__(self, credentials: ApiCredentials):
        self.credentials = credentials
        self.default_headers = {
            "Content-Type": "application/json",
            "Authorization": credentials.access_token
        }
        if credentials.x_requested_with:
            self.default_headers["X-Requested-With"] = credentials.x_requested_with
    
    def fetch_models(self) -> Optional[Dict[str, Any]]:
        """Fetch available models from the API."""
        try:
            response = requests.get(
                self.credentials.models_endpoint, 
                headers=self.default_headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching models: {str(e)}")
            return None
    
    def process_with_tools(self, 
                           payload: Dict[str, Any], 
                           tool_handlers: Dict[str, callable],
                           log_requests: bool = True) -> Dict[str, Any]:
        """
        Process a request with tool support.
        
        Args:
            payload: The initial payload to send
            tool_handlers: Dictionary mapping tool names to handler functions
            log_requests: Whether to log requests and responses
            
        Returns:
            The final API response
        """
        try:
            if log_requests:
                print(f"\n===== INITIAL REQUEST to {self.credentials.chat_completions_endpoint} =====")
                print(f"Headers: {json.dumps(self.default_headers, indent=2)}")
                print(f"Payload: {json.dumps(payload, indent=2)}")
                
            # Initial request
            response = requests.post(
                self.credentials.chat_completions_endpoint,
                headers=self.default_headers,
                json=payload
            )
            response.raise_for_status()
            response_data = response.json()
            
            if log_requests:
                print(f"\n===== INITIAL RESPONSE =====")
                print(f"Status Code: {response.status_code}")
                print(f"Response: {json.dumps(response_data, indent=2)}")
            
            # Handle tool calls
            message = response_data["choices"][0]["message"]
            messages_so_far = payload["messages"] + [message]
            
            conversation_turn = 1
            
            # Continue conversation until no more tool calls
            while "tool_calls" in message:
                if log_requests:
                    print(f"\n===== TOOL CALL DETECTED (Turn {conversation_turn}) =====")
                
                tool_calls = message.get("tool_calls", [])
                for tool_call in tool_calls:
                    function_call = tool_call.get("function", {})
                    function_name = function_call.get("name")
                    
                    if log_requests:
                        print(f"Tool Call ID: {tool_call.get('id')}")
                        print(f"Function Name: {function_name}")
                        print(f"Arguments: {function_call.get('arguments')}")
                    
                    # Execute tool handler if registered
                    if function_name in tool_handlers:
                        args = json.loads(function_call.get("arguments", "{}"))
                        
                        if log_requests:
                            print(f"\nExecuting tool: {function_name} with args: {args}")
                        
                        content, error = tool_handlers[function_name](**args)
                        
                        if content:
                            if log_requests:
                                print(f"Tool execution successful - Content length: {len(content)} chars")
                            tool_response = {
                                "tool_call_id": tool_call.get("id"),
                                "role": "assistant",
                                "content": content
                            }
                        else:
                            if log_requests:
                                print(f"Tool execution failed: {error}")
                            tool_response = {
                                "tool_call_id": tool_call.get("id"),
                                "role": "assistant", 
                                "content": f"Error: {error}"
                            }
                        
                        messages_so_far.append(tool_response)
                
                # Continue conversation
                continuation_payload = {
                    "model": payload["model"],
                    "messages": messages_so_far,
                    "max_tokens": payload.get("max_tokens", 1000),
                    "temperature": payload.get("temperature", 0.3),
                    "top_p": payload.get("top_p", 0.95)
                }
                
                if log_requests:
                    print(f"\n===== CONTINUATION REQUEST (Turn {conversation_turn}) =====")
                    print(f"Payload messages count: {len(continuation_payload['messages'])}")
                    # Don't print all messages as it can be too verbose
                    print(f"Last message role: {continuation_payload['messages'][-1]['role']}")
                
                # Make continuation request
                response = requests.post(
                    self.credentials.chat_completions_endpoint,
                    headers=self.default_headers,
                    json=continuation_payload
                )
                response.raise_for_status()
                response_data = response.json()
                
                if log_requests:
                    print(f"\n===== CONTINUATION RESPONSE (Turn {conversation_turn}) =====")
                    print(f"Status Code: {response.status_code}")
                    print(f"Response: {json.dumps(response_data, indent=2)}")
                
                message = response_data["choices"][0]["message"]
                messages_so_far.append(message)
                conversation_turn += 1
            
            print("\n===== FINAL RESPONSE RECEIVED =====")
            return response_data
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n===== ERROR IN API CLIENT =====")
            print(f"Error: {error_msg}")
            
            # Include response body if available
            if 'response' in locals() and hasattr(response, 'text'):
                print(f"Response Status: {response.status_code}")
                try:
                    response_body = response.json()
                    print(f"Response Body: {json.dumps(response_body, indent=2)}")
                    return {"error": error_msg, "response_body": response_body}
                except:
                    print(f"Response Text: {response.text[:500]}...")
                    return {"error": error_msg, "response_body": response.text}
            else:
                return {"error": error_msg}