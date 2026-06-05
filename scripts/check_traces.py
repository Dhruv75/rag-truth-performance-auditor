import sqlite3

conn = sqlite3.connect("auditor.db")

count = conn.execute(
    """
    SELECT COUNT(*)
    FROM rag_traces
    """
).fetchone()[0]

print("RAG Traces:", count)

conn.close()