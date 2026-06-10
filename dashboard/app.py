import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from demo_seed import seed_demo_data

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

st.info(
    """
    End-to-end RAG evaluation platform using
    LLM-as-a-Judge scoring for faithfulness,
    relevance, hallucination detection,
    retrieval latency and generation latency.
    """
)

# ==========================
# DATABASE CONNECTION
# ==========================

conn = sqlite3.connect("auditor.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS rag_traces (
    id TEXT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_query TEXT NOT NULL,
    retrieved_context TEXT NOT NULL,
    llm_answer TEXT NOT NULL,
    retrieval_latency_ms INTEGER,
    generation_latency_ms INTEGER,
    total_tokens INTEGER,
    is_audited INTEGER DEFAULT 0
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS audit_results (
    id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    faithfulness_score INTEGER,
    relevance_score INTEGER,
    is_hallucination INTEGER,
    judge_reasoning TEXT,
    FOREIGN KEY(trace_id)
        REFERENCES rag_traces(id)
)
""")

conn.commit()
seed_demo_data(conn)
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

hallucination_count = hallucinations

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

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

col1.metric(
    "Total Queries",
    total_queries
)

col2.metric(
    "Avg Faithfulness",
    round(avg_faithfulness or 0, 2),
    delta=f"{round((avg_faithfulness or 0)-4,2)}"
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
    "Hallucinations",
    hallucination_count
)

col6.metric(
    "Avg Retrieval (ms)",
    round(avg_retrieval or 0, 0)
)

col7.metric(
    "Avg Generation (ms)",
    round(avg_generation or 0, 0)
)

st.divider()


# ==========================
# FAITHFULNESS & RELEVANCE
# ==========================

col_left, col_right = st.columns(2)

with col_left:

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

with col_right:

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

# ==========================
# LATENCY ANALYTICS
# ==========================

col_left, col_right = st.columns(2)

with col_left:

    st.subheader("⚡ Retrieval Latency")

    lat_df = pd.read_sql_query(
        """
        SELECT
            DATE(timestamp) as day,
            AVG(retrieval_latency_ms) as retrieval_latency_ms
        FROM rag_traces
        GROUP BY DATE(timestamp)
        ORDER BY day
        """,
        conn
    )

    fig3 = px.line(
        lat_df,
        x="day",
        y="retrieval_latency_ms",
        title="Average Daily Retrieval Latency"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True,
        key="retrieval_latency"
    )

with col_right:

    st.subheader("⚡ Generation Latency")

    gen_df = pd.read_sql_query(
        """
        SELECT
            DATE(timestamp) as day,
            AVG(generation_latency_ms) as generation_latency_ms
        FROM rag_traces
        GROUP BY DATE(timestamp)
        ORDER BY day
        """,
        conn
    )

    fig4 = px.line(
        gen_df,
        x="day",
        y="generation_latency_ms",
        title="Average Daily Generation Latency"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True,
        key="generation_latency"
    )
# ==========================
# VOLUME & HALLUCINATION
# ==========================

col_left, col_right = st.columns(2)

with col_left:

    st.subheader("📊 Query Volume Over Time")

    volume_df = pd.read_sql_query(
        """
        SELECT
            DATE(timestamp) as day,
            COUNT(*) as queries
        FROM rag_traces
        GROUP BY DATE(timestamp)
        ORDER BY day
        """,
        conn
    )

    fig5 = px.line(
        volume_df,
        x="day",
        y="queries",
        title="Daily Query Volume"
    )

    st.plotly_chart(
        fig5,
        use_container_width=True,
        key="query_volume"
    )

with col_right:

    st.subheader("🚨 Hallucination Trend")

    hall_trend_df = pd.read_sql_query(
        """
        SELECT
            DATE(rt.timestamp) as day,
            ROUND(
                100.0 * SUM(ar.is_hallucination)
                / COUNT(*),
                2
            ) as hallucination_rate

        FROM audit_results ar

        JOIN rag_traces rt
        ON ar.trace_id = rt.id

        GROUP BY DATE(rt.timestamp)

        ORDER BY day
        """,
        conn
    )

    fig6 = px.line(
        hall_trend_df,
        x="day",
        y="hallucination_rate",
        title="Daily Hallucination Rate (%)"
    )

    st.plotly_chart(
        fig6,
        use_container_width=True,
        key="hallucination_trend"
    )

# ==========================
# QUESTIONS & CATEGORIES
# ==========================

col_left, col_right = st.columns(2)

with col_left:

    st.subheader("🔥 Top Asked Questions")

    top_df = pd.read_sql_query(
        """
        SELECT
            user_query,
            COUNT(*) as query_count

        FROM rag_traces

        GROUP BY user_query

        ORDER BY query_count DESC

        LIMIT 10
        """,
        conn
    )

    fig7 = px.bar(
        top_df,
        x="query_count",
        y="user_query",
        orientation="h",
        title="Most Frequently Asked Questions"
    )

    fig7.update_layout(
        yaxis_title="Question",
        xaxis_title="Count"
    )

    st.plotly_chart(
        fig7,
        use_container_width=True,
        key="top_questions"
    )

with col_right:

    st.subheader("🥧 Query Category Breakdown")

    category_df = pd.read_sql_query(
        """
        SELECT
            CASE

                WHEN LOWER(user_query) LIKE '%travel%'
                    OR LOWER(user_query) LIKE '%hotel%'
                THEN 'Travel'

                WHEN LOWER(user_query) LIKE '%leave%'
                THEN 'Leave'

                WHEN LOWER(user_query) LIKE '%password%'
                THEN 'Security'

                WHEN LOWER(user_query) LIKE '%learning%'
                THEN 'Training'

                WHEN LOWER(user_query) LIKE '%referral%'
                THEN 'Recruitment'

                WHEN LOWER(user_query) LIKE '%procurement%'
                THEN 'Procurement'

                WHEN LOWER(user_query) LIKE '%support%'
                THEN 'Support'

                WHEN LOWER(user_query) LIKE '%access logs%'
                THEN 'Privacy'

                WHEN LOWER(user_query) LIKE '%recovery%'
                    OR LOWER(user_query) LIKE '%rto%'
                    OR LOWER(user_query) LIKE '%rpo%'
                THEN 'Business Continuity'

                ELSE 'Other'

            END AS category,

            COUNT(*) AS count

        FROM rag_traces

        GROUP BY category

        ORDER BY count DESC
        """
        ,
        conn
    )

    fig8 = px.pie(
        category_df,
        names="category",
        values="count",
        title="Query Distribution by Category"
    )

    st.plotly_chart(
        fig8,
        use_container_width=True,
        key="category_breakdown"
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
LIMIT 10
    """,
    conn
)

st.dataframe(
    hall_df,
 
 
    use_container_width=True
)


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


st.divider()

st.caption(
    "Built with Streamlit • LangChain • Qdrant • OpenRouter • SQLite"
)

# ==========================
# CLOSE CONNECTION
# ==========================

conn.close()