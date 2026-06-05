import sqlite3
import pandas as pd
import streamlit as st

# ==========================
# Page Config
# ==========================

st.set_page_config(
    page_title="RAG Truth & Performance Auditor",
    layout="wide"
)

st.title("📊 RAG Truth & Performance Auditor")

# ==========================
# Database Connection
# ==========================

conn = sqlite3.connect("auditor.db")

# ==========================
# KPI Queries
# ==========================

total_queries = conn.execute(
    """
    SELECT COUNT(*)
    FROM rag_traces
    """
).fetchone()[0]

avg_faithfulness = conn.execute(
    """
    SELECT AVG(faithfulness_score)
    FROM audit_results
    """
).fetchone()[0]

avg_relevance = conn.execute(
    """
    SELECT AVG(relevance_score)
    FROM audit_results
    """
).fetchone()[0]

hallucinations = conn.execute(
    """
    SELECT COUNT(*)
    FROM audit_results
    WHERE is_hallucination = 1
    """
).fetchone()[0]

hallucination_rate = (
    hallucinations / total_queries * 100
    if total_queries > 0
    else 0
)

# ==========================
# KPI Cards
# ==========================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Queries",
    total_queries
)

col2.metric(
    "Avg Faithfulness",
    round(avg_faithfulness or 0, 2)
)

col3.metric(
    "Avg Relevance",
    round(avg_relevance or 0, 2)
)

col4.metric(
    "Hallucination Rate",
    f"{hallucination_rate:.2f}%"
)

st.divider()

# ==========================
# Evaluation Table
# ==========================

query = """
SELECT
    rt.user_query,
    rt.llm_answer,
    ar.faithfulness_score,
    ar.relevance_score,
    ar.is_hallucination,
    ar.judge_reasoning

FROM audit_results ar

JOIN rag_traces rt
ON ar.trace_id = rt.id

ORDER BY rt.timestamp DESC
"""

df = pd.read_sql_query(query, conn)

st.subheader("Evaluation Results")

st.dataframe(
    df,
    use_container_width=True
)

conn.close()