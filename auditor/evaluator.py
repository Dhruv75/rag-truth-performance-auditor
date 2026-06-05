import os
import json
import sqlite3
import uuid

from dotenv import load_dotenv
from openai import OpenAI

from prompts import JUDGE_PROMPT

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

conn = sqlite3.connect("auditor.db")

rows = conn.execute(
    """
    SELECT
        id,
        user_query,
        retrieved_context,
        llm_answer
    FROM rag_traces
    WHERE is_audited = 0
    """
).fetchall()

print(f"Found {len(rows)} traces")

for row in rows:

    trace_id = row[0]
    question = row[1]
    context = row[2]
    answer = row[3]

    prompt = JUDGE_PROMPT.format(
        question=question,
        context=context,
        answer=answer
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b:free",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    raw = response.choices[0].message.content

    print("\nJudge Output:")
    print(raw)

    try:

        result = json.loads(raw)

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
                result["faithfulness"],
                result["relevance"],
                int(result["hallucination"]),
                result["reasoning"]
            )
        )

        conn.execute(
            """
            UPDATE rag_traces
            SET is_audited = 1
            WHERE id = ?
            """,
            (trace_id,)
        )

        conn.commit()

    except Exception as e:

        print("Failed to parse:")
        print(e)

conn.close()

print("\nEvaluation Complete")