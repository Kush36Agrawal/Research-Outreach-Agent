import time
import random
import asyncio
import pandas as pd
from get_prof_list import ProfessorList
from get_abstract1 import ProfessorResearch
from playwright.async_api import async_playwright

class ProfDataCreater:
    """Creates a DataFrame with the List of Professors and their Researches"""

    def __init__(self, url: str, regions: list):
        self.url = url
        self.regions = regions

    async def get_data(self) -> pd.DataFrame :

        df = await self._get_prof_list(self.url, self.regions)

        researches = []
        # Iterate over each link and add a random delay between 8 to 12 seconds
        for link in df['DBLP Link']:
            researches.append(self._get_prof_research(link))

        # Convert the list of results into a DataFrame
        researches = pd.DataFrame(researches, columns=['Research Summary'])
        final_df = pd.concat([df, researches], axis=1)

        return final_df

    async def _get_prof_list(self, url: str, regions: list) -> pd.DataFrame:
        prof_list = ProfessorList(url, regions)
        return await prof_list.getProfList()
    
    def _get_prof_research(self, prof_url: str) -> list:
        prof_researches = ProfessorResearch(prof_url)
        return prof_researches.getProfResearch()


# Start Playwright
class EmailAndAbstractFinder:
    """Finds the Emails of Professors and Abstracts of their Researches and then Genreates a Personalised Email using Copilot."""

    def __init__(self, df1: pd.DataFrame):
        self.df1 = df1
        
        temp_df = df1[['Professor Name', 'University Name']].copy()
        temp_df = temp_df.rename(columns={'Professor Name': 'prof_name', 'University Name': 'university_name'})
        self.tables = temp_df.to_dict(orient='records')           # Convert the DataFrame into a list of dictionaries

        self.df = pd.DataFrame(columns=['Professor Name', 'University Name', 'Email Address'])

    async def get_emails_and_abstracts(self) -> pd.DataFrame :

        async with async_playwright() as p:

            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            # Open the webpage
            await page.goto('https://copilot.microsoft.com/')
            
            try:
                await asyncio.sleep(50)
                copilot_button = page.locator('//*[@id="userInput"]')
                await copilot_button.click()

            except Exception as e:
                print(f"Error while clicking the Copilot button: {e}")
                await browser.close()  # Ensure the browser is closed even if there is an error
                raise

            # Loop through the list of tables and send messages
            await asyncio.sleep(2) 

            for table in self.tables:
                prof_name = table["prof_name"]
                university_name = table["university_name"]
                
                try:
                    input_field = page.locator('//textarea[@placeholder="Message Copilot"]')
                    await input_field.fill(f"Find email address of Professor {prof_name} in {university_name} University. "
                                           f"In an email address format username@domainname.extension. Output just the email address and nothing else.")
                    await asyncio.sleep(2) 
                    await input_field.press('Enter')
                except Exception as e:
                    print(f"Error while filling the input field for {prof_name}: {e}")
                    continue  # Continue with the next table

                await asyncio.sleep(3)

                try:
                    output_locator = page.locator('//*[@id="app"]/main/div[2]/div/div/div[2]/div/div[2]')
                    await output_locator.wait_for(state='visible')  # Wait until the output is visible

                    # Extract and clean up the Copilot output
                    copilot_output = await output_locator.text_content()
                    copilot_output = copilot_output[12:]  # Remove unwanted text at the beginning
                    print(copilot_output)

                    new_row = pd.DataFrame([{'Professor Name': prof_name, 'University Name': university_name, 'Email Address': copilot_output}])
                    self.df = pd.concat([self.df, new_row], ignore_index=True)

                except Exception as e:
                    print(f"Error while extracting output for {prof_name}: {e}")

                await asyncio.sleep(2)  # Wait before processing the next request

            await browser.close()

            return self.df