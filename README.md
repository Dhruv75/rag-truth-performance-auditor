# RAG Truth & Performance Auditor

An end-to-end RAG evaluation platform that measures retrieval quality, answer faithfulness, relevance, hallucinations, and latency.

## Features

* RAG pipeline using Qdrant vector database
* Semantic retrieval with sentence-transformer embeddings
* Answer generation using OpenRouter LLMs
* Trace logging in SQLite
* LLM-as-a-Judge evaluation
* Faithfulness scoring
* Relevance scoring
* Hallucination detection
* Streamlit observability dashboard
* Retrieval and generation latency tracking

## Architecture

User Query
→ Retrieval (Qdrant)
→ Context Generation
→ LLM Response
→ Trace Logging (SQLite)
→ Evaluation (LLM Judge)
→ Dashboard Analytics

## Tech Stack

* Python
* Qdrant
* OpenRouter
* LangChain
* SQLite
* Streamlit
* Plotly
* Sentence Transformers

## Metrics Tracked

* Faithfulness Score
* Relevance Score
* Hallucination Rate
* Retrieval Latency
* Generation Latency
* Token Usage

## Project Structure

```text
auditor/
dashboard/
data/
scripts/
target_rag/

requirements.txt
schema.sql
README.md
```

## Example Evaluation

Question:
What is the travel reimbursement limit?

Context:
Travel reimbursement is limited to ₹5000 per trip.

Answer:
Travel reimbursement is ₹10000 per trip.

Evaluation:

* Faithfulness: 1/5
* Relevance: 4/5
* Hallucination: True

## Future Improvements

* Advanced retrieval metrics
* Multi-document evaluation
* Automated benchmark datasets
* Streamlit Cloud deployment
* Production monitoring integrations
