import time
import textwrap
import pandas as pd
from get_prof_list import ProfessorList
from get_abstract import ResearchAbstract
from playwright.sync_api import sync_playwright
from get_researches_of_prof import ProfResearches

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


# Start Playwright
class EmailAndAbstractFinder:
    """Finds the emails and abstracts of Professors using Copilot."""

    def __init__(self, df1):
        self.df1 = df1
        
        temp_df = df1[['Professor Name', 'University Name']].copy()
        temp_df = temp_df.rename(columns={'Professor Name': 'prof_name', 'University Name': 'university_name'})
        self.tables = temp_df.to_dict(orient='records')           # Convert the DataFrame into a list of dictionaries

        self.df = pd.DataFrame(columns=['Professor Name', 'University Name', 'Email Address'])

    def get_emails_and_abstracts(self):

        with sync_playwright() as p:
            # Launch browser (use headless=False for a visible browser)
            browser = p.chromium.launch(headless=False)  # Use .launch(headless=False) to view the browser
            page = browser.new_page()
            
            # Open the webpage
            page.goto('https://copilot.microsoft.com/')
            
            try:
                time.sleep(3)
                copilot_button = page.locator('//*[@id="userInput"]')
                copilot_button.click()
            except Exception as e:
                print(f"Error while clicking the Copilot button: {e}")
                browser.close()
                raise

            # Loop through the list of tables and send messages
            time.sleep(2)

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

                time.sleep(3)               # Wait for the output to be visible

                try:
                    output_locator = page.locator('//*[@id="app"]/main/div[2]/div/div/div[2]/div/div[2]')
                    output_locator.wait_for(state='visible')        # Wait until the output is visible

                    # Extract and clean up the Copilot output
                    copilot_output = output_locator.text_content()
                    copilot_output = copilot_output[12:]
                    print(copilot_output)

                    new_row = pd.DataFrame([{'Professor Name': prof_name, 'University Name': university_name, 'Email Address': copilot_output}])
                    self.df = pd.concat([self.df, new_row], ignore_index=True)

                except Exception as e:
                    print(f"Error while extracting output for {prof_name}: {e}")

                time.sleep(2)  # Wait before processing the next request


            # Click the Copilot button (you can adjust the selector if needed)
            copilot_button = page.locator('//*[@id="userInput"]')
            copilot_button.click()

            # Find the input field and send the message
            input_field = page.locator('//textarea[@placeholder="Message Copilot"]')
            input_field.fill(f"In the following messages I will provide you with chunks of my New HTML page source code. Please extract the New abstract from it. After all the chunks are completed I will explcity send a message saying all chunks have been given.")

            time.sleep(2)
            input_field.press('Enter')
            time.sleep(1)

            list_of_summary_of_researches = []
            for _, row in self.df1.iterrows():
                all_researches = [row['Research 1'], row['Research 2'], row['Research 3']]

                summarized_researches = ""
                for research in all_researches:
                    chunks = self._chunk_text(research, 10000)
                    print (len(chunks))

                    for chunk in chunks:
                        input_field = page.locator('//textarea[@placeholder="Message Copilot"]')
                        input_field.fill(f"{chunk}")
                        time.sleep(3)
                        input_field.press('Enter')

                    input_field = page.locator('//textarea[@placeholder="Message Copilot"]')
                    input_field.fill(" All chunks have been given. Now extract the abstract and provide directly the abstract and nothing like here is the abstract ")
                    time.sleep(3)

                    input_field.press('Enter')

                    output_locator = page.locator('//*[@id="app"]/main/div[2]/div/div/div[2]/div/div[2]')
                    output_locator.wait_for(state='visible')  # Wait until the output is visible

                    copilot_output = output_locator.text_content()
                    copilot_output=copilot_output[12:]
                    # print(copilot_output)
                    summarized_researches += copilot_output + "\n"
                list_of_summary_of_researches.append(summarized_researches)
            
            # Close the browser after all tasks are complete
            browser.close()

            research_df = pd.DataFrame(list_of_summary_of_researches, columns=['Research Summary'])
            df3 = pd.concat([self.df1, research_df], axis=1)
            df3 = pd.merge(df3, self.df, on=['Professor Name', 'University Name'], how='outer')

            return df3
        

    def _chunk_text(self, text, max_chunk_size=1000):
        """
        Breaks a long text into chunks of a specified maximum size.
        
        Args:
        - text (str): The input text to be split.
        - max_chunk_size (int): Maximum size of each chunk in characters (default 1000).

        Returns:
        - List of text chunks.
        """
        return textwrap.wrap(text, max_chunk_size)