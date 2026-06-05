JUDGE_PROMPT = """
You are an expert RAG evaluator.

Evaluate the answer using ONLY the provided context.

Question:
{question}

Context:
{context}

Answer:
{answer}

Instructions:

1. Faithfulness Score (1-5)
- 5 = Completely supported by context
- 4 = Mostly supported with minor omissions
- 3 = Partially supported
- 2 = Weakly supported
- 1 = Contradicts context

2. Relevance Score (1-5)
- 5 = Fully answers the question
- 4 = Mostly answers the question
- 3 = Partially answers the question
- 2 = Related but incomplete
- 1 = Irrelevant

3. Hallucination
- true if the answer contains information not supported by the context
- false otherwise

Special Rule:

If the answer is "I do not know" (or a similar refusal such as
"Information not available", "Not mentioned in the context", etc.):

- If the requested information is NOT present in the context:
    faithfulness = 5
    relevance = 2
    hallucination = false

- If the requested information IS present in the context but the model failed to use it:
    faithfulness = 2
    relevance = 1
    hallucination = false

Important Rules:

- Do not penalize an answer for admitting uncertainty.
- A grounded refusal is better than a fabricated answer.
- Any answer that contradicts the context should receive faithfulness = 1.
- Any answer containing unsupported facts should be marked hallucination = true.
- Use the context as the only source of truth.

Return ONLY valid JSON.



Format:

{{
    "faithfulness": <number>,
    "relevance": <number>,
    "hallucination": <true/false>,
    "reasoning": "<short explanation>"
}}
"""