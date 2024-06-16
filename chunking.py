from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialize the language model
import os

# from dotenv import load_dotenv
# load_dotenv()
# import openai
# # Set up OpenAI API key
# openai.api_key = os.getenv("OPENAI_API_KEY")

from dotenv import load_dotenv

load_dotenv()


llm = ChatOpenAI(model_name="gpt-4")
# from script_generation import ini_script

# Define the prompt template
prompt_template = ChatPromptTemplate.from_template(
    """
Given the following script, break it down into meaningful segments suitable for subtitles. Ensure each segment is concise and captures the essence of the content.

Script:
{script}

Output:
"""
)

# Create the chain
chain = prompt_template | llm | StrOutputParser()

# The script to be chunked
# script = ini_script

# Perform semantic chunking
# result = chain.invoke({"script": script})
# print(result)
