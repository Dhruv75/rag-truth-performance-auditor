import sqlite3
import uuid

def seed_demo_data(conn):

    count = conn.execute(
        "SELECT COUNT(*) FROM rag_traces"
    ).fetchone()[0]

    if count > 0:
        return

    demo_records = [
        {
            "query": "What is the travel reimbursement limit?",
            "answer": "₹5000 per trip.",
            "faithfulness": 5,
            "relevance": 5,
            "hallucination": 0,
            "retrieval": 1200,
            "generation": 2500,
        },
        {
            "query": "What is the employee referral bonus?",
            "answer": "₹10000 upon successful hiring.",
            "faithfulness": 5,
            "relevance": 5,
            "hallucination": 0,
            "retrieval": 1400,
            "generation": 2800,
        },
        {
            "query": "What is the CEO's private phone number?",
            "answer": "I do not know.",
            "faithfulness": 5,
            "relevance": 2,
            "hallucination": 0,
            "retrieval": 1500,
            "generation": 3000,
        },
        {
            "query": "What is the travel reimbursement limit?",
            "answer": "₹10000 per trip.",
            "faithfulness": 1,
            "relevance": 4,
            "hallucination": 1,
            "retrieval": 1700,
            "generation": 3400,
        }
    ]

    for row in demo_records:

        trace_id = str(uuid.uuid4())

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
                trace_id,
                row["query"],
                "Demo Context",
                row["answer"],
                row["retrieval"],
                row["generation"],
                350,
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
                trace_id,
                row["faithfulness"],
                row["relevance"],
                row["hallucination"],
                "Demo evaluation record"
            )
        )

    conn.commit()