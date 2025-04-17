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
model = ChatOllama(model="llama3.2:3b", format="json", temperature=0.3, num_ctx=8192)
model = model.bind_tools(tools=tools)

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
    result = model.invoke(formatted_prompt)
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
            elif function_name == "get_list_of_emails":
                return "Please upload your Resume first to write Personalized Emails."

    return result.content

# Chainlit event handler for chat start
@cl.on_chat_start
async def start():
    """
    Initializes the chat session.
    """
    logging.info("Chat started")
    cl.user_session.set("model", model)
    
    # Welcome message with instructions
    await cl.Message(
        content="""Welcome! I am your AI Assitant to help you in writing Personalized Emails to Professors of Various Countries.
        If you want to write a personalized email, please upload your Resume."""
    ).send()

# Chainlit event handler for incoming messages
@cl.on_message
async def main(message: cl.Message):
    """
    Handles incoming user messages, processes them, and sends responses.

    Args:
    message (cl.Message): The incoming user message
    """
    logging.info(f"Received message: {message.content}")

    # Handle regular messages
    if message.content and not message.elements:
        resume = cl.user_session.get('resume')
        query = message.content
        
        if resume:
            response = process_query(query, resume)
        else:
            response = process_query(query)

        logging.info(f"Generated Response: {response}")
        await cl.Message(content=response).send()

    elif message.elements and message.elements[0].type == "file":

        resume = message.elements[0]
        if resume.mime != "application/pdf":
            await cl.Message(content="File type not Supported, Please upload Resume as a PDF file.").send()
            return
        # Process the uploaded file
        pdf_text = ""
        msg = cl.Message(content=f"Processing `{resume.name}`...")
        await msg.send()

        try:
            # Extract text from the PDF file
            with open(resume.path, "rb") as file:
                pdf_reader = PdfReader(file)
                for page in pdf_reader.pages:
                    pdf_text += page.extract_text()

            # Store the resume in the session
            cl.user_session.set("resume", pdf_text)
            
            await cl.Message(content=f"Successfully processed `{resume.name}`. You can now write emails using this resume.").send()

        except Exception as e:
            error_message = f"Error processing `{resume.name}`: {str(e)}"
            logging.error(error_message)
            await cl.Message(content=error_message).send()
