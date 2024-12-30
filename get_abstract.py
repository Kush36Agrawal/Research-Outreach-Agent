import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from playwright.async_api import async_playwright

def is_valid_url(url: str) -> bool:
    """Check if the provided URL is valid and ensure it starts with 'https://'."""

    if not url.lower().startswith('https://'):      # Step 1: Ensure the URL starts with 'https://'
        url = 'https://' + url

    try:
        result = urlparse(url)                      # Step 2: Validate the URL
        return all([result.scheme, result.netloc])
    except:
        return False

class ProfessorResearch:
    """Fetch the webpage content, extract readable text, and capture all redirecting elements within the text."""
    
    def __init__(self, url: str):
        self.url = url

    async def getProfResearch(self) -> str:
        if not is_valid_url(self.url):
            print("Error: Invalid URL")
            return None
        
        print(self.url)

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                page = await browser.new_page()
                
                # Navigate to the URL
                await page.goto(self.url, timeout=60000)  # Set a timeout of 60 seconds

                # Wait for the page to load by waiting for a specific selector (e.g., <body> tag)
                await page.wait_for_selector('body', timeout=60000)  

                # Get the page content
                page_content = await page.content()

                # Close the browser
                await browser.close()

            # Create BeautifulSoup object from the page source
            soup = BeautifulSoup(page_content, 'html.parser')

            # Remove script and style elements
            for element in soup(["script", "style", "meta", "noscript", "header", "footer", "nav"]):
                element.decompose()

            # Get text content
            text = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            # Remove multiple newlines
            text = re.sub(r'\n\s*\n', '\n\n', text)

            return text.strip()

        except Exception as e:
            print(f"Error: {str(e)}")
            return None