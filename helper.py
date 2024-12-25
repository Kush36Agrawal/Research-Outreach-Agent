import time
import logging
import pandas as pd
from get_prof_list import ProfessorList
from get_abstract import ResearchAbstract
from playwright.sync_api import sync_playwright
from get_researches_of_prof import ProfResearches
from get_summary_of_abstract import AbstractAndEmailFinder
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EmailCreater:
    """Creates a DataFrame with the list of Professors and their Research Abstracts."""

    def __init__(self, url, regions):
        self.url = url
        self.regions = regions

    def get_data(self):
        df = self._get_prof_list()

        research_links_df = df['DBLP Link'].apply(self._get_prof_researches).apply(pd.Series)   # Apply _get_prof_researches for vectorized processing
        research_links_df.columns = [f"Link {i+1}" for i in range(len(research_links_df.columns))]

        df = pd.concat([df, research_links_df], axis=1)                                         # Concatenate research links DataFrame with the original DataFrame

        processed_links_df = df[['Link 1', 'Link 2', 'Link 3']].map(self._process_link)         # Apply _process_link for vectorized processing
        processed_links_df.columns = ['Research 1', 'Research 2', 'Research 3']

        final_df = pd.concat([df, processed_links_df], axis=1)

        return final_df

    def _get_prof_list(self):
        prof_list = ProfessorList(self.url, self.regions)
        return prof_list.getProfList()
    
    def _get_prof_researches(self, prof_url):
        prof_researches = ProfResearches(prof_url)
        return prof_researches.getProfResearches()
    
    def _get_research_abstract(self, research_url):
        research_abstract = ResearchAbstract(research_url)
        return research_abstract.getResearchAbstract()
    
    def _process_link(self, link):
        return self._get_research_abstract(link)

class EmailFinder:
    """Creates a DataFrame with the list of Professors and their Emails."""

    def __init__(self, df1):
        self.df1 = df1
        
        temp_df = df1[['Professor Name', 'University Name']].copy()
        temp_df = temp_df.rename(columns={'Professor Name': 'prof_name', 'University Name': 'university_name'})
        self.tables = temp_df.to_dict(orient='records')           # Convert the DataFrame into a list of dictionaries

        self.df = pd.DataFrame(columns=['Professor Name', 'University Name', 'Email Address'])

    def get_emails(self):

        try:
            with sync_playwright() as p:
                # Launch browser (use headless=False for a visible browser)
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()

                # Open the webpage
                page.goto('https://copilot.microsoft.com/')

                # Find the user input field and click it
                try:
                    time.sleep(2)
                    copilot_button = page.locator('//*[@id="userInput"]')
                    copilot_button.click()
                except Exception as e:
                    print(f"Error while clicking the Copilot button: {e}")
                    browser.close()
                    raise

                # Loop through the list of tables and send messages
                time.sleep(1)
                for table in self.tables:
                    prof_name = table["prof_name"]
                    university_name = table["university_name"]
                    
                    try:
                        input_field = page.locator('//textarea[@placeholder="Message Copilot"]')
                        input_field.fill(f"Find email address of Professor {prof_name} in {university_name} University. "
                                        f"in an email address format username@domainname.extension. Output just the email address and nothing else.")
                        time.sleep(1)
                        input_field.press('Enter')
                    except Exception as e:
                        print(f"Error while filling the input field for {prof_name}: {e}")
                        continue                # Continue with the next table

                    time.sleep(5)               # Wait for the output to be visible

                    try:
                        output_locator = page.locator('//*[@id="app"]/main/div[2]/div/div/div[2]/div/div[2]')
                        output_locator.wait_for(state='visible')        # Wait until the output is visible
                        time.sleep(2)                                   # Wait for the output to be visible

                        # Extract and clean up the Copilot output
                        copilot_output = output_locator.text_content()
                        copilot_output = copilot_output[12:]
                        print(copilot_output)

                        new_row = pd.DataFrame([{'Professor Name': prof_name, 'University Name': university_name, 'Email Address': copilot_output}])
                        self.df = pd.concat([self.df, new_row], ignore_index=True)

                    except Exception as e:
                        print(f"Error while extracting output for {prof_name}: {e}")

                    time.sleep(2)  # Wait before processing the next request

                # Close the browser after all tasks are complete
                browser.close()

        except Exception as e:
            print(f"An error occurred while running the Playwright script: {e}")

        return self.df