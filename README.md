# Financial Data Extractor

![Financial Data Extractor]

An AI-powered application that extracts structured financial data from news articles and financial reports. This tool leverages LLM capabilities through the Cody API to automatically identify key financial metrics from URLs.

## Features

- Extract key financial metrics (Company name, Stock symbol, Revenue, Net income, EPS)
- Support for multiple language models via Cody API
- Beautiful, responsive UI built with Streamlit
- Configurable API parameters (max tokens, temperature, etc.)
- Error handling and detailed logging
- Persistent model selection between sessions

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/financial-data-extractor.git
   cd financial-data-extractor
   ```

2. Create a `.env` file in the root directory with the following variables:
   ```
   SG_ACCESS_TOKEN=your_access_token_here
   SG_MODELS_ENDPOINT=/.api/llm/models
   SG_CHAT_COMPLETIONS_ENDPOINT=your_chat_completions_endpoint_here
   X_Requested_With=YourApplication
   ```

## Usage

Run the application:

```zshrc
streamlit run main.py
```

Then, navigate to the provided URL (usually http://localhost:8501) in your web browser.

### Extracting Financial Data

1. Select a model from the dropdown in the sidebar
2. Configure API parameters if needed
3. Enter a URL to a financial news article or report
4. Click "Extract Data"
5. View the extracted financial metrics or summary


### Components

- **main.py**: Application entry point and orchestration
- **config.py**: Configuration management
- **api_client.py**: Handles API interactions with Cody
- **data_processor.py**: Processes and extracts financial data
- **url_scraper.py**: Fetches and parses web content
- **ui_components.py**: UI elements and layouts

### Data Flow

1. User inputs a URL
2. Application fetches content using BeautifulSoup
3. Content is sent to the Cody API with appropriate tools
4. API response is processed to extract structured financial data
5. Results are displayed in a user-friendly format

## Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| Max Tokens | Maximum number of tokens in response | 1000 |
| Temperature | Randomness of completion (0-2) | 0.3 |
| Top P | Nucleus sampling parameter (0-1) | 0.95 |

## Dependencies

- Streamlit
- Requests
- BeautifulSoup4
- Python-dotenv
- Pandas

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Streamlit](https://streamlit.io/)
- [Sourcegraph Cody](https://sourcegraph.com/cody)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)

## Project structure
```
financial_data_extraction
├── README.md
├── api_client.py
├── config.py
├── data_processor.py
├── main.py
├── pyproject.toml
├── ui_components.py
├── url_scraper.py
└── uv.lock
```