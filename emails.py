import os
import sys
import ast
import logging
import asyncio
import pandas as pd
import chainlit as cl
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from streaming_output import generate_email_streaming

model = ChatOllama(model="llama3.2:3b", temperature=0.5, num_ctx=2048)

# Function to Normalize the input Locations
def normalize_location_param(topic) -> list:
    """
    Ensures that the 'topic' parameter is always a list of strings.
    If the model mistakenly returns a string, it converts it into a valid list.
    """

    if topic is None:
        return []
    
    if isinstance(topic, list):
        return topic  # Already a valid list
    
    if isinstance(topic, str):
        try:
            # Case 1: If it's a string representation of a list, safely evaluate it
            parsed_topic = ast.literal_eval(topic)
            if isinstance(parsed_topic, list):
                return [t.strip() for t in parsed_topic if isinstance(t, str)]
        except (SyntaxError, ValueError):
            pass  # Not a list representation, move to next check
        
        # Case 2: If it's a comma-separated string, split it
        return [t.strip() for t in topic.split(",") if t.strip()]

    return []


# Function to extract skills from resume
def extract_skills(resume: str) -> str:
    prompt = ChatPromptTemplate.from_template(f"""You are an AI assistant that reads resumes and extracts the candidate's key technical and domain-specific skills. From the following resume, extract the most relevant and noteworthy skills and summarize them clearly in a single paragraph. Do not include soft skills or personal traits. Focus only on technical tools, programming languages, libraries, frameworks, relevant technologies and work experiences (if any). Return only a clean paragraph summarizing the skills.
    Resume Text:
    {resume}
    Extracted Skills:""")
    formatted_prompt = prompt.format_messages(resume=resume)
    result = model.invoke(formatted_prompt)
    logging.info(result)
    return result.content


# Function to generate email
def create_prompt(prof_name: str, summarized_researches: str, skills: str) -> str:
    # Prompt for general use
    # prompt = ChatPromptTemplate.from_template(f"""Below is a professor's research abstract and a summary of my skills froskills. Please generate a polite and professional email body introducing me to the professor. In the email, mention the specific area of research the professor is involved in, and highlight the skills I have that are relevant to their work. Express my interest in discussing potential opportunities for collaboration or research.

    # Prompt for personal use
    prompt = ChatPromptTemplate.from_template(f"""You are Devyansh Gupta, a B.Tech student at IIT Roorkee in Data Science and AI branch. Below is a professor's research abstract. Your task is to generate a polite and professional email body introducing yourself to the professor. If the professor’s name is provided, make sure to address them by name in the email. Discuss the specific areas of research the professor is involved in, referring to the abstract. Briefly highlight your own skills and background that are relevant to their work — without boasting or using spam-like language. Express a genuine interest in collaborating with or conducting research under their guidance.
    Professor's Research Abstract:
    {summarized_researches}
    Your Skills:
    {skills}
    Generate a personalized email to the Professor {prof_name}:""")
    formatted_prompt = prompt.format_messages(summarized_researches=summarized_researches, skills=skills)
    return formatted_prompt


async def get_list_of_emails(args, resume: str, locally: bool = True) -> list:
    """
    Get the list of emails by processing professor data and generate emails with streaming output.
    
    Arguments:
    - args: Dictionary containing the website and location.
    - resume: User's resume for extracting skills.
    - locally: Boolean indicating whether to use local llm or copilot for email generation.
    
    Returns:
    - list_of_emails: A list of email bodies.
    """

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))     # Add the current directory to the system path to import local modules
    if locally:
        from helper_local import ProfDataCreater, EmailAndAbstractFinder
    else:
        from helper_auto import ProfDataCreater, EmailAndAbstractFinder
    
    skills = extract_skills(resume)

    locations = normalize_location_param(args['location'])

    df1 = await ProfDataCreater(args['website'], locations, skills).get_data()
    df1.to_csv('prof_research_data.csv', index=False)

    df2 = await EmailAndAbstractFinder(df1, resume).get_emails_and_abstracts()
    df2.to_csv('prof_research_and_email.csv', index=False)

    list_of_emails = []

    for i, (_, row) in enumerate(df2.iterrows()):
        article_progress_msg = cl.Message(content=f"⏳ Processing to Write Email for: **{row['Professor Name']}**")
        await article_progress_msg.send()
        
        await asyncio.sleep(0.1)
    
        formatted_prompt = create_prompt(row['Professor Name'], row['Research Summary'], skills)
        
        email_content, article_msg = await generate_email_streaming(formatted_prompt, row['Professor Name'])
        
        if email_content:
            article_msg.content = f"**Email: **\n\n{email_content}"
            await article_msg.update()
        
            list_of_emails.append(email_content)
            
        else:
            article_progress_msg.content = f"❌ Failed to generate email for professor {row['Professor Name']}"
            await article_progress_msg.update()
        
        await asyncio.sleep(0.5)
    
    email_df = pd.DataFrame(list_of_emails, columns=['Email Body'])
    final_df = pd.concat([df2, email_df], axis=1)
    final_df.to_csv('final_emails_data.csv', index=False)
