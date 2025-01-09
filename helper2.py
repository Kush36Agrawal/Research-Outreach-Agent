import asyncio
import textwrap
import pandas as pd
from get_prof_list import ProfessorList
from get_abstract2 import ProfessorResearch
from playwright.async_api import async_playwright
from get_researches_of_prof import ProfessorResearchesLink

class ProfDataCreater:
    """Creates a DataFrame with the List of Professors and their Researches"""

    def __init__(self, url: str, regions: list):
        self.url = url
        self.regions = regions

    async def get_data(self) -> pd.DataFrame :

        df = await self._get_prof_list()
        research_links_df = []
        for link in df['DBLP Link']:
            result = await self._get_prof_researches_link(link)
            research_links_df.append(result)
            await asyncio.sleep(3)
        research_links_df = pd.DataFrame(research_links_df)
        research_links_df.columns = [f"Link {i+1}" for i in range(len(research_links_df.columns))]

        df = pd.concat([df, research_links_df], axis=1)          # Concatenate research links DataFrame with the original DataFrame

        processed_links_df = await self._process_links_async(df)

        final_df = pd.concat([df, processed_links_df], axis=1)

        return final_df

    async def _get_prof_list(self) -> pd.DataFrame:
        prof_list = ProfessorList(self.url, self.regions)
        return await prof_list.getProfList()
    
    async def _get_prof_researches_link(self, prof_url: str) -> list:
        prof_researches = ProfessorResearchesLink(prof_url)
        return await prof_researches.getProfResearchesLink()
    
    async def _get_prof_research(self, research_url: str) -> str:
        research_abstract = ProfessorResearch(research_url)
        return await research_abstract.getProfResearch()
    
    async def _process_links_async(self, df: pd.DataFrame) -> pd.DataFrame:
        processed_rows = []

        for _, row in df.iterrows():
            # Process all three links for the current row
            results = await asyncio.gather(
                self._process_link(row['Link 1']),
                self._process_link(row['Link 2']),
                self._process_link(row['Link 3'])
            )
            processed_rows.append(results)
            await asyncio.sleep(10) # Wait for 15 seconds before processing each row

        # Create a DataFrame from the processed results
        processed_links_df = pd.DataFrame(processed_rows, columns=['Research 1', 'Research 2', 'Research 3'])
        return processed_links_df
    
    async def _process_link(self, link: str):
        return await self._get_prof_research(link)


