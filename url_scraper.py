import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, Optional, Union, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_url_content(url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Fetch content from a URL using Beautiful Soup.
    
    Args:
        url (str): The URL to fetch content from
        
    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple containing (content, error_message)
                                           If successful, error_message will be None
                                           If failed, content will be None
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }
    
    try:
        logger.info(f"Fetching content from URL: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse with Beautiful Soup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements that might contain unwanted text
        for script_or_style in soup(['script', 'style', 'nav', 'footer', 'header']):
            script_or_style.decompose()
            
        # Extract text content
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up text (remove excessive whitespace)
        clean_text = ' '.join(text.split())
        
        logger.info(f"Successfully fetched and parsed content from {url} - Content length: {len(clean_text)} chars")
        return clean_text, None
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching URL {url}: {str(e)}"
        logger.error(error_msg)
        return None, error_msg
    except Exception as e:
        error_msg = f"Unexpected error processing URL {url}: {str(e)}"
        logger.error(error_msg)
        return None, error_msg

def extract_article_content(url: str) -> Dict[str, Union[str, bool]]:
    """
    Extract article content from a URL with metadata.
    
    Args:
        url (str): The URL to extract content from
        
    Returns:
        Dict: A dictionary containing:
            - success: Boolean indicating success or failure
            - content: The extracted content (if success is True)
            - error: Error message (if success is False)
            - title: Article title (if available)
            - meta_description: Meta description (if available)
    """
    try:
        logger.info(f"Extracting article content from URL: {url}")
        response = requests.get(
            url, 
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            },
            timeout=30
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = soup.title.string if soup.title else "No title found"
        
        # Extract meta description
        meta_desc_tag = soup.find("meta", attrs={"name": "description"})
        meta_description = meta_desc_tag.get("content", "") if meta_desc_tag else "No description found"
        
        # Extract the main content - this is a simplified approach
        # For better results, you might need to customize based on site structure
        for unwanted in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            unwanted.decompose()
            
        # Try to find article content (customize based on common article structures)
        main_content = None
        
        # Look for common article containers
        for selector in ['article', 'main', '.article', '.post', '.content', '#content', '[role="main"]']:
            content_container = soup.select_one(selector)
            if content_container:
                main_content = content_container.get_text(separator=' ', strip=True)
                break
        
        # If no container found, use body content
        if not main_content:
            main_content = soup.body.get_text(separator=' ', strip=True) if soup.body else "No content found"
        
        # Clean up text
        main_content = ' '.join(main_content.split())
        
        logger.info(f"Successfully extracted article content from {url}")
        return {
            "success": True,
            "content": main_content,
            "title": title,
            "meta_description": meta_description
        }
        
    except Exception as e:
        error_msg = f"Error extracting article content from {url}: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }
