import csv
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chatbot.agents.tools.food_retriever import retriever

TOP_K = 10
rows = []

with open("evaluate/queries.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    queries = list(reader)

for q in queries:
    query_id = q["query_id"]
    query_text = q["query_text"]

    print(f"Processing query_id: {query_id}")

    docs = retriever(query_text, top_k=TOP_K)

    for rank, doc in enumerate(docs, start=1):
        rows.append({
            "query_id": query_id,
            "food_id": doc.metadata["meal_id"],
            "page_content": doc.page_content,
            "rank": rank,
            "relevance_score": ""
        })

with open("evaluate/retrieval_results_manual.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["query_id", "food_id", "page_content", "rank", "relevance_score"]
    )
    writer.writeheader()
    writer.writerows(rows)