# Start Playwright
class EmailAndAbstractFinder:
    """Finds the Emails of Professors and Abstracts of their Researches using Copilot."""

    def __init__(self, df1: pd.DataFrame, resume: str):
        self.df1 = df1
        
        temp_df = df1[['Professor Name', 'University Name']].copy()
        temp_df = temp_df.rename(columns={'Professor Name': 'prof_name', 'University Name': 'university_name'})
        self.tables = temp_df.to_dict(orient='records')           # Convert the DataFrame into a list of dictionaries

        self.df = pd.DataFrame(columns=['Professor Name', 'University Name', 'Email Address'])
        self.resume = resume

    async def get_emails_and_abstracts(self) -> pd.DataFrame :

        async with async_playwright() as p:

            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            # Open the webpage
            await page.goto('https://copilot.microsoft.com/')
            
            try:
                await asyncio.sleep(100)
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
            self.df.to_csv("Emails_Save.csv")

            # Click the Copilot button (you can adjust the selector if needed)
            copilot_button = page.locator('//*[@id="userInput"]')
            await copilot_button.click()

            # Find the input field and send the message
            input_field = page.locator('//textarea[@placeholder="Message Copilot"]')
            await input_field.fill(f"In the following messages I will provide you with chunks of my New HTML page source code. "
                                   f"Please extract the New abstract from it. After all the chunks are completed I will explicitly send a message saying all chunks have been given."
                                   f"Report me summary of the research only after I tell you don't answer it earlier.")

            await asyncio.sleep(2)
            await input_field.press('Enter')
            await asyncio.sleep(2)

            list_of_summary_of_researches = []

            for _, row in self.df1.iterrows():
                all_researches = [row['Research 1'], row['Research 2'], row['Research 3']]

                summarized_researches = ""

                for research in all_researches:
                    chunks = self._chunk_text(research, 10000)
                    print(len(chunks))

                    for chunk in chunks:
                        input_field = page.locator('//textarea[@placeholder="Message Copilot"]')
                        await input_field.fill(f"{chunk}")
                        await asyncio.sleep(6) 
                        await input_field.press('Enter')
                        await asyncio.sleep(4)

                    input_field = page.locator('//textarea[@placeholder="Message Copilot"]')
                    await input_field.fill(f"All chunks have been given." 
                                           f"Now extract the abstract and provide directly the abstract and nothing like here is the abstract")
                    
                    await asyncio.sleep(2)
                    await input_field.press('Enter')
                    await asyncio.sleep(8) 

                    output_locator = page.locator('//*[@id="app"]/main/div[2]/div/div/div[2]/div/div[2]')
                    await output_locator.wait_for(state='visible')  # Wait until the output is visible

                    copilot_output = await output_locator.text_content()
                    copilot_output = copilot_output[12:]  # Clean up the output

                    summarized_researches += copilot_output + "\n"

                list_of_summary_of_researches.append(summarized_researches)

            research_df = pd.DataFrame(list_of_summary_of_researches, columns=['Research Summary'])
            df3 = pd.concat([self.df1, research_df], axis=1)
            df3 = pd.merge(df3, self.df, on=['Professor Name', 'University Name'], how='outer')
            df3.to_csv("Emails_and_Absract_Save.csv", index=False)

            copilot_button = page.locator('//*[@id="userInput"]')
            await copilot_button.click()
            await copilot_button.click()

            # Initial message to start the process
            prompt = (f"""
                    My Resume: 
                    {self.resume}.
                    In the following messages, I will give you Professor's Research Abstract, Professor Name, University Name. For Each professor, generate a personalized email as soon as you receive these three things. Generate a polite and professional email body introducing yourself to the professor. In the email, mention the specific areas of research the professor is involved in and discuss them properly, and highlight the skills you have that are relevant to their work. Express your interest for collaboration or research with the professor. Make sure not to boast your skills too much. Make the email spam-free, do not use spam keywords.""")
            chunks = self._chunk_text(research, 10000)

            print (len(chunks))
            for chunk in chunks:
                input_field = page.locator('//textarea[@placeholder="Message Copilot"]')
                # output_locator = page.locator('//*[@id="app"]/main/div[2]/div/div/div[2]/div/div[2]')
                # output_locator.wait_for(state='visible')  # Wait until the output is visible
                await input_field.fill(f"{chunk}")
                await asyncio.sleep(5)
                await input_field.press('Enter')

            list_of_emails = []

            # Iterate over rows in the DataFrame to generate emails
            for _, row in df3.iterrows():
                summarized_researches = row["Research Summary"]
                professor_name = row["Professor Name"]
                university_name = row["University Name"]
                summarized_researches = row["Research Summary"]
                professor_name = row["Professor Name"]
                university_name = row["University Name"]

                prompt = (f"""
                Professor's Research Abstract:
                {summarized_researches}
                Professor Name:
                {professor_name}
                University Name:
                {university_name}
                Generate a personalized email to the professor. Give me just the Subject, Email body, and nothing else. Do not add ending phrases like 'I hope this helps' or anything of the sort.""")
                await asyncio.sleep(5)

                chunks=self._chunk_text(prompt, 10000)
                print (len(chunks))
                for chunk in chunks:
                    input_field = page.locator('//textarea[@placeholder="Message Copilot"]')
                    await input_field.fill(f"{chunk}")
                    await asyncio.sleep(5)
                    await input_field.press('Enter')
                    await asyncio.sleep(1)

                await asyncio.sleep(5)
                output_locator = page.locator('//*[@id="app"]/main/div[2]/div/div/div[2]/div/div[2]')
                await output_locator.wait_for(state='visible')  # Wait until the output is visible
                copilot_output = await output_locator.text_content()
                copilot_output = copilot_output[12:]
                print(copilot_output)
                list_of_emails.append(copilot_output)

            # Create a DataFrame with the generated emails
            email_df = pd.DataFrame(list_of_emails, columns=['Email Body'])
            final_df = pd.concat([df3, email_df], axis=1)

            # Close the browser
            await browser.close()

            return final_df
        

    def _chunk_text(self, text: str ="", max_chunk_size: int = 1000) -> list:
        """
        Breaks a long text into chunks of a specified maximum size.

        Args:
        - text (str): The input text to be split.
        - max_chunk_size (int): Maximum size of each chunk in characters (default 1000).

        Returns:
        - List of text chunks.
        """
        if text is None:
            text = "" 
        return textwrap.wrap(text, max_chunk_size)
    