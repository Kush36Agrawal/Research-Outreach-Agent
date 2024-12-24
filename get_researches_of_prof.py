from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urlparse
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def is_valid_url(url):
    """Check if the provided URL is valid and ensure it starts with 'https://'."""

    if not url.lower().startswith('https://'):      # Step 1: Ensure the URL starts with 'https://'
        url = 'https://' + url

    try:
        result = urlparse(url)                      # Step 2: Validate the URL
        return all([result.scheme, result.netloc])
    except:
        return False

class ProfResearches:
    """Fetch the Research Links of Prof using DBLP Link."""
    
    def __init__(self, url ):
        self.url=url

    def getProfResearches(self):

        if not is_valid_url(self.url):
            print("Error: Invalid URL")
            return None
        print(self.url)

        try:

            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            
            driver.get(self.url)

            page_content = driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')
            research_links=[]

            counter=0

            for nav in soup.find_all('nav', class_='publ'):
                if counter>=3:
                    break
                counter+=1

                # Find the first <li> under this <nav>
                first_li = nav.select_one('ul li')
                
                # Find the <a> tag within the first <li>
                first_a_tag = first_li.find('a') if first_li else None

                # Get the href attribute (the URL)
                if first_a_tag:
                    first_url = first_a_tag.get('href')
                    research_links.append(first_url)

            driver.quit()

            return research_links

        except Exception as e:
            print(f"Error: {str(e)}")
            return None