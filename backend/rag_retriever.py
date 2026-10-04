import math

from ollama_service import embed_text
from schema_reader import get_schema_documents


def cosine_similarity(vector_a, vector_b):

    dot_product = sum(
        a * b
        for a, b in zip(
            vector_a,
            vector_b
        )
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0

    return dot_product / (
        magnitude_a * magnitude_b
    )


def retrieve_relevant_schema(
    database_path,
    question,
    top_k=3
):

    documents = get_schema_documents(
        database_path
    )

    if not documents:
        raise ValueError(
            "The database contains no tables."
        )

    question_embedding = embed_text(
        question
    )

    scored_documents = []

    for document in documents:

        document_embedding = embed_text(
            document["text"]
        )

        score = cosine_similarity(
            question_embedding,
            document_embedding
        )

        scored_documents.append(
            {
                "table": document["table"],
                "text": document["text"],
                "score": score,
            }
        )

    scored_documents.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    selected = scored_documents[
        :min(top_k, len(scored_documents))
    ]

    schema_context = "\n\n".join(
        item["text"]
        for item in selected
    )

    table_names = [
        item["table"]
        for item in selected
    ]

    return schema_context, table_names