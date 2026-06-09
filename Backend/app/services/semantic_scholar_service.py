import httpx
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
SEMANTIC_SCHOLAR_BASE_URL = "https://api.semanticscholar.org/graph/v1"

async def search_semantic_scholar(
    query: str, 
    max_results: int = 10,
    fields: Optional[List[str]] = None
) -> List[Dict]:
    """
    Search Semantic Scholar API in real-time using /graph/v1/paper/search endpoint.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        fields: Optional list of fields to return (default: title, authors, abstract, url, year, venue)
    
    Returns:
        List of paper dictionaries with unified schema matching arXiv format
    """
    if fields is None:
        fields = ["title", "authors", "abstract", "url", "year", "venue", "paperId"]
    
    url = f"{SEMANTIC_SCHOLAR_BASE_URL}/paper/search"
    
    params = {
        "query": query,
        "limit": min(max_results, 100),  # API limit is 100
        "fields": ",".join(fields)
    }
    
    headers = {}
    if SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = SEMANTIC_SCHOLAR_API_KEY
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            results_list = []
            papers = data.get("data", [])
            
            for paper in papers:
                # Extract authors
                authors = []
                if paper.get("authors"):
                    authors = [author.get("name", "") for author in paper["authors"]]
                
                # Get paper URL - prefer Semantic Scholar URL, fallback to external URLs
                paper_url = paper.get("url", "")
                if not paper_url and paper.get("externalIds"):
                    arxiv_id = paper["externalIds"].get("ArXiv")
                    if arxiv_id:
                        paper_url = f"https://arxiv.org/abs/{arxiv_id}"
                
                # Format year
                year = paper.get("year", "")
                published = str(year) if year else "Unknown"
                
                # Get abstract, ensuring it's never None
                abstract = paper.get("abstract")
                if abstract is None or abstract == "":
                    abstract = "No abstract available"
                
                # Create unified schema matching arXiv format
                paper_dict = {
                    "title": paper.get("title", "No title"),
                    "authors": authors,
                    "summary": str(abstract),
                    "link": paper_url or f"https://www.semanticscholar.org/paper/{paper.get('paperId', '')}",
                    "published": published,
                    "venue": paper.get("venue", ""),
                    "paperId": paper.get("paperId", ""),
                    "source": "semantic_scholar"
                }
                
                results_list.append(paper_dict)
            
            return results_list
            
    except httpx.HTTPStatusError as e:
        print(f"Semantic Scholar API error: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        print(f"Error searching Semantic Scholar: {e}")
        return []


async def get_paper_by_id(paper_id: str) -> Optional[Dict]:
    """
    Get a specific paper by Semantic Scholar paper ID.
    
    Args:
        paper_id: Semantic Scholar paper ID
    
    Returns:
        Paper dictionary or None if not found
    """
    url = f"{SEMANTIC_SCHOLAR_BASE_URL}/paper/{paper_id}"
    
    fields = ["title", "authors", "abstract", "url", "year", "venue", "paperId", "externalIds"]
    params = {"fields": ",".join(fields)}
    
    headers = {}
    if SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = SEMANTIC_SCHOLAR_API_KEY
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            paper = response.json()
            
            # Extract authors
            authors = []
            if paper.get("authors"):
                authors = [author.get("name", "") for author in paper["authors"]]
            
            # Get paper URL
            paper_url = paper.get("url", "")
            if not paper_url and paper.get("externalIds"):
                arxiv_id = paper["externalIds"].get("ArXiv")
                if arxiv_id:
                    paper_url = f"https://arxiv.org/abs/{arxiv_id}"
            
            year = paper.get("year", "")
            published = str(year) if year else "Unknown"
            
            # Get abstract, ensuring it's never None
            abstract = paper.get("abstract")
            if abstract is None or abstract == "":
                abstract = "No abstract available"
            
            return {
                "title": paper.get("title", "No title"),
                "authors": authors,
                "summary": str(abstract),
                "link": paper_url or f"https://www.semanticscholar.org/paper/{paper.get('paperId', '')}",
                "published": published,
                "venue": paper.get("venue", ""),
                "paperId": paper.get("paperId", ""),
                "source": "semantic_scholar"
            }
            
    except Exception as e:
        print(f"Error fetching paper {paper_id}: {e}")
        return None

