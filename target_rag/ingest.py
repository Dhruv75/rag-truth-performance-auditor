import os
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

if not all([QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME]):
    raise ValueError("Missing environment variables")

print("Loading handbook...")

with open("data/company_handbook.txt", "r", encoding="utf-8") as f:
    handbook = f.read()

print(f"Document size: {len(handbook)} characters")
print(handbook[-500:])

splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50
)

chunks = splitter.split_text(handbook)

documents = [
    Document(page_content=chunk)
    for chunk in chunks
]

print(f"Created {len(documents)} chunks")

print("Loading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Uploading to Qdrant...")

QdrantVectorStore.from_documents(
    documents=documents,
    embedding=embeddings,
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    collection_name=COLLECTION_NAME,
)

print("Upload complete!")
print(f"Collection: {COLLECTION_NAME}")
print(f"Chunks uploaded: {len(documents)}")