import os
import time
import uuid
import sqlite3

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from langchain_community.embeddings import HuggingFaceEmbeddings
from openai import OpenAI

# ==========================
# Load Environment Variables
# ==========================

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ==========================
# OpenRouter Client
# ==========================

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# ==========================
# Embedding Model
# ==========================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ==========================
# Qdrant Client
# ==========================

qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

# ==========================
# Main RAG Function
# ==========================

def ask_rag(question: str):

    # --------------------------
    # Retrieval
    # --------------------------

    retrieval_start = time.time()

    query_vector = embeddings.embed_query(question)

    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=3
    ).points

    retrieval_latency = int(
        (time.time() - retrieval_start) * 1000
    )

    print(f"Retrieved {len(results)} chunks")

    context = "\n\n".join(
        hit.payload["page_content"]
        for hit in results
    )

    # --------------------------
    # Generation
    # --------------------------

    generation_start = time.time()

    prompt = f"""
You are an HR assistant.

Answer ONLY using the provided context.

If the answer is not present in the context, reply:

I do not know.

Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b:free",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response.choices[0].message.content

    generation_latency = int(
        (time.time() - generation_start) * 1000
    )

    total_tokens = response.usage.total_tokens

    # --------------------------
    # Save Trace to SQLite
    # --------------------------

    trace_id = str(uuid.uuid4())

    conn = sqlite3.connect("auditor.db")

    conn.execute(
        """
        INSERT INTO rag_traces
        (
            id,
            user_query,
            retrieved_context,
            llm_answer,
            retrieval_latency_ms,
            generation_latency_ms,
            total_tokens
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            trace_id,
            question,
            context,
            answer,
            retrieval_latency,
            generation_latency,
            total_tokens
        )
    )

    conn.commit()
    conn.close()

    return {
        "answer": answer,
        "retrieval_latency": retrieval_latency,
        "generation_latency": generation_latency,
        "tokens": total_tokens
    }


# ==========================
# CLI Interface
# ==========================

if __name__ == "__main__":

    print("\nRAG Auditor Ready!")
    print("Type your question below.\n")

    while True:

        question = input("Ask: ")

        if question.lower() in ["exit", "quit"]:
            break

        result = ask_rag(question)

        print("\nAnswer:")
        print(result["answer"])

        print("\nMetrics:")
        print(
            f"Retrieval Latency: {result['retrieval_latency']} ms"
        )
        print(
            f"Generation Latency: {result['generation_latency']} ms"
        )
        print(
            f"Tokens Used: {result['tokens']}"
        )

        print("\n" + "=" * 60 + "\n")