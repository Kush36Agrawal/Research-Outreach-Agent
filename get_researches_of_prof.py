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

class ProfResearches:
    def __init__(self, url ):
        self.url=url
        print(url)

    def getProfResearches(self):
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

            page_content = driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')
            text=""

            counter=0

            for nav in soup.find_all('nav', class_='publ'):
                if counter>=5:
                    break
                counter+=1

                # Find the first <li> under this <nav>
                first_li = nav.select_one('ul li')
                
                # Find the <a> tag within the first <li>
                first_a_tag = first_li.find('a') if first_li else None

                # Get the href attribute (the URL)
                if first_a_tag:
                    first_url = first_a_tag.get('href')
                    text+=f"{first_url}\n"


            # Close the driver once done
            driver.quit()


            return text.strip()

        except Exception as e:
            print(f"Error: {str(e)}")
            return None
    
file_name = "user_agent.txt"
text=ProfResearches("https://dblp.org/pid/24/2104.html").getProfResearches()

with open("user_agent.txt", "w", encoding="utf-8") as file:
    file.write(text)