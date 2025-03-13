import streamlit as st
from config import AppConfig
from api_client import ApiClient, ApiCredentials
from data_processor import FinancialDataProcessor
from ui_components import (
    setup_page_config, 
    display_financial_data, 
    display_summary,
    create_model_selector,
    create_api_config_controls,
    create_url_input,
    display_progress
)
from url_scraper import fetch_url_content

# Add this function to main.py
def log_section(title, message=None):
    """Helper to log section headers consistently"""
    print(f"\n===== {title} =====")
    if message:
        print(message)

def main():
    """Main application entry point."""
    # Initialize configuration
    config = AppConfig.from_env()
    
    # Validate configuration
    if not config.validate():
        st.error("Please set all required environment variables in the .env file.")
        st.code("""
        SG_ACCESS_TOKEN=your_access_token_here
        SG_MODELS_ENDPOINT=/.api/llm/models
        SG_CHAT_COMPLETIONS_ENDPOINT=your_chat_completions_endpoint_here
        """)
        st.stop()
    
    # Setup page
    setup_page_config()
    
    # Display header
    st.markdown('<h1 class="main-header">Financial Data Extractor</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Extract financial data from news articles using AI</p>', unsafe_allow_html=True)
    
    # Initialize API client
    credentials = ApiCredentials(
        access_token=config.access_token,
        models_endpoint=config.models_endpoint,
        chat_completions_endpoint=config.chat_completions_endpoint,
        x_requested_with=config.x_requested_with
    )
    api_client = ApiClient(credentials)
    
    # Sidebar for configuration
    st.sidebar.title("Configuration")
    
    # Initialize session state for selected model if it doesn't exist
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = None

    # Load models with spinner
    with st.spinner("Fetching available models..."):
        models_data = api_client.fetch_models()
    
    # Select model, passing the current selection from session state
    selected_model = create_model_selector(models_data, st.session_state.selected_model)

    # Save the selection to session state for future runs
    st.session_state.selected_model = selected_model    
    # API parameters
    api_params = create_api_config_controls()
    
    # URL input
    url, process_button = create_url_input()
    
    # Initialize data processor
    data_processor = FinancialDataProcessor()
    
    # Process the URL when button is clicked
    # Example usage in main function:
    if process_button:
        if not url:
            st.error("Please enter a URL")
        else:
            log_section("PROCESS STARTED", f"URL: {url}, Model: {selected_model}")
            
            # Show progress
            progress_bar, progress_text = display_progress("Processing URL with AI...", 25)
            
            # Define tool handlers
            tool_handlers = {
                "fetch_url_content": fetch_url_content
            }
            
            # Create the prompt for extraction
            prompt = data_processor.create_prompt(url)
            
            # Prepare the API payload
            payload = {
                "model": selected_model,
                "messages": [
                    {
                        "role": "assistant",
                        "content": "You are a financial data extraction assistant. Extract the requested financial information from the provided URL accurately. Use the fetch_url_content tool to access the content of the URL. Only use information explicitly stated in the article."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "fetch_url_content",
                            "description": "Fetches content from a URL with proper headers to avoid blocking",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "url": {
                                        "type": "string",
                                        "description": "The URL to extract content from"
                                    }
                                },
                                "required": ["url"]
                            }
                        }
                    }
                ],
                "tool_choice": "auto",
                "max_tokens": api_params["max_tokens"],
                "temperature": api_params["temperature"],
                "top_p": api_params["top_p"]
            }
            
            # Process with the API
            response = api_client.process_with_tools(
                payload=payload,
                tool_handlers={"fetch_url_content": fetch_url_content}
            )
            
            # Update progress
            progress_text.text("AI processing complete. Analyzing results...")
            progress_bar.progress(75)
            
            # Parse financial data
            data, error_or_summary = data_processor.parse_financial_data(response)
            
            # Complete progress
            progress_text.text("Process complete!")
            progress_bar.progress(100)
            
            # Clear progress indicators
            progress_text.empty()
            progress_bar.empty()
            
            # Display results
            if data:
                display_financial_data(data)
            else:
                display_summary(error_or_summary)
            
            # Show raw response in expander
            with st.expander("Raw API Response"):
                st.json(response)

            log_section("PROCESS COMPLETE")

if __name__ == "__main__":
    main()