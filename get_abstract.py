from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import requests
import re
from urllib.parse import urlparse

def is_valid_url(url):
    """Check if the provided URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

class ResearchAbstract():

    def __init__(self, url):
        self.url=url
        print(url)

    def getResearchAbstract(self):
        url=self.url
        """Fetch the webpage content, extract readable text, and capture all redirecting elements within the text."""
        if not is_valid_url(url):
            print("Error: Invalid URL format")
            return None

        try:
            # Set up Selenium WebDriver (using Chrome in this case)
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")  # Optional: run in headless mode (no UI)
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            
            # Open the URL
            driver.get(url)

            # Wait for dynamic content to load (adjust the wait time or condition based on the page)
            # Interact with all dropdowns on the page
            
            page_content = driver.page_source

            # Close the driver once done
            driver.quit()

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

            # Embed links (URLs in <a> tags) into the text
            

            return text.strip()

        except Exception as e:
            print(f"Error: {str(e)}")
            return None
    
# file_name = "user_agent.txt"
# text=ResearchAbstract("https://doi.org/10.4230/LIPIcs.ECOOP.2024.17").getResearchAbstract()

# with open("user_agent.txt", "w", encoding="utf-8") as file:
#     file.write(text)