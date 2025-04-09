"""Web scraper module for extracting content from websites."""

import trafilatura
import pandas as pd
from datetime import datetime

class WebScraper:
    """Web scraper for extracting and analyzing content from various websites."""
    
    def __init__(self):
        """Initialize the web scraper."""
        # Track recently scraped URLs for caching purposes
        self.scraped_cache = {}
    
    def get_website_text_content(self, url):
        """
        Extract the main text content from a website.
        
        Args:
            url: URL of the website to scrape
            
        Returns:
            String containing the extracted text content
        """
        # Check cache first to avoid repeated requests
        if url in self.scraped_cache:
            return self.scraped_cache[url]
            
        try:
            # Send a request to the website
            downloaded = trafilatura.fetch_url(url)
            
            if not downloaded:
                return f"Error: Could not download content from {url}"
                
            # Extract the main text content
            text = trafilatura.extract(downloaded)
            
            if not text:
                return f"Error: No content could be extracted from {url}"
                
            # Cache the result
            self.scraped_cache[url] = text
            return text
            
        except Exception as e:
            return f"Error scraping {url}: {str(e)}"
            
    def extract_structured_data(self, url):
        """
        Extract structured data from a website, attempting to identify key information.
        
        Args:
            url: URL of the website to scrape
            
        Returns:
            Dictionary containing structured data elements
        """
        text = self.get_website_text_content(url)
        
        # If an error occurred during scraping
        if text.startswith("Error:"):
            return {"error": text}
            
        # Create a basic structure with timestamp and source
        structured_data = {
            "source_url": url,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": text,
            "word_count": len(text.split()),
            "character_count": len(text)
        }
        
        return structured_data
        
    def compare_websites(self, urls):
        """
        Compare content from multiple websites.
        
        Args:
            urls: List of URLs to compare
            
        Returns:
            DataFrame with comparison metrics
        """
        if not urls:
            return pd.DataFrame()
            
        comparison_data = []
        
        for url in urls:
            text = self.get_website_text_content(url)
            
            # Skip URLs that couldn't be scraped
            if text.startswith("Error:"):
                comparison_data.append({
                    "url": url,
                    "status": "Error",
                    "word_count": 0,
                    "character_count": 0
                })
                continue
                
            comparison_data.append({
                "url": url,
                "status": "Success",
                "word_count": len(text.split()),
                "character_count": len(text)
            })
            
        return pd.DataFrame(comparison_data)
        
    def export_to_csv(self, data, filename=None):
        """
        Export scraped data to CSV format.
        
        Args:
            data: String content or DataFrame to export
            filename: Optional filename (defaults to timestamp)
            
        Returns:
            CSV data as bytes
        """
        if filename is None:
            filename = f"web_scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
        if isinstance(data, pd.DataFrame):
            # If it's already a DataFrame, export directly
            csv_bytes = data.to_csv(index=False).encode('utf-8')
        elif isinstance(data, dict):
            # Convert dictionary to DataFrame
            df = pd.DataFrame([data])
            csv_bytes = df.to_csv(index=False).encode('utf-8')
        else:
            # For plain text, create a simple one-column DataFrame
            df = pd.DataFrame({"content": [data]})
            csv_bytes = df.to_csv(index=False).encode('utf-8')
            
        return csv_bytes