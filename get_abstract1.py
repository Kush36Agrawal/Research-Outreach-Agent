import asyncio
import random
from scrapers import get_paper_details
from playwright.async_api import async_playwright

class ProfessorResearch:
    def __init__(self, url: str):
        self.url = url
        self.base_url = "https://scholar.google.com"

    async def scrape_gsc(self, hyperlink, page):
        delay = random.uniform(8, 12)
        print(f"Sleeping for {delay:.2f} seconds...")
        await asyncio.sleep(delay)

        await page.goto(hyperlink)
        await page.wait_for_selector("#gs_bdy", timeout=10000)

        ids_to_traverse = [
            "gs_bdy_ccl",
            "gsc_vcpb",
            "gsc_oci_title_wrapper",
            "gsc_oci_title",
        ]

        current = await page.query_selector("#gs_bdy")
        for div_id in ids_to_traverse:
            if current:
                current = await current.query_selector(f"div#{div_id}")
            else:
                return None

        if current:
            anchor = await current.query_selector("a")
            if anchor:
                href = await anchor.get_attribute("href")
                return href
        return None

    async def getProfResearch(self):
        abstracts = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(self.url, timeout=60000)
            await page.wait_for_selector("tbody#gsc_a_b")

            # Get all research paper links
            a_tags = await page.query_selector_all("tbody#gsc_a_b tr.gsc_a_tr td.gsc_a_t a")
            links = []
            for a in a_tags[:10]:
                href = await a.get_attribute("href")
                if href:
                    links.append(self.base_url + href)

            # For each paper, get the external URL and extract abstract
            for link in links:
                if len(abstracts) >= 3:
                    break
                target_url = await self.scrape_gsc(link, page)
                if target_url:
                    _, abstract = get_paper_details(target_url)
                    if abstract != "Abstract not found":
                        abstracts.append(f"{len(abstracts) + 1}.) {abstract}")

            await browser.close()

        return "\n".join(abstracts) if abstracts else "No abstracts found."
