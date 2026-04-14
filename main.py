"""
main.py — FastAPI RAG API
Run with: python -m uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import chromadb
from chromadb.utils import embedding_functions
import ollama

from config import (
    CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL,
    OLLAMA_MODEL, N_RESULTS, ASSISTANT_DESCRIPTION,
)

app = FastAPI(title="RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_fn,
)


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]


@app.get("/api")
def root():
    return {"status": "ok", "message": "RAG API is running"}


@app.post("/ask", response_model=AnswerResponse)
def ask(request: QuestionRequest):
    question = request.question.strip()

    results = collection.query(
        query_texts=[question],
        n_results=N_RESULTS,
    )

    chunks = results["documents"][0]
    sources = list(set(m["url"] for m in results["metadatas"][0]))
    context = "\n\n".join(chunks)

    prompt = f"""You are {ASSISTANT_DESCRIPTION}.
Answer the user's question using only the information provided below.
If the answer is not in the context, say you don't have that information.

Context:
{context}

Question: {question}

Answer:"""

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response["message"]["content"].strip()
    return AnswerResponse(answer=answer, sources=sources)


# Serve frontend — must be last
app.mount("/", StaticFiles(directory="static", html=True), name="static")
