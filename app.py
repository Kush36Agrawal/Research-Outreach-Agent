import logging
import pandas as pd
import chainlit as cl
from PyPDF2 import PdfReader
from helper import EmailCreater, EmailFinder
from weather import get_current_weather
from random_joke import get_random_joke
from langchain_ollama import ChatOllama
from langchain.schema import SystemMessage
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define tools (functions) that can be called by the AI model
tools = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                },
            },
            "required": ["location"],
        },
    },
    {
        "name": "get_random_joke",
        "description": "Get a random joke",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_conversational_response",
        "description": "Respond conversationally if no other tools should be called for a given query.",
        "parameters": {
            "type": "object",
            "properties": {
                "response": {
                    "type": "string",
                    "description": "Conversational response to the user.",
                },
            },
            "required": ["response"],
        },
    },
    {
        "name": "get_prof_list",
        "description": "Get the data of professors in a given location and field",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "The Country, e.g. USA, Singapore, China, etc.",
                },
                "website": {
                    "type": "string",
                    "description": "The website where data is present, e.g. https://www.stanford.edu",
                },
            },
            "required": ["location", "website"],
        },
    },
]

# Initialize the AI model
model1 = ChatOllama(model="llama3.2:3b", format="json", temperature=0.3, num_ctx=8192)
model2 = ChatOllama(model="llama3.2:3b", temperature=0.6, num_ctx=8192)
model3 = ChatOllama(model="llama3.2:3b", temperature=0.4, num_ctx=2048)
model1 = model1.bind_tools(tools=tools)

# Create the prompt template for the AI model
prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="You are a helpful AI assistant. Use the provided tools when necessary else respond with your own knowledge. Also don't tell answer for illegal queries"),
    HumanMessagePromptTemplate.from_template("{input}"),
])

# Function to extract skills from resume
def extract_skills(resume: str) -> str:
    prompt = ChatPromptTemplate.from_template(f"""You are an AI assistant tasked with extracting the skills from a resume. The resume may contain various sections such as personal information, education, work experience, and technical skills. Focus on identifying and listing the skills mentioned in the resume. Please extract the skills and list them clearly. If the skills are organized in a section, make sure to list them from that section. If the skills are mentioned throughout the document, collect them all and present them as a comprehensive list.
    Resume Text:
    {resume}
    Extracted Skills:""")
    formatted_prompt = prompt.format_messages(resume=resume)
    result = model2.invoke(formatted_prompt)
    logging.info(result)
    return result.content

# Function to create summarized abstract
def create_abstract(research: str) -> str:
    prompt = ChatPromptTemplate.from_template(f"You are an AI assistant tasked with creating an Abstract of the following research by summarizing the relevant information about research:\n{research}")
    formatted_prompt = prompt.format_messages(research=research)
    result = model2.invoke(formatted_prompt)
    logging.info(result)
    return result.content

# Function to generate email
def generate_email(summarized_researches: str, skills: str) -> str:
    # Prompt for general use
    # prompt = ChatPromptTemplate.from_template(f"""Below is a professor's research abstract and a summary of my skills froskills. Please generate a polite and professional email body introducing me to the professor. In the email, mention the specific area of research the professor is involved in, and highlight the skills I have that are relevant to their work. Express my interest in discussing potential opportunities for collaboration or research.
    # Prompt for personal use
    prompt = ChatPromptTemplate.from_template(f"""You are Devyansh Gupta, a B.Tech student at IIT Roorkee in Data Science and AI branch. Below is a professor's research abstract your task is to generate a polite and professional email body introducing yourself to the professor. In the email, mention the specific areas of research the professor is involved in and discuss them properly, and highlight the skills you have that are relevant to their work. Express your interest for collaboration or research with the professor. Make sure not to boast your skills too much.
    Professor's Research Abstract:
    {summarized_researches}
    Your Skills:
    {skills}
    Generate a personalized email to the professor:""")
    formatted_prompt = prompt.format_messages(summarized_researches=summarized_researches, skills=skills)
    result = model3.invoke(formatted_prompt)
    logging.info(result)
    return result.content

