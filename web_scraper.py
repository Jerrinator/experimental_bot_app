## modBot Project
## web_scraper.py

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
from datetime import datetime
import json
from urllib.parse import urlparse, unquote
import time
from config import get_config
import os
# from database_handler import DatabaseHandler, Document
# from document_writer import DocumentWriter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv, dotenv_values, set_key
import re
import PyPDF2
import io


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
import warnings
import logging

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Set up logging
#logging.basicConfig(level=logging.CRITICAL)
#logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO)
logging.disable(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#########################################################################################



class WebScraper:
    def __init__(self, chat_service, database_handler=None, document_writer=None):
        # self.db_handler = database_handler
        """Initialize the web scraper with configuration."""
        self.config = get_config()
        self.chat_service = chat_service  # Add this line to store the ChatService instance
        # self.document_writer = document_writer  # Initialize DocumentWriter instance

    async def read_pdf_content_from_url(self, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                pdf_content = await response.read()
                reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
              
                # Combine text from PDF pages
                text = ''.join(page.extract_text() for page in reader.pages if page.extract_text())

                # Extract the title from the first line of the text
                title_lines = text.splitlines()  # Split content into lines
                title = title_lines[0].strip() if title_lines else "Untitled"  # Get the first line as title

                return title, text  # Return the title and the extracted text as a tuple
                
                #return ''.join(page.extract_text() for page in reader.pages if page.extract_text())

    async def fetch_page_content(self, url: str) -> Dict[str, str]:
        logger.debug("\nArrived in fetch_page_content")
        url = url
        """
        Asynchronously fetch webpage content and metadata using traditional parsing
        """
        try:
            # Check if the URL is a PDF
            if url.lower().endswith('.pdf'):
                title, pdf_content = await self.read_pdf_content_from_url(url)
                #print(f"\n\nPDF Content from URL: {pdf_content}")
                # Call DocumentWriter to summarize and write the PDF content
                # await self.document_writer.summarize_and_write(title, pdf_content)  # Use an appropriate title here

                return pdf_content  # Return the text as well

            # Handle local file URLs
            elif url.startswith('file://'):
                file_path = unquote(url[7:])  # Remove 'file://' and decode URL encoding
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        html = f.read()
                    return await self._parse_content(html, url)
                else:
                    logger.error(f"Local file not found: {file_path}")
                    return None

            # Handle HTTP(S) URLs
            else:
                headers = {
                    'User-Agent': self.config.user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive'
                }

                async with aiohttp.ClientSession(headers=headers) as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            html = await response.text()
                            # Parse the content
                            parsed_data = await self._parse_content(html, url)

                            def sanitize_title(title: str) -> str:
                                # Replace non-alphanumeric characters with an empty string
                                return re.sub(r'[^a-zA-Z0-9 ]', '', title)

                            sanitized_title = sanitize_title(parsed_data['title'])
                            print(f"Sanitized title: {sanitized_title}")
                            prompt = (
                                f"You are a content processing assistant. Please format the following web data in this exact structure:\n\n"
                                f"1. START with a concise content index (single-spaced, no extra lines)\n"
                                f"2. FOLLOW with the complete cleaned content\n\n"
                                f"IMPORTANT AUTHOR EXTRACTION: If the Author field shows 'None', extract the author from the title or content. Look for patterns like 'by [Author Name]', 'written by [Author Name]', or author names in the title.\n\n"
                                f"Source data from '{url}':\n"
                                f"Title: {sanitized_title}\n"
                                f"Author: {parsed_data['author']}\n"
                                f"Publication Date: {parsed_data['publication_date']}\n"
                                f"Raw Content: {parsed_data['content']}\n\n"
                                f"FORMAT YOUR RESPONSE EXACTLY AS:\n"
                                f"**Content Index:**\n"
                                f"- Title: [actual title - cleaned]\n"
                                f"- Author: [actual author name - extract from title/content if not provided above]\n"
                                f"- Date: [actual date if available]\n"
                                f"- Main Topics: [2-3 key topics from content]\n"
                                f"- Key Points: [2-3 essential points]\n"
                                f"---\n"
                                f"**Cleaned Content:**\n"
                                f"[Complete article/content with proper formatting, paragraphs, and all original substance preserved but cleaned of HTML artifacts, navigation elements, and irrelevant text]"
                            )

                            # Generate response from the LLM
                            ai_response = await asyncio.to_thread(self.chat_service.chat_model, prompt)
                            cleaned_content = ai_response.content
                            print(url)
                            # await self.document_writer.summarize_and_write(parsed_data['title'], cleaned_content)
                            return cleaned_content
                        else:
                            logger.error(f"Error fetching {url}: Status {response.status}")
                            return None

        except Exception as e:
            logger.error(f"Error in fetch_page_content: {str(e)}")
            return None

    async def _parse_content(self, html: str, url: str) -> Dict[str, str]:
        logger.debug("\nArrived in _parse_content")        
        """
        Parse HTML content using BeautifulSoup
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            logger.debug(f"\nSoup extracted with BeautifulSoup {soup}")
            
            # Remove unwanted elements
            logger.debug("\nRemoving unwanted elements from soup")
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'iframe']):
                element.decompose()
            logger.debug("\nUnwanted elements removed from soup")

            # Extract title
            logger.debug("\nExtracting title")
            title = ''
            if soup.title:
                title = soup.title.string
            elif soup.find('h1'):
                title = soup.find('h1').get_text(strip=True)
            logger.debug(f"\nTitle extracted {title}")
                
            
            # Extract main content
            logger.debug("\nExtracting main content")
            main_content = ''
            # Try common content containers
            content_containers = [
                soup.find('main'),
                soup.find('article'),
                soup.find(class_='content'),
                soup.find(id='content'),
                soup.find(class_='post-content'),
                soup.find(class_='entry-content')
            ]
            
            for container in content_containers:
                if container:
                    main_content = container.get_text(separator=' ', strip=True)
                    break
            logger.debug(f"\nMain content extracted {main_content}")
            
            # If no content found in common containers, get body text
            logger.debug("\nIf no main content, getting body text")
            if not main_content and soup.body:
                main_content = soup.body.get_text(separator=' ', strip=True)
                logger.debug(f"\nNo main content found, main content extracted from body text {main_content}")

            # Extract author
            logger.debug("\nExtracting author")
            author = None
            author_elements = [
                soup.find(class_='author'),
                soup.find(rel='author'),
                soup.find(class_='byline'),
                soup.find(class_='post-author')
            ]
            for element in author_elements:
                if element:
                    author = element.get_text(strip=True)
                    break
            logger.debug("\nAuthor extracted: [author}")

            # Extract publication date
            logger.debug("\nExtracting publication date")
            
            logger.debug("\nExtracting publication date")
            pub_date = None
            date_elements = [
                soup.find('time'),
                soup.find(class_='date'),
                soup.find(class_='published'),
                soup.find(class_='post-date')
            ]
            for element in date_elements:
                if element:
                    # Try to get datetime attribute first
                    pub_date = element.get('datetime', element.get_text(strip=True))
                    break
            logger.debug("\nPublication date extracted: [pub_date}")

            # Create summary (first 500 characters of main content)
            logger.debug("\nCreating summary of main_content")
            summary = main_content[:500] + '...' if len(main_content) > 500 else main_content
            logger.debug("\nSummary of main_content created")
            
            logger.debug("\nReturning web scraping")
            return {
                'url': url,
                'domain': urlparse(url).netloc or os.path.dirname(url),
                'content': main_content,
                'title': title,
                'author': author,
                'publication_date': pub_date,
                'summary': summary,
                'date_scraped': datetime.utcnow().isoformat(),
                'type': 'document'
            }

        except Exception as e:
            logger.error(f"Error parsing content: {str(e)}")
            return {
                'url': url,
                'domain': urlparse(url).netloc or os.path.dirname(url),
                'content': '',
                'title': '',
                'author': None,
                'publication_date': None,
                'summary': '',
                'date_scraped': datetime.utcnow().isoformat(),
                'type': 'document'
            }


    async def scrape_multiple_urls(
        self,
        urls: List[str],
        delay: float = 1.0
    ) -> List[Dict[str, str]]:
        """
        Scrape multiple URLs with rate limiting
        
        Args:
            urls: List of URLs to scrape
            delay: Delay between requests in seconds
        """
        results = []
        
        for url in urls:
            # Add delay between requests for HTTP URLs only
            if results and not url.startswith('file://'):
                await asyncio.sleep(delay)
                
            result = await self.fetch_page_content(url)
            if result:
                results.append(result)
        
        return results
