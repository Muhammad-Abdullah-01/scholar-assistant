"""
Evaluation module for semantic retrieval, summarization, and citation systems.
Supports Precision@k, Recall@k, ROUGE-1, ROUGE-L, BLEU, and citation verification.
"""
import json
import csv
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Try to import evaluation libraries
try:
    from rouge_score import rouge_scorer
    ROUGE_AVAILABLE = True
except ImportError:
    ROUGE_AVAILABLE = False
    print("Warning: rouge-score not available. ROUGE metrics will be skipped.")

try:
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    from nltk.tokenize import word_tokenize
    import nltk
    BLEU_AVAILABLE = True
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
except ImportError:
    BLEU_AVAILABLE = False
    print("Warning: nltk not available. BLEU metrics will be skipped.")


def precision_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
    """
    Calculate Precision@k.
    
    Args:
        retrieved_ids: List of retrieved document IDs
        relevant_ids: List of relevant document IDs (ground truth)
        k: Number of top results to consider
    
    Returns:
        Precision@k score (0.0 to 1.0)
    """
    if k == 0 or len(retrieved_ids) == 0:
        return 0.0
    
    top_k = retrieved_ids[:k]
    relevant_retrieved = len(set(top_k) & set(relevant_ids))
    
    return relevant_retrieved / min(k, len(retrieved_ids))


def recall_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
    """
    Calculate Recall@k.
    
    Args:
        retrieved_ids: List of retrieved document IDs
        relevant_ids: List of relevant document IDs (ground truth)
        k: Number of top results to consider
    
    Returns:
        Recall@k score (0.0 to 1.0)
    """
    if len(relevant_ids) == 0:
        return 0.0
    
    top_k = retrieved_ids[:k]
    relevant_retrieved = len(set(top_k) & set(relevant_ids))
    
    return relevant_retrieved / len(relevant_ids)


def calculate_rouge(reference: str, candidate: str) -> Dict[str, float]:
    """
    Calculate ROUGE-1 and ROUGE-L scores.
    
    Args:
        reference: Reference text (ground truth)
        candidate: Candidate text (generated)
    
    Returns:
        Dictionary with 'rouge1' and 'rougel' scores
    """
    if not ROUGE_AVAILABLE:
        return {"rouge1": 0.0, "rougel": 0.0}
    
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
    scores = scorer.score(reference, candidate)
    
    return {
        "rouge1": scores['rouge1'].fmeasure,
        "rougel": scores['rougeL'].fmeasure
    }


def calculate_bleu(reference: str, candidate: str) -> float:
    """
    Calculate BLEU score.
    
    Args:
        reference: Reference text (ground truth)
        candidate: Candidate text (generated)
    
    Returns:
        BLEU score (0.0 to 1.0)
    """
    if not BLEU_AVAILABLE:
        return 0.0
    
    try:
        reference_tokens = word_tokenize(reference.lower())
        candidate_tokens = word_tokenize(candidate.lower())
        
        # Use smoothing to avoid zero scores
        smoothing = SmoothingFunction().method1
        score = sentence_bleu([reference_tokens], candidate_tokens, smoothing_function=smoothing)
        
        return float(score)
    except Exception as e:
        print(f"Error calculating BLEU: {e}")
        return 0.0


def verify_citations(citations: List[Dict], retrieved_papers: List[Dict]) -> Dict[str, float]:
    """
    Verify citations using heuristics.
    
    Checks:
    - Whether cited papers are in retrieved set
    - Whether citation titles match retrieved titles (fuzzy)
    - Whether authors overlap
    
    Args:
        citations: List of citation dictionaries with 'title', 'authors', etc.
        retrieved_papers: List of retrieved paper dictionaries
    
    Returns:
        Dictionary with verification metrics
    """
    if not citations or not retrieved_papers:
        return {
            "citation_coverage": 0.0,
            "title_match_rate": 0.0,
            "author_overlap_rate": 0.0
        }
    
    retrieved_titles = {p.get("title", "").lower().strip() for p in retrieved_papers}
    retrieved_author_sets = [
        set(a.lower() for a in p.get("authors", [])) for p in retrieved_papers
    ]
    
    cited_in_retrieved = 0
    title_matches = 0
    author_overlaps = 0
    
    for citation in citations:
        cite_title = citation.get("title", "").lower().strip()
        cite_authors = set(a.lower() for a in citation.get("authors", []))
        
        # Check if citation is in retrieved set
        if cite_title in retrieved_titles:
            cited_in_retrieved += 1
        
        # Check title similarity (exact match for now, can be extended with fuzzy matching)
        if cite_title in retrieved_titles:
            title_matches += 1
        
        # Check author overlap
        for author_set in retrieved_author_sets:
            if cite_authors & author_set:  # Intersection
                author_overlaps += 1
                break
    
    total_citations = len(citations)
    
    return {
        "citation_coverage": cited_in_retrieved / total_citations if total_citations > 0 else 0.0,
        "title_match_rate": title_matches / total_citations if total_citations > 0 else 0.0,
        "author_overlap_rate": author_overlaps / total_citations if total_citations > 0 else 0.0
    }