# Function to process user queries
def process_query(query: str, resume: str = None) -> str:
    """
    Processes user queries by invoking the AI model and calling appropriate functions.
    """
    logging.info(f"Processing query: {query}")
    formatted_prompt = prompt.format_messages(input=query)
    logging.info(f"Formatted prompt: {formatted_prompt}")
    result = model1.invoke(formatted_prompt)
    logging.info(result)
    
    if result.tool_calls:
        for tool_call in result.tool_calls:
            function_name = tool_call['name']
            args = tool_call['args']
            logging.info(f"Function call: {function_name}, Args: {args}")

            if function_name == "get_current_weather":
                return get_current_weather(**args)
            elif function_name == "get_random_joke":
                return get_random_joke()
            elif function_name == "get_conversational_response":
                return args['response']
            elif function_name == "get_prof_list" and resume:
                
                skills = extract_skills(resume)
                df1 = EmailCreater(args['website'], args['location']).get_data()

                df2 = EmailFinder(df1).get_emails()
                df1 = pd.merge(df1, df2, on=['Professor Name', 'University Name'], how='outer')

                list_of_summary_of_researches = []
                for _, row in df1.iterrows():
                    all_researches = [row['Research 1'], row['Research 2'], row['Research 3']]
                    summarized_researches = ""
                    for research in all_researches:
                        summarized_researches += create_abstract(research) + "\n"

                    list_of_summary_of_researches.append(summarized_researches)
                
                research_df = pd.DataFrame(list_of_summary_of_researches, columns=['Research Summary'])
                df3 = pd.concat([df1, research_df], axis=1)

                list_of_emails = []
                for _, row in df3.iterrows():
                    email = generate_email(row['Research Summary'], skills) 
                    list_of_emails.append(email)
                
                email_df = pd.DataFrame(list_of_emails, columns=['Email Body'])
                final_df = pd.concat([df3, email_df], axis=1)
                
                final_df.to_csv('final_df.csv', index=False)

                return list_of_emails[0]

    return result.content

# Chainlit event handler for chat start
@cl.on_chat_start
async def start():
    """
    Initializes the chat session.
    """
    logging.info("Chat started")
    cl.user_session.set("model", model1)

    # Ask the user to upload a file
    files = await cl.AskFileMessage(
        content="Please upload the Resume to begin!",
        accept=["application/pdf"],
        max_size_mb=20,
        timeout=10,  # Consider increasing the timeout if needed
    ).send()

    if files is None or len(files) == 0:
        # Handle the case where no file is uploaded or timeout occurs
        await cl.Message(content="No file was uploaded or the upload timed out. Please try again.").send()
        return

    # Process the uploaded file
    resume = files[0]
    pdf_text = ""
    msg = cl.Message(content=f"Processing `{resume.name}`...")
    await msg.send()

    try:
        # Extract text from the PDF file
        with open(resume.path, "rb") as file:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                pdf_text += page.extract_text()

        # Send the extracted text as a message
        if pdf_text.strip():
            msg = cl.Message(content=f"Extracted text from `{resume.name}`:\n{pdf_text}")
        else:
            msg = cl.Message(content=f"Could not extract text from `{resume.name}`. It may be a scanned image or empty.")
        await msg.send()

        # Store the resume in the session
        cl.user_session.set("resume", pdf_text)

    except Exception as e:
        error_message = f"Error processing `{resume.name}`: {str(e)}"
        logging.error(error_message)
        await cl.Message(content=error_message).send()

# Chainlit event handler for incoming messages
@cl.on_message
async def main(message: cl.Message):
    """
    Handles incoming user messages, processes them, and sends responses.

    Args:
    message (cl.Message): The incoming user message
    """
    logging.info(f"Received message: {message.content}")

    if message.content:
        resume = cl.user_session.get('resume')
        query = message.content
        if resume:
            response = await cl.make_async(process_query)(query, resume)
            logging.info(f"Generated Response: {response}")
            await cl.Message(content=response).send()
        else:
            # This should ideally never happen if resume was uploaded correctly
            await cl.Message(content="Something went wrong while processing the resume. Please try again.").send()
