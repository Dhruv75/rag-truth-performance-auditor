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
);

CREATE TABLE IF NOT EXISTS audit_results (
    id TEXT PRIMARY KEY,

    trace_id TEXT NOT NULL,

    faithfulness_score INTEGER,

    relevance_score INTEGER,

    is_hallucination INTEGER,

    judge_reasoning TEXT,

    FOREIGN KEY(trace_id)
        REFERENCES rag_traces(id)
);