## modBot Project
## document_loader.py

import os
from typing import List, Dict, Optional, Union
from pathlib import Path
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredMarkdownLoader
)

#########################################################################################


# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Set up logging
#logging.basicConfig(level=logging.CRITICAL)
#logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO)
logging.disable(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#########################################################################################

class DocumentLoader:
    """Enhanced document loader with support for multiple file types and chunking strategies."""
    
    SUPPORTED_EXTENSIONS = {
        '.txt': TextLoader,
        '.md': UnstructuredMarkdownLoader,
    }

    def __init__(
        self,
        chunk_size: int = 1460,
        chunk_overlap: int = 200,
        length_function: callable = len,
    ):
        """
        Initialize the DocumentLoader with customizable chunking parameters.
        
        Args:
            chunk_size (int): The size of text chunks
            chunk_overlap (int): The amount of overlap between chunks
            length_function (callable): Function to measure text length
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=length_function,
        )
        
    def _get_loader_class(self, file_path: Union[str, Path]) -> Optional[type]:
        """Get the appropriate loader class for a file type."""
        ext = os.path.splitext(str(file_path))[1].lower()
        return self.SUPPORTED_EXTENSIONS.get(ext)

    def _is_supported_file(self, file_path: Union[str, Path]) -> bool:
        """Check if the file type is supported."""
        return self._get_loader_class(file_path) is not None

    async def load_single_document(self, file_path: Union[str, Path]) -> List[str]:
        """
        Load and process a single document.
        
        Args:
            file_path: Path to the document
            
        Returns:
            List of text chunks from the document
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            loader_class = self._get_loader_class(file_path)
            if not loader_class:
                raise ValueError(f"Unsupported file type: {file_path.suffix}")

            logger.info(f"Loading document: {file_path}")
            loader = loader_class(str(file_path))
            docs = loader.load()
            
            # Split documents into chunks
            splits = self.text_splitter.split_documents(docs)
            
            # Extract text content from splits
            chunks = [doc.page_content for doc in splits]
            
            logger.info(f"Successfully processed {file_path} into {len(chunks)} chunks")
            return chunks

        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            raise

    async def load_documents(
        self,
        file_paths: List[Union[str, Path]],
        ignore_errors: bool = False
    ) -> Dict[str, List[str]]:
        """
        Load multiple documents and return their chunks.
        
        Args:
            file_paths: List of paths to documents
            ignore_errors: If True, continue processing even if some files fail
            
        Returns:
            Dictionary mapping file paths to their chunks
        """
        results = {}
        
        for file_path in file_paths:
            try:
                chunks = await self.load_single_document(file_path)
                results[str(file_path)] = chunks
            except Exception as e:
                if ignore_errors:
                    logger.warning(f"Skipping {file_path} due to error: {str(e)}")
                    continue
                raise

        return results

    def get_supported_formats(self) -> List[str]:
        """Get a list of supported file extensions."""
        return list(self.SUPPORTED_EXTENSIONS.keys())

    @staticmethod
    def get_directory_documents(
        directory: Union[str, Path],
        recursive: bool = True
    ) -> List[Path]:
        """
        Get all supported documents in a directory.
        
        Args:
            directory: Directory to scan
            recursive: If True, scan subdirectories as well
            
        Returns:
            List of paths to supported documents
        """
        directory = Path(directory)
        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")

        pattern = "**/*" if recursive else "*"
        all_files = directory.glob(pattern)
        
        return [
            f for f in all_files
            if f.is_file() and f.suffix.lower() in DocumentLoader.SUPPORTED_EXTENSIONS
        ]
