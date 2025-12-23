import csv
import math
from collections import defaultdict

def dcg_at_k(relevance_scores, k):
    """
    relevance_scores: list[int | float]
    k: int
    """
    dcg = 0.0
    for i, rel in enumerate(relevance_scores[:k]):
        dcg += rel / math.log2(i + 2)  # i+2 vì i bắt đầu từ 0
    return dcg

def idcg_at_k(relevance_scores, k):
    """
    relevance_scores: list[int | float]
    """
    sorted_rels = sorted(relevance_scores, reverse=True)
    return dcg_at_k(sorted_rels, k)

def ndcg_at_k(relevance_scores, k):
    dcg = dcg_at_k(relevance_scores, k)
    idcg = idcg_at_k(relevance_scores, k)

    if idcg == 0:
        return 0.0

    return dcg / idcg

def precision_at_k(relevance_scores, k):
    """
    Tính Precision@k.
    Precision@k = (Số tài liệu liên quan trong top-k) / k
    """
    relevant_count = sum(1 for rel in relevance_scores[:k] if rel > 0)
    return relevant_count / k

def evaluate_metrics(csv_path, k):
    results = load_results_from_csv(csv_path)

    ndcg_per_query = {}
    precision_per_query = {}
    all_ndcg_scores = []
    all_precision_scores = []

    for query_id, items in results.items():
        items_sorted = sorted(items, key=lambda x: x[0])

        relevance_scores = [rel for _, rel in items_sorted]

        # Tính nDCG@k
        ndcg_score = ndcg_at_k(relevance_scores, k)
        ndcg_per_query[query_id] = ndcg_score
        all_ndcg_scores.append(ndcg_score)

        # Tính Precision@k
        precision_score = precision_at_k(relevance_scores, k)
        precision_per_query[query_id] = precision_score
        all_precision_scores.append(precision_score)

    mean_ndcg = sum(all_ndcg_scores) / len(all_ndcg_scores) if all_ndcg_scores else 0.0
    mean_precision = sum(all_precision_scores) / len(all_precision_scores) if all_precision_scores else 0.0

    return ndcg_per_query, mean_ndcg, precision_per_query, mean_precision

def load_results_from_csv(csv_path):
    """
    Trả về:
    {
        query_id: [(rank, relevance_score), ...]
    }
    """
    results = defaultdict(list)

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            query_id = row["query_id"]
            rank = int(row["rank"])
            relevance_str = row["relevance_score"].strip()

            if relevance_str == "":
                relevance = 0
            else:
                relevance = int(relevance_str)

            results[query_id].append((rank, relevance))

    return results

if __name__ == "__main__":
    csv_path = "evaluate/retrieval_results_manual.csv"

    for k in [5, 10]:
        ndcg_per_query, mean_ndcg, precision_per_query, mean_precision = evaluate_metrics(csv_path, k)

        print(f"\n=== nDCG@{k} ===")
        for qid, score in ndcg_per_query.items():
            print(f"Query {qid}: nDCG@{k} = {score:.4f}")
        print(f"Mean nDCG@{k}: {mean_ndcg:.4f}")

        print(f"\n=== Precision@{k} ===")
        for qid, score in precision_per_query.items():
            print(f"Query {qid}: Precision@{k} = {score:.4f}")
        print(f"Mean Precision@{k}: {mean_precision:.4f}")