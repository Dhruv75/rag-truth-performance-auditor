import sqlite3
import uuid

conn = sqlite3.connect("auditor.db")

# Demo trace 1
trace_id_1 = str(uuid.uuid4())

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
        total_tokens,
        is_audited
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        trace_id_1,
        "What is the travel reimbursement limit?",
        "Travel reimbursement is limited to ₹5000 per trip.",
        "₹5000 per trip.",
        1200,
        2500,
        320,
        1
    )
)

conn.execute(
    """
    INSERT INTO audit_results
    (
        id,
        trace_id,
        faithfulness_score,
        relevance_score,
        is_hallucination,
        judge_reasoning
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        str(uuid.uuid4()),
        trace_id_1,
        5,
        5,
        0,
        "Answer fully supported by context."
    )
)

# Demo trace 2 (Hallucination)

trace_id_2 = str(uuid.uuid4())

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
        total_tokens,
        is_audited
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        trace_id_2,
        "What is the travel reimbursement limit?",
        "Travel reimbursement is limited to ₹5000 per trip.",
        "₹10000 per trip.",
        1500,
        3200,
        410,
        1
    )
)

conn.execute(
    """
    INSERT INTO audit_results
    (
        id,
        trace_id,
        faithfulness_score,
        relevance_score,
        is_hallucination,
        judge_reasoning
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        str(uuid.uuid4()),
        trace_id_2,
        1,
        4,
        1,
        "Answer contradicts retrieved context."
    )
)

conn.commit()
conn.close()

print("Demo data inserted")