import sqlite3

conn = sqlite3.connect("auditor.db")

count = conn.execute(
    """
    SELECT COUNT(*)
    FROM audit_results
    """
).fetchone()[0]

print("Audit Results:", count)

conn.close()