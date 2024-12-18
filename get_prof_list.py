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

def get_webpage_text(url):
    print(url)
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
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        text=""

        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "centerscreen"))
        )

        dropdowns = driver.find_elements(By.ID, "regions")


        for dropdown in dropdowns:
            try:
                dropdown.click()  # Open the dropdown
                time.sleep(2)  # Wait for dropdown to load options
                options = dropdown.find_elements(By.TAG_NAME, "option")  # Get all options in the dropdown
                # options=options[:2]
                for option in options:
                    option.click()
                    option_text = option.text
                    text += "\n"  # Ensure a new line starts
                    text += "#############################################################################################################\n"
                    text += option_text + "\n"  # Dropdown option text on a new line
                    text += "#############################################################################################################\n"
                    time.sleep(2)
                    page_content = driver.page_source
                    soup = BeautifulSoup(page_content, 'html.parser')
                    print(f"Dropdown option: {option_text}")  # Print out the option text (optional)
                    for a_tag in soup.find_all("a", href=True):
                        parent_td = a_tag.find_parent("td")
                        if parent_td and parent_td.get("align") == "right":
                            continue  # Skip this <a> tag

                        if ("title" in a_tag.attrs and "Click for author's home page." in a_tag["title"]):
                            author_name = a_tag.get_text(strip=True)
                            if author_name:
                                text+="\n"
                                text+="\n"
                                text += f"Name: {author_name}"
                            else:
                                link_url = a_tag["href"]
                                if link_url.startswith("/"):
                                    link_url = urlparse(url)._replace(path=link_url).geturl()
                                # Embed the link URL into the text
                                text += f"\n\n[Link: {link_url}]"

                            
                        if ("title" in a_tag.attrs and "Click for author's Google Scholar page." in a_tag["title"]):
                            link_url = a_tag["href"]
                            if link_url.startswith("/"):
                                link_url = urlparse(url)._replace(path=link_url).geturl()
                            # Embed the link URL into the text
                            text += f"\n\n[Link: {link_url}]"
                        if ("title" in a_tag.attrs and "Click for author's DBLP entry." in a_tag["title"]):
                            link_url = a_tag["href"]
                            if link_url.startswith("/"):
                                link_url = urlparse(url)._replace(path=link_url).geturl()
                            # Embed the link URL into the text
                            text += f"\n\n[Link: {link_url}]"
                            

            except Exception as e:
                print(f"Error interacting with dropdown: {str(e)}")


        driver.quit()

        return text.strip()

    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    
file_name = "user_agent.txt"

with open("user_agent.txt", "w", encoding="utf-8") as file:
    file.write(get_webpage_text("https://www.csrankings.org"))

