from typing import List, Dict, Optional
import asyncio
from app.services.arxiv_service import search_arxiv
from app.services.semantic_scholar_service import search_semantic_scholar
from app.services.embedding_service import (
    get_embedding,
    get_or_compute_embedding,
    rank_by_similarity
)


async def unified_semantic_search(
    query: str,
    max_results_per_source: int = 10,
    top_k: int = 20,
    use_sbert: bool = True,
    use_arxiv: bool = True,
    use_semantic_scholar: bool = True
) -> List[Dict]:
    """
    Perform unified semantic search across arXiv and Semantic Scholar.
    
    Args:
        query: Natural language search query
        max_results_per_source: Maximum results to fetch from each source
        top_k: Final number of top-ranked results to return
        use_sbert: Use Sentence-BERT for embeddings (faster, free)
        use_arxiv: Include arXiv results
        use_semantic_scholar: Include Semantic Scholar results
    
    Returns:
        List of papers ranked by semantic similarity, with unified schema
    """
    # Fetch papers from both sources in parallel
    tasks = []
    
    if use_arxiv:
        tasks.append(search_arxiv(query, max_results=max_results_per_source))
    
    if use_semantic_scholar:
        tasks.append(search_semantic_scholar(query, max_results=max_results_per_source))
    
    # Wait for all API calls to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Combine results
    all_papers = []
    for result in results:
        if isinstance(result, Exception):
            print(f"Error in search: {result}")
            continue
        if isinstance(result, list):
            all_papers.extend(result)
    
    if not all_papers:
        return []
    
    # Deduplicate by link/paperId
    seen = set()
    unique_papers = []
    for paper in all_papers:
        # Create unique identifier
        paper_id = paper.get("paperId", "")
        link = paper.get("link", "")
        
        if paper_id:
            key = f"id_{paper_id}"
        elif link:
            key = f"link_{link}"
        else:
            # Fallback to title hash
            key = f"title_{hash(paper.get('title', ''))}"
        
        if key not in seen:
            seen.add(key)
            unique_papers.append(paper)
    
    # Get query embedding
    query_embedding = await get_embedding(query, use_sbert=use_sbert)
    
    # Get embeddings for all papers (with caching)
    paper_embeddings = []
    embedding_tasks = [
        get_or_compute_embedding(paper, use_sbert=use_sbert) 
        for paper in unique_papers
    ]
    paper_embeddings = await asyncio.gather(*embedding_tasks, return_exceptions=True)
    
    # Filter out errors and match papers with embeddings
    valid_pairs = []
    for paper, embedding in zip(unique_papers, paper_embeddings):
        if isinstance(embedding, Exception):
            print(f"Error computing embedding for {paper.get('title', 'unknown')}: {embedding}")
            continue
        valid_pairs.append((paper, embedding))
    
    if not valid_pairs:
        return []
    
    # Separate papers and embeddings for ranking
    papers, embeddings = zip(*valid_pairs)
    
    # Rank by semantic similarity
    ranked_papers = rank_by_similarity(
        query_embedding,
        list(papers),
        list(embeddings),
        top_k=top_k
    )
    
    # Ensure all papers have valid summary strings (safety check)
    for paper in ranked_papers:
        if paper.get("summary") is None or not isinstance(paper.get("summary"), str):
            paper["summary"] = "No abstract available"
        # Also ensure title is never None
        if paper.get("title") is None:
            paper["title"] = "No title"
        # Ensure authors is always a list
        if not isinstance(paper.get("authors"), list):
            paper["authors"] = []
    
    return ranked_papers


async def semantic_search_with_abstracts(
    query: str,
    max_results_per_source: int = 10,
    top_k: int = 20,
    use_sbert: bool = True
) -> Dict:
    """
    Perform semantic search and return results with query information.
    
    Returns:
        Dictionary with 'query', 'results', and 'total_found' keys
    """
    results = await unified_semantic_search(
        query=query,
        max_results_per_source=max_results_per_source,
        top_k=top_k,
        use_sbert=use_sbert
    )
    
    return {
        "query": query,
        "results": results,
        "total_found": len(results)
    }

