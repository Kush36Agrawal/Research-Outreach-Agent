import asyncio
import random
import numpy as np
from scrapers import get_paper_details
from langchain_ollama import OllamaEmbeddings
from playwright.async_api import async_playwright

embed_model = OllamaEmbeddings(model='all-minilm:33m', num_ctx=512)

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculates the cosine similarity between two texts using embeddings."""
    embed1 = embed_model.embed_query(text1)
    embed2 = embed_model.embed_query(text2)
    vec1 = np.array(embed1)
    vec2 = np.array(embed2)

    # Calculate cosine similarity
    cosine_similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    print(f"Cosine Similarity: {cosine_similarity:.4f}")
    return cosine_similarity

class ProfessorResearch:
    def __init__(self, url: str, skills: str):
        self.url = url
        self.base_url = "https://scholar.google.com"
        self.skills = skills

    async def scrape_gsc(self, hyperlink, page):
        try:
            delay = random.uniform(8, 12)
            print(f"Sleeping for {delay:.2f} seconds...")
            await asyncio.sleep(delay)

            try:
                await page.goto(hyperlink, timeout=15000)
                await page.wait_for_selector("#gs_bdy", timeout=10000)
            except Exception as e:
                print(f"[scrape_gsc] Navigation or selector error: {e}")
                return None

            ids_to_traverse = [
                "gs_bdy_ccl",
                "gsc_vcpb",
                "gsc_oci_title_wrapper",
                "gsc_oci_title",
            ]

            try:
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
            except Exception as e:
                print(f"[scrape_gsc] Error while traversing DOM: {e}")
                return None

        except Exception as e:
            print(f"[scrape_gsc] Unexpected error: {e}")

        return None


    async def getProfResearch(self):
        abstracts = []
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                try:
                    await page.goto(self.url, timeout=60000)
                    await page.wait_for_selector("tbody#gsc_a_b")

                    # Get all research paper links
                    a_tags = await page.query_selector_all("tbody#gsc_a_b tr.gsc_a_tr td.gsc_a_t a")
                    links = []
                    for a in a_tags[:10]:
                        try:
                            href = await a.get_attribute("href")
                            if href:
                                links.append(self.base_url + href)
                        except Exception as e:
                            print(f"Error extracting href: {e}")

                    # For each paper, get the external URL and extract abstract then compare similarity
                    for link in links:
                        if len(abstracts) >= 3:
                            break
                        try:
                            target_url = await self.scrape_gsc(link, page)
                            if target_url:
                                _, abstract = get_paper_details(target_url)
                                if abstract != "Abstract not found":
                                    similarity = calculate_similarity(abstract, self.skills)
                                    if similarity > 0.07:
                                        abstracts.append(f"{len(abstracts) + 1}.) {abstract}")
                        except Exception as e:
                            print(f"Error processing link {link}: {e}")
                            continue

                except Exception as e:
                    print(f"Error navigating the page: {e}")
                finally:
                    await browser.close()
        except Exception as e:
            print(f"Error initializing playwright: {e}")

        return "\n".join(abstracts) if abstracts else "No abstracts found."

