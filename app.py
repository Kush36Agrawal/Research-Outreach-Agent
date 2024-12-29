import asyncio
import logging
import chainlit as cl
from PyPDF2 import PdfReader
from tools_config import tools
from emails import get_list_of_emails
from weather import get_current_weather
from langchain_ollama import ChatOllama
from langchain.schema import SystemMessage
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the AI model
model1 = ChatOllama(model="llama3.2:3b", format="json", temperature=0.3, num_ctx=8192)
model1 = model1.bind_tools(tools=tools)

# Create the prompt template for the AI model
prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="You are a helpful AI assistant. Use the provided tools when necessary else respond with your own knowledge. Also don't tell answer for illegal queries"),
    HumanMessagePromptTemplate.from_template("{input}"),
])

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
            elif function_name == "get_conversational_response":
                return args['response']
            elif function_name == "get_list_of_emails" and resume:
                list_of_emails = asyncio.run(get_list_of_emails(args, resume))
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
            response = process_query(query, resume)
            logging.info(f"Generated Response: {response}")
            await cl.Message(content=response).send()
        else:
            # This should ideally never happen if resume was uploaded correctly
            await cl.Message(content="Something went wrong while processing the resume. Please try again.").send()
