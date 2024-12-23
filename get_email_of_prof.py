import time
from playwright.sync_api import sync_playwright

class EmailFinder:
    def __init__(self, tables):
        self.tables = tables

    def get_emails(self):
        tables = self.tables

        try:
            with sync_playwright() as p:
                # Launch browser (use headless=False for a visible browser)
                browser = p.chromium.launch(headless=False)  # Use .launch(headless=False) to view the browser
                page = browser.new_page()

                # Open the webpage
                page.goto('https://copilot.microsoft.com/')

                # Find the user input field and click it
                try:
                    copilot_button = page.locator('//*[@id="userInput"]')
                    copilot_button.click()
                except Exception as e:
                    print(f"Error while clicking the Copilot button: {e}")
                    browser.close()
                    raise

                # List of tables containing professor names and universities
                tables = [{"prof_name": "Abhinav Gupta", "university_name": "CMU"},
                        {"prof_name": "Willem Visser", "university_name": "Stellenbosch "}]

                # Loop through the list of tables and send messages
                for table in tables:
                    prof_name = table["prof_name"]
                    university_name = table["university_name"]
                    
                    try:
                        input_field = page.locator('//textarea[@placeholder="Message Copilot"]')
                        input_field.fill(f"Find email address of {prof_name} Prof in {university_name} University. "
                                        f"in an email address format username@domainname.extension. Output just the email address and nothing else.")
                        input_field.press('Enter')
                    except Exception as e:
                        print(f"Error while filling the input field for {prof_name}: {e}")
                        continue  # Continue with the next table

                    # Wait for the output to be visible
                    time.sleep(8)  # Wait for the output to be visible

                    try:
                        output_locator = page.locator('//*[@id="app"]/main/div[2]/div/div/div[2]/div/div[2]')
                        output_locator.wait_for(state='visible')  # Wait until the output is visible
                        time.sleep(2)  # Wait for the output to be visible

                        # Extract and clean up the Copilot output
                        copilot_output = output_locator.text_content()
                        copilot_output = copilot_output[12:]
                        print(copilot_output)

                    except Exception as e:
                        print(f"Error while extracting output for {prof_name}: {e}")

                    time.sleep(2)  # Wait before processing the next request

                # Close the browser after all tasks are complete
                browser.close()

        except Exception as e:
            print(f"An error occurred while running the Playwright script: {e}")