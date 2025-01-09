import logging
import pandas as pd
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
# from helper1 import ProfDataCreater, EmailAndAbstractFinder       # Uncomment to use with Ollama
from helper2 import ProfDataCreater, EmailAndAbstractFinder

model1 = ChatOllama(model="llama3.2:3b", temperature=0.5, num_ctx=2048)
model2 = ChatOllama(model="llama3.2:3b", temperature=0.6, num_ctx=8192)
model3 = ChatOllama(model="llama3.2:3b", temperature=0.4, num_ctx=2048)

# Function to extract skills from resume
def extract_skills(resume: str) -> str:
    prompt = ChatPromptTemplate.from_template(f"""You are an AI assistant tasked with extracting the skills from a resume. The resume may contain various sections such as personal information, education, work experience, and technical skills. Focus on identifying and listing the skills mentioned in the resume. Please extract the skills and list them clearly. If the skills are organized in a section, make sure to list them from that section. If the skills are mentioned throughout the document, collect them all and present them as a comprehensive list.
    Resume Text:
    {resume}
    Extracted Skills:""")
    formatted_prompt = prompt.format_messages(resume=resume)
    result = model1.invoke(formatted_prompt)
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
    prompt = ChatPromptTemplate.from_template(f"""You are Devyansh Gupta, a B.Tech student at IIT Roorkee in Data Science and AI branch. Below is a professor's research abstract your task is to generate a polite and professional email body introducing yourself to the professor. In the email, mention the specific areas of research the professor is involved in and discuss them properly, and highlight the skills you have that are relevant to their work. Express your interest for collaboration or research with the professor. Make sure not to boast your skills too much and don't use spam words.
    Professor's Research Abstract:
    {summarized_researches}
    Your Skills:
    {skills}
    Generate a personalized email to the professor:""")
    formatted_prompt = prompt.format_messages(summarized_researches=summarized_researches, skills=skills)
    result = model3.invoke(formatted_prompt)
    logging.info(result)
    return result.content

async def get_list_of_emails(args, resume: str) -> list:
    """
    Get the list of emails by processing professor data and generating emails.
    
    Arguments:
    - args: Dictionary containing the website and location.
    - resume: User's resume for extracting skills.
    
    Returns:
    - list_of_emails: A list of email bodies.
    """

    # Uncomment these lines to extract skills from resume using Ollama
    skills = extract_skills(resume)
    df1 = await ProfDataCreater(args['website'], args['location']).get_data()
    df1.to_csv('prof_data.csv')
    df2 = await EmailAndAbstractFinder(df1).get_emails_and_abstracts()
    list_of_emails = []
    for _, row in df2.iterrows():
        email = generate_email(row['Research Summary'], skills)
        list_of_emails.append(email)
    
    email_df = pd.DataFrame(list_of_emails, columns=['Email Body'])
    final_df = pd.concat([df2, email_df], axis=1)
    final_df.to_csv('final_df.csv', index=False)
    
    return list_of_emails

    # df1 = await ProfDataCreater(args['website'], args['location']).get_data()
    # df1.to_csv('prof_data.csv')
    # df2 = await EmailAndAbstractFinder(df1, resume).get_emails_and_abstracts()

    # df2.to_csv('final_df.csv')
    # return [df2['Email Body'][0]]
