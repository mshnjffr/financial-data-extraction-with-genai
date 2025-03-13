import re
import json
from typing import Dict, Tuple, Optional, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialDataProcessor:
    """Process and extract financial data from API responses"""
    
    def __init__(self, extraction_patterns: Optional[Dict[str, str]] = None):
        """
        Initialize with extraction patterns.
        
        Args:
            extraction_patterns: Dictionary mapping data types to regex patterns
        """
        self.extraction_patterns = extraction_patterns or {
            "company name": r"Company name:?\s*(.+?)(?:\n|$)",
            "stock symbol": r"Stock symbol:?\s*(.+?)(?:\n|$)",
            "revenue": r"Revenue:?\s*(.+?)(?:\n|$)",
            "net income": r"Net income:?\s*(.+?)(?:\n|$)",
            "EPS": r"EPS:?\s*(.+?)(?:\n|$)"
        }
        self.min_data_points = 3  # Minimum data points to consider extraction successful    
    def parse_financial_data(self, response: Dict[str, Any]) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
        """
        Parse financial data from API response.
        
        Args:
            response: The API response to parse
            
        Returns:
            Tuple containing (parsed_data, error_or_summary)
              - If successful: (data_dict, None)
              - If error or insufficient data: (None, error_message_or_summary)
        """
        if "error" in response:
            error_msg = self._format_error_message(response)
            print("\n===== ERROR IN RESPONSE =====")
            print(f"Error message: {error_msg}")
            return None, error_msg
        
        try:
            print("\n===== PARSING FINANCIAL DATA =====")
            
            # Extract content from response
            message = response.get("choices", [{}])[0].get("message", {})
            content = message.get("content", "")
            
            print(f"Message content length: {len(content)} chars")
            print(f"Content preview: {content[:100]}...")
            
            # Try to extract structured data
            data = self._extract_data_from_content(content)
            
            print(f"Extracted data points: {len(data)}")
            if data:
                print(f"Found data: {json.dumps(data, indent=2)}")
            
            # Decide if we have enough data
            if len(data) >= self.min_data_points:
                print(f"Sufficient data points detected ({len(data)} >= {self.min_data_points})")
                return data, None
            else:
                print(f"Insufficient data points ({len(data)} < {self.min_data_points})")
                print("Returning content as summary instead")
                return None, content
        
        except Exception as e:
            print("\n===== ERROR PARSING DATA =====")
            print(f"Exception: {str(e)}")
            logger.error(f"Error parsing financial data: {str(e)}")
            return None, f"Parsing Error: {str(e)}"    
    def _format_error_message(self, response: Dict[str, Any]) -> str:
        """Format error message from API response"""
        error_msg = f"API Error: {response['error']}"
        
        if "response_body" in response:
            error_msg += f"\n\nResponse Body: {json.dumps(response['response_body'], indent=2)}"
        
        return error_msg
    
    def _extract_data_from_content(self, content: str) -> Dict[str, str]:
        """Extract structured data using regex patterns"""
        data = {}
        
        for key, pattern in self.extraction_patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match and match.group(1).strip() not in ["Not found", "N/A", "Unknown"]:
                data[key] = match.group(1).strip()
        
        return data
    
    def create_prompt(self, url: str) -> str:
        """Create a prompt for financial data extraction"""
        return f"""
        I need to extract financial data from this URL: {url}

        First, please use the fetch_url_content tool to get the content from the URL.
        
        Then, extract the following information from the article:
        - Company name
        - Stock symbol
        - Revenue
        - Net income
        - EPS (Earnings Per Share)
        
        Format your answer as:
        - Company name: [Company Name]
        - Stock symbol: [Stock Symbol]
        - Revenue: [Revenue]
        - Net income: [Net Income]
        - EPS: [EPS]
        
        If any information isn't available, indicate with "Not found". If you can't extract structured data at all, provide a brief summary of the article content.
        """
