from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
from app.services.summarizer_service import generate_search_query
from app.services.arxiv_service import search_arxiv
from app.services.semantic_scholar_service import search_semantic_scholar
from app.services.embedding_service import (
    get_embedding,
    get_or_compute_embedding,
    rank_by_similarity
)

router = APIRouter(
    prefix="/citation_router",
    tags=["citation_router"],
)


class CitationRequest(BaseModel):
    text: str
    use_arxiv: Optional[bool] = True
    use_semantic_scholar: Optional[bool] = True
    max_results_per_source: Optional[int] = 5
    top_k: Optional[int] = 10
    use_sbert: Optional[bool] = True

class Paper(BaseModel):
    title: str
    authors: List[str]
    summary: str
    link: str
    published: str
    score: float  # similarity score
    source: Optional[str] = None
    venue: Optional[str] = None
    paperId: Optional[str] = None

class CitationResponse(BaseModel):
    query: str
    results: List[Paper]
    sources_used: List[str]


# -----------------------
# Semantic citation recommender with arXiv + Semantic Scholar
# -----------------------
@router.post("/recommend", response_model=CitationResponse)
async def recommend_citation(request: CitationRequest):
    """
    Recommend citations based on semantic similarity.
    Searches both arXiv and Semantic Scholar for relevant papers.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    user_text = request.text
    print("Received text:", user_text)

    # Generate high-quality search queries from text
    queries = await generate_search_query(user_text)
    print("Generated queries:", queries)

    # Get user text embedding
    user_embedding = await get_embedding(user_text, use_sbert=request.use_sbert)

    # Fetch candidate papers from both sources in parallel
    candidate_papers = []
    sources_used = []
    
    # Collect search tasks
    search_tasks = []
    for query in queries:
        if request.use_arxiv:
            search_tasks.append(search_arxiv(query, max_results=request.max_results_per_source))
            if "arXiv" not in sources_used:
                sources_used.append("arXiv")
        
        if request.use_semantic_scholar:
            search_tasks.append(search_semantic_scholar(query, max_results=request.max_results_per_source))
            if "Semantic Scholar" not in sources_used:
                sources_used.append("Semantic Scholar")
    
    # Execute all searches in parallel
    if search_tasks:
        search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Collect papers from all search results
        for result in search_results:
            if isinstance(result, Exception):
                print(f"Error in search: {result}")
                continue
            if isinstance(result, list):
                candidate_papers.extend(result)
    
    if not candidate_papers:
        return {
            "query": ", ".join(queries),
            "results": [],
            "sources_used": sources_used
        }

    # Deduplicate papers by link/paperId
    seen = set()
    unique_papers = []
    for paper in candidate_papers:
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

    # Get embeddings for all papers (with caching)
    paper_embeddings = []
    embedding_tasks = [
        get_or_compute_embedding(paper, use_sbert=request.use_sbert)
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
        return {
            "query": ", ".join(queries),
            "results": [],
            "sources_used": sources_used
        }

    # Separate papers and embeddings for ranking
    papers, embeddings = zip(*valid_pairs)

    # Rank papers by semantic similarity to user text
    ranked_papers = rank_by_similarity(
        user_embedding,
        list(papers),
        list(embeddings),
        top_k=request.top_k
    )

    # Ensure all papers have required fields
    for paper in ranked_papers:
        if paper.get("summary") is None or not isinstance(paper.get("summary"), str):
            paper["summary"] = "No abstract available"
        if paper.get("title") is None:
            paper["title"] = "No title"
        if not isinstance(paper.get("authors"), list):
            paper["authors"] = []
        # Ensure source field exists
        if "source" not in paper:
            paper["source"] = "unknown"

    return {
        "query": ", ".join(queries),
        "results": ranked_papers,
        "sources_used": sources_used
    }
