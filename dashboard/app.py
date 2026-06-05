import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="RAG Truth & Performance Auditor",
    layout="wide"
)

# ==========================
# HEADER
# ==========================

st.title("📊 RAG Truth & Performance Auditor")

st.markdown(
    """
Tracks retrieval quality, response faithfulness,
hallucinations, latency and relevance across RAG pipelines.
"""
)

# ==========================
# DATABASE CONNECTION
# ==========================

conn = sqlite3.connect("auditor.db")

# ==========================
# KPI QUERIES
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

avg_retrieval = conn.execute(
    """
    SELECT AVG(retrieval_latency_ms)
    FROM rag_traces
    """
).fetchone()[0]

avg_generation = conn.execute(
    """
    SELECT AVG(generation_latency_ms)
    FROM rag_traces
    """
).fetchone()[0]

hallucination_rate = (
    hallucinations / total_queries * 100
    if total_queries > 0
    else 0
)

# ==========================
# KPI CARDS
# ==========================

col1, col2, col3, col4, col5, col6 = st.columns(6)

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

col5.metric(
    "Avg Retrieval (ms)",
    round(avg_retrieval or 0, 0)
)

col6.metric(
    "Avg Generation (ms)",
    round(avg_generation or 0, 0)
)

st.divider()

# ==========================
# EVALUATION TABLE
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

# ==========================
# FAITHFULNESS CHART
# ==========================

st.subheader("📈 Faithfulness Distribution")

faith_df = pd.read_sql_query(
    """
    SELECT faithfulness_score
    FROM audit_results
    """,
    conn
)

fig1 = px.histogram(
    faith_df,
    x="faithfulness_score",
    nbins=5,
    title="Faithfulness Score Distribution"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# ==========================
# RELEVANCE CHART
# ==========================

st.subheader("📈 Relevance Distribution")

rel_df = pd.read_sql_query(
    """
    SELECT relevance_score
    FROM audit_results
    """,
    conn
)

fig2 = px.histogram(
    rel_df,
    x="relevance_score",
    nbins=5,
    title="Relevance Score Distribution"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.subheader("⚡ Retrieval Latency")

lat_df = pd.read_sql_query(
    """
    SELECT retrieval_latency_ms
    FROM rag_traces
    """,
    conn
)

fig3 = px.line(
    lat_df,
    y="retrieval_latency_ms",
    title="Retrieval Latency"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

st.subheader("⚡ Generation Latency")

gen_df = pd.read_sql_query(
    """
    SELECT generation_latency_ms
    FROM rag_traces
    """,
    conn
)

fig4 = px.line(
    gen_df,
    y="generation_latency_ms",
    title="Generation Latency"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

# ==========================
# HALLUCINATION FEED
# ==========================

st.subheader("🚨 Potential Hallucinations")

hall_df = pd.read_sql_query(
    """
    SELECT
        rt.user_query,
        rt.llm_answer,
        ar.faithfulness_score,
        ar.judge_reasoning

    FROM audit_results ar

    JOIN rag_traces rt
    ON ar.trace_id = rt.id

   WHERE ar.is_hallucination = 1

    ORDER BY rt.timestamp DESC
    """,
    conn
)

st.dataframe(
    hall_df,
    use_container_width=True
)

# ==========================
# CLOSE CONNECTION
# ==========================

conn.close()