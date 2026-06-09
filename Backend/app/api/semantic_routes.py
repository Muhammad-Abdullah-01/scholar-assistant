from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.services.semantic_retrieval_service import (
    unified_semantic_search,
    semantic_search_with_abstracts
)
from app.services.summarizer_service import summarize_text
from app.services.embedding_service import get_embedding, get_or_compute_embedding, rank_by_similarity
import asyncio

router = APIRouter(
    prefix="/semantic",
    tags=["semantic"],
)


class SemanticSearchRequest(BaseModel):
    query: str
    max_results_per_source: Optional[int] = 10
    top_k: Optional[int] = 20
    use_sbert: Optional[bool] = True

class PipelineRequest(BaseModel):
    query: str
    max_results_per_source: Optional[int] = 10
    top_k: Optional[int] = 10
    use_sbert: Optional[bool] = True
    generate_summary: Optional[bool] = True
    generate_citations: Optional[bool] = True

class Paper(BaseModel):
    title: str
    authors: List[str]
    summary: str
    link: str
    published: str
    score: float
    source: Optional[str] = None
    venue: Optional[str] = None
    paperId: Optional[str] = None

class SemanticSearchResponse(BaseModel):
    query: str
    results: List[Paper]
    total_found: int

class PipelineResponse(BaseModel):
    query: str
    retrieved_papers: List[Paper]
    summary: Optional[str] = None
    citations: Optional[List[Paper]] = None
    total_retrieved: int


# -----------------------
# Semantic Search Endpoint
# -----------------------
@router.post("/search", response_model=SemanticSearchResponse)
async def semantic_search(request: SemanticSearchRequest):
    """
    Perform semantic search across arXiv and Semantic Scholar.
    Returns ranked papers based on semantic similarity.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        results = await unified_semantic_search(
            query=request.query,
            max_results_per_source=request.max_results_per_source,
            top_k=request.top_k,
            use_sbert=request.use_sbert
        )
        
        return {
            "query": request.query,
            "results": results,
            "total_found": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing semantic search: {str(e)}")


# -----------------------
# End-to-End Pipeline: Retrieval → Summarization → Citation
# -----------------------
@router.post("/pipeline", response_model=PipelineResponse)
async def semantic_pipeline(request: PipelineRequest):
    """
    Complete pipeline:
    1. Semantic search across arXiv + Semantic Scholar
    2. Summarize retrieved abstracts
    3. Generate citation recommendations from summary
    
    Returns structured result with papers, summary, and citations.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        # Step 1: Semantic retrieval
        retrieved_papers = await unified_semantic_search(
            query=request.query,
            max_results_per_source=request.max_results_per_source,
            top_k=request.top_k,
            use_sbert=request.use_sbert
        )
        
        summary = None
        citations = None
        
        # Step 2: Summarization (if requested)
        if request.generate_summary and retrieved_papers:
            # Combine abstracts from top papers
            abstracts = []
            for paper in retrieved_papers[:5]:  # Use top 5 for summary
                abstract = paper.get("summary", paper.get("abstract", ""))
                if abstract:
                    abstracts.append(f"Title: {paper.get('title', '')}\nAbstract: {abstract}")
            
            if abstracts:
                combined_text = "\n\n".join(abstracts)
                summary = summarize_text(combined_text)
        
        # Step 3: Citation recommendation (if requested)
        if request.generate_citations and retrieved_papers:
            # Use summary if available, otherwise use query
            citation_query = summary if summary else request.query
            
            # Get embedding for citation query
            citation_embedding = await get_embedding(citation_query, use_sbert=request.use_sbert)
            
            # Get embeddings for all retrieved papers
            paper_embeddings = []
            embedding_tasks = [
                get_or_compute_embedding(paper, use_sbert=request.use_sbert)
                for paper in retrieved_papers
            ]
            paper_embeddings = await asyncio.gather(*embedding_tasks, return_exceptions=True)
            
            # Filter valid embeddings
            valid_pairs = []
            for paper, embedding in zip(retrieved_papers, paper_embeddings):
                if not isinstance(embedding, Exception):
                    valid_pairs.append((paper, embedding))
            
            if valid_pairs:
                papers, embeddings = zip(*valid_pairs)
                # Rank by similarity to summary/query
                citations = rank_by_similarity(
                    citation_embedding,
                    list(papers),
                    list(embeddings),
                    top_k=min(10, len(papers))
                )
        
        return {
            "query": request.query,
            "retrieved_papers": retrieved_papers,
            "summary": summary,
            "citations": citations,
            "total_retrieved": len(retrieved_papers)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in pipeline: {str(e)}")


@router.get("/")
async def semantic_api_status():
    """Status endpoint for semantic API."""
    return {"status": "Semantic API is running"}

