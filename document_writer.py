## Project_Libby
# document_writer.py

import os
from pathlib import Path
from typing import Union, Dict
from docx import Document
from fpdf import FPDF
import PyPDF2
import logging
import requests
from dotenv import load_dotenv, dotenv_values
import asyncio
from chat_service import ChatService
from database_handler import DatabaseHandler
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from datetime import datetime
import re
import aiohttp
import io
from urllib.parse import unquote



#########################################################################################

### LOAD VARIABLES
load_dotenv()
env_vars = dotenv_values(".env")  # Load existing environment variables into a dictionary
# Set .env variables
api_key = os.getenv("OPENAI_API_KEY")
chat_model = os.getenv("CHAT_MODEL")
vector_model = os.getenv("EMBEDDING_MODEL")
token = os.getenv("ASTRA_DB_TOKEN")
api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
USER_AGENT = os.getenv("USER_AGENT")
keyspace = os.getenv("ASTRA_DB_KEYSPACE")
collection_name = os.getenv("ASTRA_DB_COLLECTION")
recency_collection_name = os.getenv("RECENCY_COLLECTION")
dimension = int(os.getenv("VECTOR_DIMENSION"))
user_name = os.getenv("USERNAME")
chunk_size = os.getenv("CHUNK_SIZE")
chunk_overlap = os.getenv("CHUNK_OVERLAP")


#########################################################################################

### INITIATE DB CLIENT AND EMBEDDINGS CLIENT
# Initialize DatabaseHandler first, but without ChatService yet
db_handler = DatabaseHandler(token, api_endpoint, keyspace, collection_name, recency_collection_name, dimension, chat_service=None)

# Create the collection using the handler
collection = db_handler.collection  # This will create the collection and store it in `collection`

# Initialize ChatService with the database handler 
chat_service = ChatService(database_handler=db_handler)
chat_service2 = ChatService(database_handler=db_handler)

# Now you can pass the chat_service back to the db_handler if needed
db_handler.chat_service = chat_service  # Reference it back if needed



####################################################





