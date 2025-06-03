# Research OutReach Agent

Research OutReach Agent is an AI-powered academic outreach automation tool. It helps users discover professors in their field, analyze their research, and generate personalized emails for academic collaboration or research opportunities. The system leverages web scraping, language models, and browser automation to streamline the process of connecting with academics worldwide.

---

https://github.com/user-attachments/assets/ee167581-6780-43fa-9945-5d518e07755c

## Features

- **Automated Professor Discovery:**  
  Scrapes academic ranking sites (e.g., CSRankings) to find professors by country, region, or university.

- **Research Extraction:**  
  Uses browser automation and web scraping to extract research paper titles, abstracts, and links from Google Scholar, DBLP, and other sources.

- **Intelligent Abstract Filtering:**  
  Compares research abstracts to your skills/interests using local language models and semantic similarity.

- **Personalized Email Generation:**  
  Generates tailored emails to professors using your resume and the professor's research profile.

- **Bulk Email Sending:**  
  Sends personalized emails to multiple professors and saves results in CSV files.

---

## Tech Stack

- **Python 3.10+**
- [Playwright](https://playwright.dev/python/) (browser automation)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) (HTML parsing)
- [Langchain](https://python.langchain.com/) + [Ollama](https://ollama.com/) (Local LLMs and embeddings)
- [Chainlit](https://www.chainlit.io/) (chat interface)
- [SMTP](https://docs.python.org/3/library/smtplib.html) (email sending)

---

## Project Structure

```
.
├── app.py                    # Main Chainlit app and entry point
├── emails.py                 # Email generation logic using LLMs
├── get_abstract1.py          # Google Scholar research extraction (Playwright)
├── get_abstract2.py          # Alternative research extraction
├── get_prof_list.py          # Professor list scraping from ranking sites
├── get_researches_of_prof.py # Extracts research links from professor profiles
├── helper_auto.py            # Automated pipeline for data gathering and email generation
├── helper_local.py           # Local pipeline for data gathering and email generation
├── scrapers.py               # Web scrapers for academic paper sites
├── smtp_setup.py             # Email sending via SMTP
├── streaming_output.py       # (If present) Streaming output utilities
├── test.py                   # Test and utility functions
├── tools_config.py           # Tool definitions for AI assistant
├── weather.py                # Weather info retrieval
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
└── ...                       # Data files, CSVs, and other resources
```

---

## How to Use

1. **Clone the Repository**
   ```powershell
   git clone https://github.com/Kush36Agrawal/Research-Outreach-Agent
   cd "Research Outreach Agent"
   ```

2. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Run the Ollama Backend Server**
   ```powershell
   ollama run llama3.2:3b
   ollama run all-minilm:33m
   ollama serve
   ```

4. **Run the Application**
   ```powershell
   chainlit run app.py
   ```

4. **Upload Your Resume**
   - When prompted in the Chainlit interface, upload your resume (PDF or text).

5. **Start the Email Generation Process**
   - Use a query like:
     ```
     write emails to professor of {countries} from website www.csrankings.org
     ```
   - The system will scrape professors, analyze their research, and generate personalized emails.

6. **View Saved Results**
   - Wait for the process to complete. The final CSV file with emails and details will be automatically saved in the project folder.

---

## Configuration

- **Email Sending:**  
  Configure your SMTP credentials in `smtp_setup.py` or via environment variables.

- **LLM Model:**  
  The system uses local models via Ollama. Ensure Ollama is installed and running.

---

## Example Query

```
write emails to professor of Germany, France from website www.csrankings.org
```

---
