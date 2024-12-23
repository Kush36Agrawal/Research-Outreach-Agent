import time
from get_prof_list import ProfessorList
from get_abstract import ResearchAbstract
from get_researches_of_prof import ProfResearches
import logging
import pandas as pd
from playwright.sync_api import sync_playwright
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EmailCreater:
    def __init__(self, url, regions):
        self.url = url
        self.regions = regions

    def get_data(self):
        data, df = self._get_prof_list()
        newText=""
        lines=data.splitlines()
        for line in lines:
            line=line.strip()
            if line.startswith("[Link:"):
                start_index=line.find("http")
                end_index=line.find("]",start_index)
                prof_url=line[start_index:end_index]
                newText= newText + self._get_prof_researches(prof_url)
            else :
                newText+="\n"
                newText+=line
        x=newText.splitlines()
        y=x[:10]
        newText="\n".join(y)

        researches = []
        lines=newText.splitlines()
        counter=1
        for line in lines:
            newText2=""
            line=line.strip()
            if line.startswith("https://"):
                research_url=line
                newText2+="\n"
                newText2+=f"Abstract for Research Paper {counter}"
                newText2+="\n"
                newText2+="\n"
                newText2+=self._get_research_abstract(research_url)
                newText2+="\n"
                counter+=1
            else :
                counter=1
                newText2+=line
                newText2+="\n"
            logging.info(newText2)
            researches.append(newText2)

        return researches, df

    def _get_prof_list(self):
        prof_list = ProfessorList(self.url, self.regions)
        return prof_list.getProfList()
    
    def _get_prof_researches(self, prof_url):
        prof_researches = ProfResearches(prof_url)
        return prof_researches.getProfResearches()
    
    def _get_research_abstract(self, research_url):
        research_abstract = ResearchAbstract(research_url)
        return research_abstract.getResearchAbstract()
    

class EmailFinder:
    def __init__(self, tables):
        self.tables = tables
        self.df = pd.DataFrame(columns=['Professor Name', 'University Name', 'Email Address'])

    def get_emails(self):
        tables = self.tables

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
                for table in tables:
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