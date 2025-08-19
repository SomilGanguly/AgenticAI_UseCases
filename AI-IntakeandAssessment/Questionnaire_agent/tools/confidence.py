def score_confidence(best, retrieval, user_answer: str = None) -> str:
    # If user provided, treat as High
    if user_answer and user_answer.strip():
        return "High"
    # best.score is normalized to ~0..4 (semantic reranker) or BM25*4
    if best and best.score >= 3.2:
        return "High"
    if best and best.score >= 1.6:
        return "Medium"
    if best:
        return "Low"
    return "Unknown"