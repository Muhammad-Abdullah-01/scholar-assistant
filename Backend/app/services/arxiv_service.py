import arxiv
from typing import List, Dict

async def search_arxiv(query: str, max_results: int = 5) -> List[Dict]:
    """
    Search arXiv using the arxiv Python library and return top results.
    """
    # Construct the default client
    client = arxiv.Client()
    
    # Create a search object
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    
    results_list = []
    
    # Fetch results (arxiv library uses a generator)
    for result in client.results(search):
        authors = [author.name for author in result.authors]
        # Ensure summary is never None
        summary = result.summary if result.summary else "No abstract available"
        results_list.append({
            "title": result.title,
            "authors": authors,
            "summary": str(summary),
            "link": result.entry_id,
            "published": result.published.strftime("%Y-%m-%d"),
            "source": "arxiv"
        })
    
    return results_list
