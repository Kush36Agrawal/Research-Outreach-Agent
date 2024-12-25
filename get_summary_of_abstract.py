import time
from playwright.sync_api import sync_playwright

import textwrap

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
class Abstract:
    def __init__(self,abstract):
        self.abstract=abstract
    def get_abstracts(self):
        abstract=self.abstract
        with sync_playwright() as p:
            # Launch browser (use headless=False for a visible browser)
            browser = p.chromium.launch(headless=False)  # Use .launch(headless=False) to view the browser
            page = browser.new_page()
            
            # Open the webpage
            page.goto('https://copilot.microsoft.com/')
            
            # Wait for the page to load and elements to become clickable
            # time.sleep(120  )  # Simulating a delay for page load (although Playwright usually handles this better)

            # Click the Copilot button (you can adjust the selector if needed)
            copilot_button = page.locator('//*[@id="userInput"]')
            copilot_button.click()

            # Wait for the textarea to be visible
            # time.sleep(10)  # Wait for the textarea to be visible

            # Find the input field and send the message
            
            chunks=chunk_text(abstract,10000 )
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
            print(copilot_output)
            

            # Wait for the output to appear
            # time.sleep(10)  # Wait for the output to be visible

            # Extract and print Copilot's output
                # time.sleep(5)  # Wait for the output to be visible

                

            # Close the browser
            # browser.close()






