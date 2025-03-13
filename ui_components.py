import streamlit as st
import pandas as pd
import json
from typing import Dict, Optional, Any

def setup_page_config():
    """Configure the Streamlit page"""
    st.set_page_config(
        page_title="Financial Data Extractor",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E3A8A;
        }
        .subheader {
            font-size: 1.5rem;
            color: #2563EB;
        }
        .success-box {
            background-color: #ECFDF5;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #10B981;
        }
        .warning-box {
            background-color: #FFFBEB;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #F59E0B;
        }
    </style>
    """, unsafe_allow_html=True)

def display_financial_data(data: Dict[str, str]):
    """Display the financial data in a formatted table."""
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.markdown("### Financial Data Extracted")
    
    # Create two columns for better presentation
    col1, col2 = st.columns(2)
    
    # Display the data
    with col1:
        st.metric("Company Name", data.get("company name", "N/A"))
        st.metric("Stock Symbol", data.get("stock symbol", "N/A"))
        st.metric("EPS", data.get("EPS", "N/A"))
    
    with col2:
        st.metric("Revenue", data.get("revenue", "N/A"))
        st.metric("Net Income", data.get("net income", "N/A"))
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Also display as a table for completeness
    st.subheader("Data Table")
    table_data = {"Measure": list(data.keys()), "Value": list(data.values())}
    df = pd.DataFrame(table_data)
    st.table(df.set_index('Measure'))

def display_summary(content: str):
    """Display a summary of the content when structured data extraction fails."""
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    
    # Check if this is an error message with API details
    if content.startswith("API Error:"):
        st.markdown("### Error Processing Request")
        
        # Split error message from response body if present
        if "\n\nResponse Body:" in content:
            error_part, response_body_part = content.split("\n\nResponse Body:", 1)
            
            # Display error message
            st.error(error_part)
            
            # Display formatted response body in an expander
            with st.expander("View API Response Details"):
                try:
                    # Try to parse as JSON for pretty display
                    response_body = response_body_part.strip()
                    st.json(response_body)
                except:
                    # If not valid JSON, show as code block
                    st.code(response_body_part.strip())
        else:
            # Display simple error
            st.error(content)
    else:
        # Standard content summary display
        st.markdown("### Content Summary")
        st.markdown("Unable to extract structured financial data. Here's a summary instead:")
        st.markdown(content)
    
    st.markdown('</div>', unsafe_allow_html=True)

def format_model_name(model_id: str) -> str:
    """Format model ID for display."""
    # Extract the model name after the last ::
    if "::" in model_id:
        parts = model_id.split("::")
        if len(parts) >= 3:
            return f"{parts[0]} - {parts[-1]}"
    return model_id

def create_model_selector(models_data: Dict[str, Any], default_model: str = None) -> str:
    """Create and display the model selection UI components"""
    sidebar_model_status = st.sidebar.empty()
    
    if models_data is None:
        sidebar_model_status.error("Failed to fetch models")
        st.error("Failed to fetch models. Please check your API credentials and try again.")
        st.stop()
    
    sidebar_model_status.text("Models loaded successfully")
    
    # Display available models and let user select
    available_models = models_data.get("data", [])
    if not available_models:
        st.error("No models available. Please check your API setup.")
        st.stop()
    
    # Use 'id' field instead of 'name' field
    model_ids = [model.get("id") for model in available_models if model.get("id")]
    
    # Create display names for the dropdown
    model_display_names = [format_model_name(model_id) for model_id in model_ids]
    
    # Create a dictionary to map display names back to model IDs
    model_name_to_id = dict(zip(model_display_names, model_ids))
    
    # Find default display name if a default model ID was provided
    default_display = None
    if default_model:
        for display_name, model_id in model_name_to_id.items():
            if model_id == default_model:
                default_display = display_name
                break
    
    # Use default if available, otherwise let Streamlit choose the first item
    index = model_display_names.index(default_display) if default_display else 0
    selected_model_display = st.sidebar.selectbox("Select Model", model_display_names, index=index)
    selected_model = model_name_to_id[selected_model_display]
    
    # Show the actual model ID that will be used
    st.sidebar.caption(f"Model ID: {selected_model}")
    
    # Display model list in an expander
    with st.sidebar.expander("Available Models"):
        for model in available_models:
            model_id = model.get("id", "")
            provider = model.get("owned_by", "Unknown Provider")
            
            st.markdown(f"**{format_model_name(model_id)}**")
            st.markdown(f"Provider: {provider}")
            st.markdown(f"Full ID: `{model_id}`")
            st.markdown("---")
    
    return selected_model
def create_api_config_controls():
    """Create UI controls for API configuration parameters"""
    st.sidebar.subheader("API Parameters")
    max_tokens = st.sidebar.slider("Max Tokens", min_value=100, max_value=4000, value=1000, step=100)
    temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=2.0, value=0.3, step=0.1)
    top_p = st.sidebar.slider("Top P", min_value=0.0, max_value=1.0, value=0.95, step=0.05)
    
    return {
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p
    }

def create_url_input():
    """Create URL input field and extraction button"""
    st.subheader("Enter Financial News URL")
    
    # URL input
    url = st.text_input("URL", "https://www.cnbc.com/2025/01/30/apple-aapl-q1-earnings-2025.html")
    
    # Process button
    col1, col2 = st.columns([1, 3])
    with col1:
        process_button = st.button("Extract Data", type="primary", use_container_width=True)
    
    # Help text
    with col2:
        st.markdown("*Enter a URL to a financial news article and click Extract Data*")
    
    return url, process_button

def display_progress(message, progress_percent):
    """Display progress bar with message"""
    progress_bar = st.progress(progress_percent)
    progress_text = st.empty()
    progress_text.text(message)
    return progress_bar, progress_text
