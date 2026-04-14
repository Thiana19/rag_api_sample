# config.example.py — Copy this file to config.py and fill in your values.
# config.py is gitignored and never committed.

SITE_NAME = "My Company"
ASSISTANT_DESCRIPTION = "a helpful assistant that answers questions based on the website content"

BASE_URL = "https://example.com/"

# Add all known pages here to guarantee they are scraped
SEED_URLS = [
    "https://example.com/",
    "https://example.com/about",
    "https://example.com/services",
    "https://example.com/contact",
]

# Storage
SCRAPED_OUTPUT = "scraped_content.json"
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "site_content"

# Embeddings & LLM
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OLLAMA_MODEL = "llama3.2"

# Chunking
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Retrieval
N_RESULTS = 4
