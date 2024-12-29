import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse


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

    def getProfResearch(self) -> str:
        if not is_valid_url(self.url):
            print("Error: Invalid URL")
            return None

        print(self.url)

        try:
            with sync_playwright() as p:
                # Launch a headless browser
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()
                
                # Navigate to the URL
                page.goto(self.url, timeout=60000)  # Set a timeout of 60 seconds
                
                # Get the page content
                page_content = page.content()

                # Close the browser
                browser.close()

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