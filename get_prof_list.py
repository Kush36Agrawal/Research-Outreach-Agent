import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def region_code(region):
    locations = {
    # Countries
    "Argentina": "ar",
    "Australia": "au",
    "Austria": "at",
    "Bangladesh": "bd",
    "Belgium": "be",
    "Brazil": "br",
    "Canada": "ca",
    "Chile": "cl",
    "China": "cn",
    "Colombia": "co",
    "Cyprus": "cy",
    "Czech Republic": "cz",
    "Denmark": "dk",
    "Egypt": "eg",
    "Estonia": "ee",
    "Finland": "fi",
    "France": "fr",
    "Germany": "de",
    "Greece": "gr",
    "Hong Kong": "hk",
    "Hungary": "hu",
    "India": "in",
    "Iran": "ir",
    "Ireland": "ie",
    "Israel": "il",
    "Italy": "it",
    "Japan": "jp",
    "Jordan": "jo",
    "Lebanon": "lb",
    "Luxembourg": "lu",
    "Macao": "mo",
    "Malaysia": "my",
    "Malta": "mt",
    "Netherlands": "nl",
    "New Zealand": "nz",
    "Norway": "no",
    "Pakistan": "pk",
    "Philippines": "ph",
    "Poland": "pl",
    "Portugal": "pt",
    "Qatar": "qa",
    "Romania": "ro",
    "Russia": "ru",
    "Saudi Arabia": "sa",
    "Singapore": "sg",
    "South Africa": "za",
    "South Korea": "kr",
    "Spain": "es",
    "Sri Lanka": "lk",
    "Sweden": "se",
    "Switzerland": "ch",
    "Thailand": "th",
    "Taiwan": "tw",
    "Turkey": "tr",
    "United Arab Emirates": "ae",
    "United Kingdom": "uk",
    "USA": "us",
    # Continents
    "North America": "northamerica",
    "South America": "southamerica",
    "Africa": "africa",
    "Asia": "asia",
    "Australasia": "australasia",
    "Europe": "europe",
    "The World": "world"
    }


    return locations.get(region, "unknown")  # Default to "unknown" if the region is not found

def is_valid_url(url):
    """Check if the provided URL is valid and ensure it starts with 'https://'."""
    
    if not url.lower().startswith('https://'):      # Step 1: Ensure the URL starts with 'https://'
        url = 'https://' + url

    if not url.lower().endswith('/#/index?all'):     # Step 2: Ensure the URL ends with '.html'
        url = url + '/#/index?all'

    try:                                            # Step 3: Validate the URL
        result = urlparse(url)
        if (result.scheme and result.netloc):
            return url, True                        # Return the corrected URL and True if valid
        else:
            return False
        
    except Exception as e:
        return False                                # Return False if the URL is invalid                      

class ProfessorList :
    """Fetch the list of professors from the given URL and regions and return a dataframe."""

    def __init__ (self, url, regions):
        self.url=url
        self.regions=regions
        self.df = pd.DataFrame(columns=['Professor Name', 'Region', 'University Name', 'DBLP Link'])
        
    def getProfList(self):
        
        self.url, flag = is_valid_url(self.url)
        if (not flag):
            print("Invalid URL")
            return None
        
        try:
            
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")                           # Optional: run in headless mode (no UI)
            options.add_argument("--disable-javascript")                 # Disable JavaScript to prevent auto redirection
            prefs = {
                "profile.default_content_setting_values.geolocation": 2  # Block geolocation
            }
            options.add_experimental_option("prefs", prefs)
            options.add_argument("--disable-geolocation")                # Disable geolocation

            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            
            for region in self.regions:
                link=self.url +"&" + region_code(region)
                print(link)
                try:
                    driver.delete_all_cookies()
                    driver.get(link)

                    # Wait for dynamic content to load (adjust the wait time or condition based on the page)
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                    WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, "centerscreen")))

                    option_text = region
                    time.sleep(2)
                    page_content = driver.page_source
                    soup = BeautifulSoup(page_content, 'html.parser')

                    print(f"Dropdown option: {option_text}")  # Print out the option text (optional)
                    for a_tag in soup.find_all("a", href=True):
                        parent_td = a_tag.find_parent("td")
                        if parent_td and parent_td.get("align") == "right":
                            continue  # Skip this <a> tag

                        if ("title" in a_tag.attrs and "Click for author's home page." in a_tag["title"] and a_tag.get_text(strip=True)):
                            author_name = a_tag.get_text(strip=True)

                            # Traverse upward to find the university name
                            university_name = "Unknown University"  # Default value
                            parent_tr = a_tag.find_parent("tr")
                            parent_tr = parent_tr.find_parent("tr")
                            parent_tr=parent_tr.find_previous_sibling().find_previous_sibling()
                            if parent_tr:
                                # print(f"DEBUG: Found parent tr: {parent_tr}")  # Debugging
                                university_span = parent_tr.find("span", onclick=True, class_=lambda x: x != "hovertip" if x else True)
                                if university_span:
                                    # print(f"DEBUG: Found span: {university_span}")  # Debugging
                                    if "toggleFaculty" in university_span.get("onclick", ""):
                                        university_name = university_span.get_text(strip=True)
                        

                        if ("title" in a_tag.attrs and "Click for author's DBLP entry." in a_tag["title"]):
                            link_url = a_tag["href"]
                            if link_url.startswith("/"):
                                link_url = urlparse(self.url)._replace(path=link_url).geturl()
                            
                            new_row = pd.DataFrame([{'Professor Name': author_name, 'Region': option_text, 'University Name': university_name, 'DBLP Link': link_url}])
                            self.df = pd.concat([self.df, new_row], ignore_index=True)
                                
                except Exception as e:
                    print(f"Error interacting with dropdown: {str(e)}")

            driver.quit()

            return self.df

        except Exception as e:
            print(f"Error: {str(e)}")
            return None
