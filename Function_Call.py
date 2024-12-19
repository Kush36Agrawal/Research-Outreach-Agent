import requests
import logging
import chainlit as cl
from helper import Email_Creater
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
model = ChatOllama(model="llama3.2:3b", format="json", temperature=0.3, num_ctx=8192)
model = model.bind_tools(tools=tools)

# Create the prompt template for the AI model
prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="You are a helpful AI assistant. Use the provided tools when necessary else respond with your own knowledge. Also don't tell answer for illegal queries"),
    HumanMessagePromptTemplate.from_template("{input}"),
])

# Function to process user queries
def process_query(query: str) -> str:
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
            elif function_name == "get_random_joke":
                return get_random_joke()
            elif function_name == "get_conversational_response":
                return args['response']
            elif function_name == "get_prof_list":
                all_researches = Email_Creater(args['website'], args['location']).get_data()
                return "\n".join(all_researches)

    return result.content

# Chainlit event handler for chat start
@cl.on_chat_start
async def start():
    """
    Initializes the chat session.
    """
    logging.info("Chat started")
    cl.user_session.set("model", model)

# Chainlit event handler for incoming messages
@cl.on_message
async def main(message: cl.Message):
    """
    Handles incoming user messages, processes them, and sends responses.

    Args:
    message (cl.Message): The incoming user message
    """
    logging.info(f"Received message: {message.content}")
    try:
        response = await cl.make_async(process_query)(message.content)
        logging.info(f"Response: {response}")
        await cl.Message(content=response).send()
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logging.error(f"Error: {error_message}")
        await cl.Message(content=error_message).send()
