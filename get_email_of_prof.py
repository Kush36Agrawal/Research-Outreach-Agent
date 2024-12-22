import time
from playwright.sync_api import sync_playwright

# Start Playwright
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
    tables=[{"prof_name":"Abhinav Gupta","university_name":"CMU"},{"prof_name":"willem visser","university_name":"Stellenbosch "}]
    for table in tables:
        prof_name=table["prof_name"]
        university_name=table["university_name"]
        input_field = page.locator('//textarea[@placeholder="Message Copilot"]')
        input_field.fill(f" Find email address of {prof_name} Prof in {university_name} Univeristy. in an email adress format username@domainname.extension. Output just the email address and nothing else. ")
        input_field.press('Enter')

    # Wait for the output to appear
    # time.sleep(10)  # Wait for the output to be visible

    # Extract and print Copilot's output
        # time.sleep(5)  # Wait for the output to be visible

        output_locator = page.locator('//*[@id="app"]/main/div[2]/div/div/div[2]/div/div[2]')
        output_locator.wait_for(state='visible')  # Wait until the output is visible
        # time.sleep(5)  # Wait for the output to be visible


        copilot_output = output_locator.text_content()
        copilot_output=copilot_output[12:]
        print(copilot_output)

    # Close the browser
    browser.close()