def evaluate_query(
    query: str,
    retrieved_papers: List[Dict],
    relevant_paper_ids: List[str],
    reference_summary: Optional[str] = None,
    generated_summary: Optional[str] = None,
    citations: Optional[List[Dict]] = None,
    k_values: List[int] = [5, 10, 20]
) -> Dict:
    """
    Evaluate a single query with all metrics.
    
    Args:
        query: Search query
        retrieved_papers: List of retrieved paper dictionaries
        relevant_paper_ids: List of relevant paper IDs (ground truth)
        reference_summary: Reference summary (ground truth, optional)
        generated_summary: Generated summary (optional)
        citations: List of citation dictionaries (optional)
        k_values: List of k values for Precision@k and Recall@k
    
    Returns:
        Dictionary with all evaluation metrics
    """
    retrieved_ids = []
    for paper in retrieved_papers:
        # Extract ID from paper (prefer paperId, then link)
        paper_id = paper.get("paperId", "")
        if not paper_id:
            link = paper.get("link", "")
            if "arxiv.org" in link:
                paper_id = link.split("/")[-1]
            else:
                paper_id = link
        retrieved_ids.append(paper_id)
    
    # Calculate Precision@k and Recall@k
    precision_scores = {}
    recall_scores = {}
    for k in k_values:
        precision_scores[f"precision@{k}"] = precision_at_k(retrieved_ids, relevant_paper_ids, k)
        recall_scores[f"recall@{k}"] = recall_at_k(retrieved_ids, relevant_paper_ids, k)
    
    # Calculate ROUGE if summaries provided
    rouge_scores = {}
    if reference_summary and generated_summary:
        rouge_scores = calculate_rouge(reference_summary, generated_summary)
    
    # Calculate BLEU if summaries provided
    bleu_score = 0.0
    if reference_summary and generated_summary:
        bleu_score = calculate_bleu(reference_summary, generated_summary)
    
    # Verify citations
    citation_metrics = {}
    if citations and retrieved_papers:
        citation_metrics = verify_citations(citations, retrieved_papers)
    
    return {
        "query": query,
        "retrieved_ids": retrieved_ids,
        "relevant_ids": relevant_paper_ids,
        **precision_scores,
        **recall_scores,
        **rouge_scores,
        "bleu": bleu_score,
        **citation_metrics,
        "timestamp": datetime.now().isoformat()
    }


async def evaluate_from_file(
    test_file: str,
    output_file: str,
    retrieval_function,
    k_values: List[int] = [5, 10, 20]
) -> List[Dict]:
    """
    Evaluate queries from a test file.
    
    Test file format (JSON or JSONL):
    {
        "query": "search query",
        "relevant_ids": ["id1", "id2", ...],
        "reference_summary": "ground truth summary" (optional),
        "expected_citations": [...] (optional)
    }
    
    Args:
        test_file: Path to test file (JSON or JSONL)
        output_file: Path to output CSV file
        retrieval_function: Async function that takes query and returns retrieved papers
        k_values: List of k values for metrics
    
    Returns:
        List of evaluation results
    """
    # Load test data
    test_path = Path(test_file)
    if not test_path.exists():
        raise FileNotFoundError(f"Test file not found: {test_file}")
    
    test_queries = []
    if test_path.suffix == ".json":
        with open(test_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                test_queries = data
            else:
                test_queries = [data]
    elif test_path.suffix == ".jsonl":
        with open(test_path, 'r', encoding='utf-8') as f:
            test_queries = [json.loads(line) for line in f]
    else:
        raise ValueError(f"Unsupported file format: {test_path.suffix}")
    
    # Evaluate each query
    results = []
    
    for test_case in test_queries:
        query = test_case.get("query", "")
        relevant_ids = test_case.get("relevant_ids", [])
        reference_summary = test_case.get("reference_summary")
        expected_citations = test_case.get("expected_citations", [])
        
        # Get retrieved papers
        retrieved_papers = await retrieval_function(query)
        
        # Get generated summary if available
        generated_summary = test_case.get("generated_summary")
        
        # Evaluate
        result = evaluate_query(
            query=query,
            retrieved_papers=retrieved_papers,
            relevant_paper_ids=relevant_ids,
            reference_summary=reference_summary,
            generated_summary=generated_summary,
            citations=expected_citations,
            k_values=k_values
        )
        results.append(result)
    
    # Write to CSV
    if results:
        output_path = Path(output_file)
        fieldnames = [
            "query", "retrieved_ids", "relevant_ids",
            *[f"precision@{k}" for k in k_values],
            *[f"recall@{k}" for k in k_values],
            "rouge1", "rougel", "bleu",
            "citation_coverage", "title_match_rate", "author_overlap_rate",
            "timestamp"
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                # Convert lists to strings for CSV
                row = result.copy()
                row["retrieved_ids"] = ",".join(row.get("retrieved_ids", []))
                row["relevant_ids"] = ",".join(row.get("relevant_ids", []))
                writer.writerow(row)
    
    return results

