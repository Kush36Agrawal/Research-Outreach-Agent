import asyncio
import pandas as pd
from bs4 import BeautifulSoup
from typing import Tuple, Union
from urllib.parse import urlparse
from playwright.async_api import async_playwright

def region_code(region: str) -> str:
    locations = {
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
        "North America": "northamerica",
        "South America": "southamerica",
        "Africa": "africa",
        "Asia": "asia",
        "Australasia": "australasia",
        "Europe": "europe",
        "The World": "world"
    }
    return locations.get(region, "unknown")  # Default to "unknown" if the region is not found

def is_valid_url(url) -> Tuple[Union[str, None], bool]:
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
            return None, False
        
    except Exception as e:
        return None, False                                # Return False if the URL is invalid                      

class ProfessorList:
    """Fetch the list of professors from the given URL and regions and return a dataframe."""
    
    def __init__(self, url: str, regions: list):
        self.url = url
        self.regions = regions
        print(regions)
        self.df = pd.DataFrame(columns=['Professor Name', 'Region', 'University Name', 'DBLP Link'])
        
    async def getProfList(self) -> pd.DataFrame :
        self.url, flag = is_valid_url(self.url)
        if not flag:
            print("Invalid URL")
            return None
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    geolocation=None,               # Deny geolocation (if necessary, but it's optional)
                    permissions=["geolocation"],    # Denying geolocation by using the permissions array format
                )
                page = await context.new_page()
                
                for region in self.regions:
                    link = self.url + "&" + region_code(region)
                    print(link)
                    try:
                        await page.goto(link)

                        # Wait for dynamic content to load (adjust the wait time or condition based on the page)
                        await page.wait_for_selector("body")
                        await asyncio.sleep(2)

                        option_text = region
                        await page.wait_for_timeout(2000)  # Give some time for the content to load
                        await asyncio.sleep(2)
                        page_content = await page.content()
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
                                parent_tr = parent_tr.find_previous_sibling().find_previous_sibling()
                                if parent_tr:
                                    university_span = parent_tr.find("span", onclick=True, class_=lambda x: x != "hovertip" if x else True)
                                    if university_span:
                                        if "toggleFaculty" in university_span.get("onclick", ""):
                                            university_name = university_span.get_text(strip=True)

                            if ("title" in a_tag.attrs and "Click for author's DBLP entry." in a_tag["title"]):
                                link_url = a_tag["href"]
                                if link_url.startswith("/"):
                                    link_url = urlparse(self.url)._replace(path=link_url).geturl()
                                
                                new_row = pd.DataFrame([{'Professor Name': author_name, 'Region': option_text, 'University Name': university_name, 'DBLP Link': link_url}])
                                self.df = pd.concat([self.df, new_row], ignore_index=True)
                    
                    except Exception as e:
                        print(f"Error interacting with region {region}: {str(e)}")
                
                await browser.close()

            return self.df.head(2)
        
        except Exception as e:
            print(f"Error: {str(e)}")
            return None