# Set up logging
logging.disable(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DocumentWriter:
    """Class to write documents in DOCX and PDF formats."""

    OUTPUT_DIRECTORY = Path("./aiGeneratedDocs")

    def __init__(self):
        """Initialize the DocumentWriter and ensure output directory exists."""
        # Create the output directory if it doesn't exist
        self.OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
        print(f"Files will be written to: {self.OUTPUT_DIRECTORY}")  # Confirmation of the output path

    def _write_docx(self, content: str, filename: str):
        """Write content to a DOCX file."""
        doc = Document()
        doc.add_paragraph(content)
        doc.save(self.OUTPUT_DIRECTORY / filename)

    def _write_pdf(self, content: str, filename: str):
        """Write content to a PDF file."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, content)
        pdf.output(str(self.OUTPUT_DIRECTORY / filename))

    def sanitize_filename(title: str) -> str:
        # Remove invalid characters and replace with an underscore
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)  # Replace invalid filename characters with '_'
        safe_title = re.sub(r'[\s]+', '_', safe_title)  # Replace spaces with underscores
        return safe_title



    async def summarize_and_write(self, title: str, text: str):
        """
        Write the given text summary to DOCX and PDF files.
        
        Args:
            title: Title of the article for naming the files.
            text: Text to summarize
            web_scraper: Instance of WebScraper
        """
        try:
            logger.info("Sending text for summarization.")

            
            # Prepare the prompt with LLM instructions
            prompt_template = ChatPromptTemplate.from_messages([
                SystemMessage(content=(
                    "You work for Liz Ahumada: The reports you produce will be marked with your name, LizBot v1.2, as the producer of the report. You are tasked with comprehensively analyzing the provided text. Be extremely thorough and detailed. Follow these guidelines to ensure accuracy and thoroughness in your reporting:\n"
                    "1. **Careful Reading:** Begin by reading the entire text attentively. Pay close attention to details, including key arguments, data, and any specific terminology used.\n"
                    "2. **Summarization:** After careful reading, provide a concise yet comprehensive summary of the main points, themes, and insights presented in the text. The summary should capture the essence without omitting crucial information.\n"
                    "3. **Citations:** For every claim, fact, or specific detail included in your summary, provide precise citations. Reference the original text with clear indications of where each piece of information was derived, including page numbers or paragraph locations if applicable. Ensure that citations are formatted consistently.\n"
                    "   **Example Citation Format for Books:** “Each year, the population of urban areas grows significantly” (Smith, 2022, p. 15).\n"
                    "   **Example Citation Format for URLs:** “The global energy consumption has increased significantly in recent years” (Renewable Energy Agency, 2023, https://www.renewableenergyagency.org/energy-consumption).\n"
                    "4. **Accuracy Check:** Before finalizing your report, cross-check your summary against the original text to ensure that all information is accurately represented, and that nuances are preserved.\n"
                    "5. **Clarity and Structure:** Present your findings clearly and logically. Use headings or bullet points if necessary to organize information neatly, making it easy for the reader to follow the summarized content and citations.\n"
                    "### Example Application\n"
                    "```markdown\n"
                    "# Main Title(font size=20, color=blue, center justified)\n"
                    "Produced by: LizBot v1.2(font size=12, color=black, left justified)\n"
                    "\n"
                    "## Section Title(font size=16, color=blue, centered)\n"
                    "\n"
                    "### Subsection Title(font size=16, color=blue, centered)\n"
                    "\n"
                    "1. **Key Point One**: Description or detail about the point.(font size=12, color=black)\n"
                    "2. **Key Point Two**: Description or detail about the point.\n"
                    "   - Bullet point for additional detail.\n"
                    "   - Bullet point for further clarification.\n"
                    "3. **Key Point Three**: Continue with remaining Key Points"
                    "\n"
                    "## Conclusion(font size=16, color=blue, centered)\n"
                    "Summarize key insights and findings.\n"
                    "```\n"
                    "Be sure to insert citations whenever presenting information from the subject document:\n"
                    "**Example Citation Format for Books:** “Each year, the population of urban areas grows significantly” (Smith, 2022, p. 15).\n"
                    "**Example Citation Format for URLs:** “The global energy consumption has increased significantly in recent years” (Renewable Energy Agency, 2023, https://www.renewableenergyagency.org/energy-consumption).\n"
                    "Be sure to remove any punctuation that identifies the output as markdown, simply format the output in this markdown format!!\n"
                    "6: **Accuracy Validation Initials**At the end your findings place a spot for initials validating the accuracy of the information contained in the report.(font size=12, color=black, right justified)\n"
                    "Example:\n"
                    "Accuracy Validation Initials_____________________\n"
                    "\n"
                    "Please process the following text thoroughly and begin your report below:\n\n"
                    f"{text}"
                )),
                HumanMessage(content=f"Please analyze the provided text.")
            ])

            # Create an instance of ChatOpenAI for this specific API call
            llm = ChatOpenAI(model=chat_model, api_key=api_key)

            # Generate response from the LLM based on the prompt
            ai_response = await asyncio.to_thread(
                llm, 
                prompt_template.format_messages()
            )

            # Extract the content from ai_response
            if hasattr(ai_response, 'content'):
                summary = ai_response.content
            else:
                summary = str(ai_response)  # Fallback to string conversion if content is not present

            def sanitize_title(title: str) -> str:
                # Replace non-alphanumeric characters with an empty string and spaces with underscores
                return re.sub(r'[^a-zA-Z0-9 ]', '', title).replace(' ', '_')

            # Example usage in the prompt construction
            sanitized_title = sanitize_title(title)
            print(f"Sanitized title: {sanitized_title}")

            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename_base = f"{sanitized_title}_{current_time}"
            print(f"Filename base: {filename_base}")
            
            # Write to DOCX
            self._write_docx(summary, f"{filename_base}.docx")
            logger.info(f"Wrote DOCX file: {filename_base}.docx")
            print(f"Wrote DOCX file to '.\\aiGeneratedDocs': {filename_base}.docx")

            # Write to PDF
            #self._write_pdf(summary, f"{filename_base}.pdf")
            #logger.info(f"Wrote PDF file: {filename_base}.pdf")
            #print(f"Wrote PDF file to .\aiGeneratedDocs: {filename_base}.pdf")

        except Exception as e:
            logger.error(f"Error writing documents: {str(e)}")
            raise