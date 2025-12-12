
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from typing import List, Dict
import time

class WebScraper:
    """Handles deep internet research without opening a browser."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }

    def search_google(self, query: str, num_results: int = 5) -> List[str]:
        """Get top URLs for a query."""
        results = []
        try:
            # Use pause to avoid rate limits
            for url in search(query, num_results=num_results, advanced=True):
                results.append(url.url)
        except Exception as e:
            print(f"Search error: {e}")
        return results

    def extract_text(self, url: str) -> str:
        """Extract main content text from a URL."""
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
                
            text = soup.get_text()
            
            # Clean text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = ' '.join(chunk for chunk in chunks if chunk)
            
            return clean_text[:5000] # Limit content length
            
        except Exception as e:
            return f"Error reading {url}: {e}"

    def research_topic(self, topic: str, num_sources: int = 3) -> Dict[str, str]:
        """Search and extract text from multiple sources."""
        print(f"🔎 Searching for: {topic}...")
        urls = self.search_google(topic, num_results=num_sources)
        
        results = {}
        for i, url in enumerate(urls, 1):
            print(f"   📄 Reading source {i}/{len(urls)}: {url[:50]}...")
            text = self.extract_text(url)
            results[url] = text
            time.sleep(1) # Be polite
            
        return results
