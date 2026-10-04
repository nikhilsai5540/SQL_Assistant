import json

from ollama_service import chat


def generate_answer(
    question,
    columns,
    rows
):

    if not rows:
        return (
            "No matching records were found "
            "for your question."
        )

    # Don't send hundreds of rows to the model
    preview_rows = rows[:50]

    result_data = {
        "columns": columns,
        "rows": preview_rows,
    }

    system_prompt = """
You are a database assistant.

Answer the user's question using ONLY
the SQL result provided.

Rules:

1. Do not invent information.
2. Keep the answer short and clear.
3. Mention important numbers or names.
4. If multiple results exist, summarize them.
5. Do not mention SQL unless necessary.
"""

    user_prompt = f"""
USER QUESTION:

{question}

DATABASE RESULT:

{json.dumps(result_data, default=str)}

Give a natural-language answer.
"""

    return chat(
        [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0,
    ).strip()