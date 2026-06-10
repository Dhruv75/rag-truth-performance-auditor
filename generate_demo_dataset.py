import sqlite3
import uuid
import random
from datetime import datetime, timedelta

conn = sqlite3.connect("auditor.db")

# ----------------------------------
# QUERY CATALOG
# ----------------------------------

queries = [
    {
        "question": "What is the travel reimbursement limit?",
        "answer": "₹5000 per trip.",
        "category": "Travel"
    },
    {
        "question": "What is the employee referral bonus?",
        "answer": "₹10000 upon successful hiring.",
        "category": "Recruitment"
    },
    {
        "question": "What is the learning budget?",
        "answer": "₹25000 annually.",
        "category": "Training"
    },
    {
        "question": "What is the Recovery Point Objective?",
        "answer": "1 hour.",
        "category": "Business Continuity"
    },
    {
        "question": "How many annual leave days do employees receive?",
        "answer": "20 annual leave days.",
        "category": "Leave"
    },
    {
        "question": "What is the hotel reimbursement cap?",
        "answer": "₹4000 per night.",
        "category": "Travel"
    },
    {
        "question": "What is the password policy?",
        "answer": "Passwords must contain at least 12 characters.",
        "category": "Security"
    },
    {
        "question": "How long are access logs retained?",
        "answer": "12 months.",
        "category": "Privacy"
    },
    {
        "question": "What is the procurement approval limit?",
        "answer": "₹50000 requires director approval.",
        "category": "Procurement"
    },
    {
        "question": "What is the support SLA?",
        "answer": "4 business hours.",
        "category": "Support"
    }
]

hallucinations = [
    "₹10000 per trip.",
    "Unlimited reimbursement.",
    "50 annual leave days.",
    "RTO is 24 hours.",
    "Passwords require 6 characters.",
    "Access logs are retained forever.",
    "Referral bonus is ₹50000.",
    "Hotel reimbursement is unlimited."
]

# ----------------------------------
# TRAFFIC MODEL
# ----------------------------------

TOTAL_DAYS = 30

for day in range(TOTAL_DAYS):

    current_day = (
        datetime.now()
        - timedelta(days=(TOTAL_DAYS - day))
    )

    weekday = current_day.weekday()

    if weekday >= 5:
        daily_queries = random.randint(5, 12)
    else:
        daily_queries = random.randint(15, 25)

    for _ in range(daily_queries):

        record = random.choice(queries)

        scenario = random.choices(
            population=[
                "good",
                "unknown",
                "hallucination"
            ],
            weights=[
                82,
                10,
                8
            ]
        )[0]

        hour = random.choices(
            population=[
                9,10,11,
                12,13,
                14,15,16,
                17,18
            ],
            weights=[
                10,10,10,
                5,5,
                10,10,10,
                8,5
            ]
        )[0]

        timestamp = current_day.replace(
            hour=hour,
            minute=random.randint(0,59),
            second=random.randint(0,59)
        )

        if 10 <= hour <= 11:
            retrieval_latency = random.randint(
                1200,
                3000
            )
        else:
            retrieval_latency = random.randint(
                700,
                1800
            )

        generation_latency = random.randint(
            1800,
            5500
        )

        total_tokens = random.randint(
            250,
            900
        )

        if scenario == "good":

            answer = record["answer"]

            faithfulness = random.choice(
                [4,5,5,5]
            )

            relevance = random.choice(
                [4,5,5]
            )

            hallucination = 0

            reasoning = (
                "Answer fully grounded in retrieved context."
            )

        elif scenario == "unknown":

            answer = "I do not know."

            faithfulness = 5
            relevance = 2

            hallucination = 0

            reasoning = (
                "Requested information unavailable in retrieved context."
            )

        else:

            answer = random.choice(
                hallucinations
            )

            faithfulness = 1

            relevance = random.randint(
                3,
                5
            )

            hallucination = 1

            reasoning = (
                "Answer contradicts or exceeds retrieved context."
            )

        trace_id = str(uuid.uuid4())

        conn.execute(
            """
            INSERT INTO rag_traces
            (
                id,
                timestamp,
                user_query,
                retrieved_context,
                llm_answer,
                retrieval_latency_ms,
                generation_latency_ms,
                total_tokens,
                is_audited
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trace_id,
                timestamp,
                record["question"],
                f"Retrieved context for {record['category']}",
                answer,
                retrieval_latency,
                generation_latency,
                total_tokens,
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
                faithfulness,
                relevance,
                hallucination,
                reasoning
            )
        )

conn.commit()
conn.close()

print("Production-grade demo dataset generated.")