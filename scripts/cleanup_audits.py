import sqlite3

conn = sqlite3.connect("auditor.db")

conn.execute("DELETE FROM audit_results")

conn.execute(
    """
    UPDATE rag_traces
    SET is_audited = 0
    """
)

conn.commit()
conn.close()

print("Audit results cleared")