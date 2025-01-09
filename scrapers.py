import requests
from lxml import html, etree
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def scrape_dl_acm(response):
    """Scrape abstract from dl.acm.org."""
    soup = BeautifulSoup(response.content, 'html.parser')
    title_tag = soup.find('h1', property='name')
    title = title_tag.text.strip() if title_tag else 'Title not found'

    abstract_section = soup.find('section', id='abstract')
    abstract = 'Abstract not found'
    if abstract_section:
        paragraphs = abstract_section.find_all('div', role='paragraph')
        abstract = "\n".join([para.text.strip() for para in paragraphs])

    return title, abstract

def scrape_sciencedirect(response):
    """Scrape abstract from sciencedirect.com."""
    soup = BeautifulSoup(response.content, 'html.parser')
    title_tag = soup.find('h1')
    title = title_tag.text.strip() if title_tag else 'Title not found'

    abstract_section = soup.find('div', class_='abstract author')
    abstract = abstract_section.text.strip() if abstract_section else 'Abstract not found'

    return title, abstract

def scrape_arxiv(response):
    """Scrape abstract from arxiv.org."""
    soup = BeautifulSoup(response.content, 'html.parser')
    title_tag = soup.find('h1', class_='title')
    title = title_tag.text.strip() if title_tag else 'Title not found'

    abstract_section = soup.find('blockquote', class_='abstract mathjax')
    abstract = abstract_section.text.strip().replace("Abstract:", "").strip() if abstract_section else 'Abstract not found'

    return title, abstract

def scrape_springer(response):
    """Scrape abstract from link.springer.com."""
    soup = BeautifulSoup(response.content, 'html.parser')
    title_tag = soup.find('h1', class_='c-article-title')
    title = title_tag.text.strip() if title_tag else 'Title not found'

    abstract_section = soup.find('div', class_='c-article-section', id='Abs1-section')
    abstract = abstract_section.text.strip() if abstract_section else 'Abstract not found'

    return title, abstract

def scrape_aclanthology(response):
    """Scrape abstract from aclanthology.org."""
    soup = BeautifulSoup(response.content, 'html.parser')
    title_tag = soup.find('h2', class_='card-title')
    title = title_tag.text.strip() if title_tag else 'Title not found'

    abstract_section = soup.find('div', class_='card-body acl-abstract')
    abstract = abstract_section.text.strip() if abstract_section else 'Abstract not found'

    return title, abstract

def scrape_ieeexplore(response):
    """Scrape abstract from ieeexplore.ieee.org."""
    tree = html.fromstring(response.content)
    abstract_raw = tree.xpath('//meta[@property="og:description"]/@content')    # Extract the abstract using XPath

    if abstract_raw:
        raw_html = abstract_raw[0]
        raw_tree = html.fragment_fromstring(raw_html, create_parent='div')
        clean_text = etree.tostring(raw_tree, method='text', encoding='unicode')
    
    return "", clean_text


# Dictionary to map domain names to specific scraper functions
SCRAPERS = {
    'dl.acm.org': scrape_dl_acm,
    'sciencedirect.com': scrape_sciencedirect,
    'arxiv.org': scrape_arxiv,
    'link.springer.com': scrape_springer,
    'aclanthology.org': scrape_aclanthology,
    'ieeexplore.ieee.org': scrape_ieeexplore
}

def get_paper_details(paper_url):
    """Extracts the title and abstract of a given paper from multiple websites."""
    try:
        # Follow redirection to get the final URL
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(paper_url, allow_redirects=True, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve paper: {paper_url}")
            return None, None

        # Parse the final domain
        final_url = response.url
        domain = urlparse(final_url).netloc

        # Select the appropriate scraper based on the domain
        scraper = SCRAPERS.get(domain)
        if scraper:
            return scraper(response)
        else:
            print(f"No scraper available for domain: {domain}")
            return 'Title not found', 'Abstract not found'

    except Exception as e:
        print(f"An error occurred while processing the URL: {paper_url}")
        print(f"An error occurred: {e}")
        return None, None
