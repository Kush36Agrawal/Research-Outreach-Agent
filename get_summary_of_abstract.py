import time
from playwright.sync_api import sync_playwright

import textwrap
import pandas as pd
# Function to break text into chunks
def chunk_text(text, max_chunk_size=1000):
    """
    Breaks a long text into chunks of a specified maximum size.
    
    Args:
    - text (str): The input text to be split.
    - max_chunk_size (int): Maximum size of each chunk in characters (default 1000).

    Returns:
    - List of text chunks.
    """
    return textwrap.wrap(text, max_chunk_size)

# Start Playwright
class AbstractAndEmailFinder:
    def __init__(self,df1):
        self.df1 = df1
        
        temp_df = df1[['Professor Name', 'University Name']].copy()
        temp_df = temp_df.rename(columns={'Professor Name': 'prof_name', 'University Name': 'university_name'})
        self.tables = temp_df.to_dict(orient='records')           # Convert the DataFrame into a list of dictionaries

        self.df = pd.DataFrame(columns=['Professor Name', 'University Name', 'Email Address'])
    def get_abstracts_and_email_finder(self):
        df1=self.df1
        with sync_playwright() as p:
            # Launch browser (use headless=False for a visible browser)
            browser = p.chromium.launch(headless=False)  # Use .launch(headless=False) to view the browser
            page = browser.new_page()
            
            # Open the webpage
            page.goto('https://copilot.microsoft.com/')
            
            # Wait for the page to load and elements to become clickable
            # time.sleep(120  )  # Simulating a delay for page load (although Playwright usually handles this better)
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




            # Click the Copilot button (you can adjust the selector if needed)
            copilot_button = page.locator('//*[@id="userInput"]')
            copilot_button.click()

            # Wait for the textarea to be visible
            # time.sleep(10)  # Wait for the textarea to be visible

            # Find the input field and send the message
            list_of_summary_of_researches = []
            for _, row in df1.iterrows():
                all_researches = [row['Research 1'], row['Research 2'], row['Research 3']]
                summarized_researches = ""
                for research in all_researches:
                    chunks=chunk_text(research,10000 )
                    print (len(chunks))
                    input_field = page.locator('//textarea[@placeholder="Message Copilot"]')
                    input_field.fill(f" In the following messages I will provide you with chunks of my New HTML page source code.Please extract the New abstract from it. After all the chunks are completed I will explcity send a message saying all chunks have been given.")
                    time.sleep(5)
                    # button_locator = page.locator('button[aria-label="Submit message"]')  # Locator for the button
                    # button_locator.wait_for(state="enabled")
                    input_field.press('Enter')
                    # output_locator = page.locator('//*[@id="app"]/main/div[2]/div/div/div[2]/div/div[2]')
                    # output_locator.wait_for(state='visible')  # Wait until the output is visible
                    for chunk in chunks:
                        input_field = page.locator('//textarea[@placeholder="Message Copilot"]')
                        # output_locator = page.locator('//*[@id="app"]/main/div[2]/div/div/div[2]/div/div[2]')
                        # output_locator.wait_for(state='visible')  # Wait until the output is visible
                        input_field.fill(f"{chunk}")
                        time.sleep(5)
                        input_field.press('Enter')
                        # time.sleep(1)
                    input_field = page.locator('//textarea[@placeholder="Message Copilot"]')
                    # input_field.wait_for(state='visible')  # Wait until the output is visible
                    # output_locator = page.locator('//*[@id="app"]/main/div[2]/div/div/div[2]/div/div[2]')
                    # output_locator.wait_for(state='visible')  # Wait until the output is visible
                    input_field.fill(" All chunks have been given. Now extract the abstract and provide directly the abstract and nothing like here is the abstract ")
                    time.sleep(5)

                    input_field.press('Enter')

                    output_locator = page.locator('//*[@id="app"]/main/div[2]/div/div/div[2]/div/div[2]')
                    output_locator.wait_for(state='visible')  # Wait until the output is visible
                    time.sleep(50)  # Wait for the output to be visible


                    copilot_output = output_locator.text_content()
                    copilot_output=copilot_output[12:]
                    # print(copilot_output)
                    summarized_researches += copilot_output + "\n"
                list_of_summary_of_researches.append(summarized_researches)

            research_df = pd.DataFrame(list_of_summary_of_researches, columns=['Research Summary'])
            df3 = pd.concat([df1, research_df], axis=1)
            

            # Close the browser after all tasks are complete
            browser.close()
            return self.df, df3



            # Wait for the output to appear
            # time.sleep(10)  # Wait for the output to be visible

            # Extract and print Copilot's output
                # time.sleep(5)  # Wait for the output to be visible

                

            # Close the browser
            # browser.close()






