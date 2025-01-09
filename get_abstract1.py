import time
import random
import requests
from bs4 import BeautifulSoup
from scrapers import get_paper_details

headers = {
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

class ProfessorResearch:
    """Fetch the webpage content, extract readable text, and capture all redirecting elements within the text."""
    
    def __init__(self, url: str):
        self.url = url

    def scrape_gsc(self, hyperlink):
        
        delay = random.uniform(8, 12)  # Adjust the range as needed
        print(f"Sleeping for {delay:.2f} seconds...")
        time.sleep(delay)
        response = requests.get(hyperlink, headers=headers)

        soup = BeautifulSoup(response.text, "html.parser")
        current_div = soup.find("div", {"id": "gs_bdy"})

        # List of IDs to traverse in order
        ids_to_traverse = [
            "gs_bdy_ccl",
            "gsc_vcpb",
            "gsc_oci_title_wrapper",
            "gsc_oci_title",
        ]

        # Traverse the nested divs
        for div_id in ids_to_traverse:
            if current_div:
                current_div = current_div.find("div", {"id": div_id})
            else:
                print(f"Div with id='{div_id}' not found.")
                break

        # Check for the anchor tag at the end
        if current_div:
            anchor_tag = current_div.find("a")
            if anchor_tag and anchor_tag.get("href"):
                return anchor_tag["href"]  # Print the href attribute

        return None


    def getProfResearch(self):
        """
        Extracts the first 10 research URLs from the given Google Scholar page URL,
        fetches the hyperlink from the title text of each, and calls `scrape()` with the hyperlink.
        """

        # Step 1: Fetch the Google Scholar page
        response = requests.get(self.url, headers=headers)

        soup = BeautifulSoup(response.text, "html.parser")
        
        tbody = soup.find("tbody", {"id": "gsc_a_b"})           # Access the tbody with id="gsc_a_b"
        tr_tags = tbody.find_all("tr", {"class": "gsc_a_tr"})   # Access all <tr> tags within the tbody

        base_url = "https://scholar.google.com/"
        links = []
        for tr in tr_tags:
            a_tag = tr.find("a")  # Find the <a> tag inside the <tr>
            if a_tag and a_tag.get("href"):  # Ensure <a> tag and href exist
                links.append(base_url + a_tag["href"])
        links = links[:10]

        abstracts = []
        # Print the extracted links
        for link in links:
            if (len(abstracts) >= 3):
                break
            url =  self.scrape_gsc(link)
            _, abstract = get_paper_details(url)
            if (abstract == 'Abstract not found'): continue
            else: abstracts.append(f"{len(abstracts) + 1}.) {abstract}")

        if (len(abstracts) == 0):
            return "No abstracts found."
        
        abstracts = "\n".join(abstracts)
        return abstracts
