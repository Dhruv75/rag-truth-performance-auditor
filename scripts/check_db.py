import sqlite3

conn = sqlite3.connect("auditor.db")

rows = conn.execute(
    "SELECT user_query, llm_answer FROM rag_traces"
).fetchall()

print(rows)

conn.close()