from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from langchain.schema import Document
import os

class DocumentLoader:
    """Handles loading documents from various sources."""
    
    def __init__(self):
        self.supported_formats = ['.txt', '.md', '.html']

    def load_from_file(self, file_path: str) -> List[Document]:
        """Load document from local file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        return [Document(
            page_content=content,
            metadata={"source": file_path, "type": "file"}
        )]

    def load_from_url(self, url: str) -> List[Document]:
        """Load document from web URL."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines 
                     for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return [Document(
                page_content=text,
                metadata={"source": url, "type": "web"}
            )]
            
        except Exception as e:
            print(f"Error loading URL {url}: {str(e)}")
            return []

    def load_documents(self, sources: List[str]) -> List[Document]:
        """Load multiple documents from various sources."""
        all_documents = []
        
        for source in sources:
            if source.startswith(('http://', 'https://')):
                docs = self.load_from_url(source)
            elif os.path.isfile(source):
                docs = self.load_from_file(source)
            else:
                print(f"Unsupported source: {source}")
                continue
            
            all_documents.extend(docs)
        
        print(f"Loaded {len(all_documents)} documents")
        return all_documents