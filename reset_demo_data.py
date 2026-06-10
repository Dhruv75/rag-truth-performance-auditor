import sqlite3

conn = sqlite3.connect("auditor.db")

conn.execute("DELETE FROM audit_results")
conn.execute("DELETE FROM rag_traces")

conn.commit()
conn.close()

print("Database cleared successfully.")