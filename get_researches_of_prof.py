import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from playwright.async_api import async_playwright

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
    
    def __init__(self, url):
        self.url = url

    async def getProfResearches(self):
        if not is_valid_url(self.url):
            print("Error: Invalid URL")
            return None
        print(self.url)

        try:
            # Initialize Playwright and open the browser
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                page = await browser.new_page()

                # Navigate to the URL
                await page.goto(self.url)

                # Get the page content after the page loads
                page_content = await page.content()
                soup = BeautifulSoup(page_content, 'html.parser')

                research_links = []
                counter = 0

                # Look for <nav> tags with class 'publ' and collect research links
                for nav in soup.find_all('nav', class_='publ'):
                    if counter >= 3:  # Stop after collecting 3 links
                        break
                    counter += 1

                    # Find the first <li> under this <nav>
                    first_li = nav.select_one('ul li')

                    # Find the <a> tag within the first <li>
                    first_a_tag = first_li.find('a') if first_li else None

                    # Get the href attribute (the URL)
                    if first_a_tag:
                        first_url = first_a_tag.get('href')
                        research_links.append(first_url)

                # Close the browser
                await browser.close()

            return research_links

        except Exception as e:
            print(f"Error: {str(e)}")
            return None

# # Example usage:
# async def main():
#     prof_researches = ProfResearches("https://dblp.org/pid/24/5051.html")
#     research_links = await prof_researches.getProfResearches()
#     print(research_links)

# # Run the async function
# asyncio.run(main())
