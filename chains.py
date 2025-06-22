import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')


class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="meta-llama/llama-4-scout-17b-16e-instruct")

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scrapped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )

        chain_extract = prompt_extract | self.llm
        response = chain_extract.invoke({"page_data": cleaned_text})

        try:
            json_parser = JsonOutputParser()
            json_output = json_parser.parse(response.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to extract job postings.")

        return json_output if isinstance(json_output, list) else [json_output]

    def write_email(self, job, links):
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}
            
            ### INSTRUCTION:
            You are Mohan, a business development executive at AtliQ. AtliQ is an AI & Software Consulting company dedicated to facilitating
            the seamless integration of business processes through automated tools. 
            Over our experience, we have empowered numerous enterprises with tailored solutions, fostering scalability, 
            process optimization, cost reduction, and heightened overall efficiency. 
            Your job is to write a cold email to the client regarding the job mentioned above describing the capability of AtliQ 
            in fulfilling their needs.
            Also add the most relevant ones from the following links to showcase Atliq's portfolio: {link_list}
            Remember you are Mohan, BDE at AtliQ. And, your contact details are mohan.singh@atlig.com, +91-8675345678
            Do not provide a preamble.
            ### EMAIL (NO PREAMBLE):
            """
        )

        chain_email = prompt_email | self.llm
        response = chain_email.invoke({"job_description": str(job), "link_list": links})

        return response.content
