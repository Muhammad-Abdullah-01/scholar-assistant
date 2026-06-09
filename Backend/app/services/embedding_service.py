# # import os
# # from typing import List, Optional, Dict
# # import numpy as np
# # from dotenv import load_dotenv
# # import pickle
# # import json
# # from pathlib import Path

# # # Try to import Sentence-BERT, fallback to OpenAI if not available
# # try:
# #     from sentence_transformers import SentenceTransformer
# #     SENTENCE_BERT_AVAILABLE = True
# # except ImportError:
# #     SENTENCE_BERT_AVAILABLE = False
# #     print("Warning: sentence-transformers not available, using OpenAI embeddings")

# # # Try to import FAISS
# # try:
# #     import faiss
# #     FAISS_AVAILABLE = True
# # except ImportError:
# #     FAISS_AVAILABLE = False
# #     print("Warning: FAISS not available, using in-memory similarity search")

# # import openai

# # load_dotenv()

# # # Cache directory for embeddings (relative to this file)
# # CACHE_DIR = Path(__file__).parent.parent.parent / "cache" / "embeddings"
# # CACHE_DIR.mkdir(parents=True, exist_ok=True)

# # # Initialize Sentence-BERT model if available
# # _sbert_model = None
# # if SENTENCE_BERT_AVAILABLE:
# #     try:
# #         _sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
# #         print("Loaded Sentence-BERT model: all-MiniLM-L6-v2")
# #     except Exception as e:
# #         print(f"Error loading Sentence-BERT model: {e}")
# #         SENTENCE_BERT_AVAILABLE = False

# # # FAISS index for cached embeddings
# # _faiss_index = None
# # _embedding_cache = {}  # Maps paper_id -> embedding
# # _paper_metadata = {}  # Maps index -> paper metadata


# # def get_embedding_model():
# #     """Get the Sentence-BERT model instance."""
# #     global _sbert_model
# #     if SENTENCE_BERT_AVAILABLE and _sbert_model is None:
# #         try:
# #             _sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
# #         except Exception as e:
# #             print(f"Error loading Sentence-BERT model: {e}")
# #     return _sbert_model


# # async def get_embedding_openai(text: str, model: str = "text-embedding-3-large") -> List[float]:
# #     """
# #     Generate vector embedding using OpenAI API.
# #     """
# #     try:
# #         resp = openai.embeddings.create(
# #             model=model,
# #             input=text
# #         )
# #         return resp.data[0].embedding
# #     except Exception as e:
# #         print(f"Error generating OpenAI embedding: {e}")
# #         raise


# # def get_embedding_sbert(text: str) -> np.ndarray:
# #     """
# #     Generate vector embedding using Sentence-BERT.
# #     Returns numpy array for efficient computation.
# #     """
# #     model = get_embedding_model()
# #     if model is None:
# #         raise ValueError("Sentence-BERT model not available")
    
# #     embedding = model.encode(text, convert_to_numpy=True)
# #     return embedding


# # async def get_embedding(
# #     text: str, 
# #     use_sbert: bool = True,
# #     model: str = "text-embedding-3-large"
# # ) -> List[float]:
# #     """
# #     Get embedding for text. Prefers Sentence-BERT for speed and cost, 
# #     falls back to OpenAI if requested or if SBERT unavailable.
    
# #     Args:
# #         text: Text to embed
# #         use_sbert: If True, use Sentence-BERT (default). If False, use OpenAI.
# #         model: OpenAI model name (only used if use_sbert=False)
    
# #     Returns:
# #         List of floats representing the embedding
# #     """
# #     if use_sbert and SENTENCE_BERT_AVAILABLE:
# #         embedding = get_embedding_sbert(text)
# #         return embedding.tolist()
# #     else:
# #         return await get_embedding_openai(text, model)


# # def compute_cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
# #     """
# #     Compute cosine similarity between two embeddings.
# #     """
# #     vec1 = np.array(embedding1)
# #     vec2 = np.array(embedding2)
    
# #     dot_product = np.dot(vec1, vec2)
# #     norm1 = np.linalg.norm(vec1)
# #     norm2 = np.linalg.norm(vec2)
    
# #     if norm1 == 0 or norm2 == 0:
# #         return 0.0
    
# #     return float(dot_product / (norm1 * norm2))


# # def get_paper_cache_key(paper: Dict) -> str:
# #     """
# #     Generate a cache key for a paper based on its unique identifier.
# #     """
# #     # Prefer paperId, then link, then title
# #     if "paperId" in paper and paper["paperId"]:
# #         return f"paper_{paper['paperId']}"
# #     elif "link" in paper and paper["link"]:
# #         # Extract arXiv ID from link if present
# #         if "arxiv.org" in paper["link"]:
# #             arxiv_id = paper["link"].split("/")[-1]
# #             return f"arxiv_{arxiv_id}"
# #         return f"link_{hash(paper['link'])}"
# #     else:
# #         return f"title_{hash(paper.get('title', ''))}"


# # async def get_cached_embedding(paper: Dict) -> Optional[List[float]]:
# #     """
# #     Check if embedding for this paper is cached.
# #     Returns embedding if found, None otherwise.
# #     """
# #     cache_key = get_paper_cache_key(paper)
# #     cache_file = CACHE_DIR / f"{cache_key}.pkl"
    
# #     if cache_file.exists():
# #         try:
# #             with open(cache_file, 'rb') as f:
# #                 cached_data = pickle.load(f)
# #                 return cached_data.get("embedding")
# #         except Exception as e:
# #             print(f"Error loading cached embedding: {e}")
    
# #     return None


# # async def cache_embedding(paper: Dict, embedding: List[float]):
# #     """
# #     Cache the embedding for a paper.
# #     """
# #     cache_key = get_paper_cache_key(paper)
# #     cache_file = CACHE_DIR / f"{cache_key}.pkl"
    
# #     try:
# #         cache_data = {
# #             "embedding": embedding,
# #             "paper": {
# #                 "title": paper.get("title", ""),
# #                 "link": paper.get("link", ""),
# #                 "paperId": paper.get("paperId", "")
# #             }
# #         }
# #         with open(cache_file, 'wb') as f:
# #             pickle.dump(cache_data, f)
# #     except Exception as e:
# #         print(f"Error caching embedding: {e}")


# # async def get_or_compute_embedding(
# #     paper: Dict, 
# #     use_sbert: bool = True
# # ) -> List[float]:
# #     """
# #     Get embedding for a paper, using cache if available.
# #     """
# #     # Check cache first
# #     cached_embedding = await get_cached_embedding(paper)
# #     if cached_embedding is not None:
# #         return cached_embedding
    
# #     # Compute new embedding
# #     text = paper.get("summary", paper.get("abstract", ""))
# #     if not text:
# #         text = paper.get("title", "")
    
# #     embedding = await get_embedding(text, use_sbert=use_sbert)
    
# #     # Cache it
# #     await cache_embedding(paper, embedding)
    
# #     return embedding


# # def rank_by_similarity(
# #     query_embedding: List[float],
# #     papers: List[Dict],
# #     paper_embeddings: List[List[float]],
# #     top_k: int = 10
# # ) -> List[Dict]:
# #     """
# #     Rank papers by cosine similarity to query embedding.
    
# #     Args:
# #         query_embedding: Query embedding vector
# #         papers: List of paper dictionaries
# #         paper_embeddings: List of embeddings corresponding to papers
# #         top_k: Number of top results to return
    
# #     Returns:
# #         List of papers sorted by similarity (highest first), with 'score' field added
# #     """
# #     if len(papers) != len(paper_embeddings):
# #         raise ValueError("Papers and embeddings lists must have same length")
    
# #     # Compute similarities
# #     scored_papers = []
# #     for paper, embedding in zip(papers, paper_embeddings):
# #         score = compute_cosine_similarity(query_embedding, embedding)
# #         paper_copy = paper.copy()
# #         paper_copy["score"] = float(score)
# #         scored_papers.append(paper_copy)
    
# #     # Sort by score (descending)
# #     ranked = sorted(scored_papers, key=lambda x: x["score"], reverse=True)
    
# #     return ranked[:top_k]



# import os
# from typing import List, Optional, Dict
# import numpy as np
# from dotenv import load_dotenv
# import pickle
# from pathlib import Path

# # Try to import Sentence-BERT (required for local embeddings)
# try:
#     from sentence_transformers import SentenceTransformer
#     SENTENCE_BERT_AVAILABLE = True
# except ImportError:
#     SENTENCE_BERT_AVAILABLE = False
#     print("Error: sentence-transformers is not available. "
#           "Install it to use local embeddings: pip install sentence-transformers")

# # Try to import FAISS (optional, not currently used)
# try:
#     import faiss  # type: ignore
#     FAISS_AVAILABLE = True
# except ImportError:
#     FAISS_AVAILABLE = False
#     print("Warning: FAISS not available, using in-memory similarity search")

# load_dotenv()

# # Cache directory for embeddings (relative to this file)
# CACHE_DIR = Path(__file__).parent.parent.parent / "cache" / "embeddings"
# CACHE_DIR.mkdir(parents=True, exist_ok=True)

# # Initialize Sentence-BERT model if available
# _sbert_model = None
# if SENTENCE_BERT_AVAILABLE:
#     try:
#         _sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
#         print("Loaded Sentence-BERT model: all-MiniLM-L6-v2")
#     except Exception as e:
#         print(f"Error loading Sentence-BERT model: {e}")
#         SENTENCE_BERT_AVAILABLE = False

# # FAISS index for cached embeddings (not actively used but kept for future extension)
# _faiss_index = None
# _embedding_cache: Dict[str, List[float]] = {}  # Maps paper cache key -> embedding
# _paper_metadata: Dict[int, Dict] = {}  # Maps index -> paper metadata


# def get_embedding_model():
#     """Get (or lazily load) the Sentence-BERT model instance."""
#     global _sbert_model
#     if SENTENCE_BERT_AVAILABLE and _sbert_model is None:
#         try:
#             _sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
#         except Exception as e:
#             print(f"Error loading Sentence-BERT model: {e}")
#     return _sbert_model


# def get_embedding_sbert(text: str) -> np.ndarray:
#     """
#     Generate vector embedding using Sentence-BERT.
#     Returns a numpy array for efficient computation.
#     """
#     model = get_embedding_model()
#     if model is None:
#         raise ValueError(
#             "Sentence-BERT model not available. "
#             "Ensure 'sentence-transformers' is installed."
#         )

#     embedding = model.encode(text, convert_to_numpy=True)
#     return embedding


# async def get_embedding(
#     text: str,
#     use_sbert: bool = True,
#     model: str = "text-embedding-3-large",
# ) -> List[float]:
#     """
#     Get embedding for text.

#     NOTE:
#         This version uses ONLY local Sentence-BERT embeddings.
#         The `use_sbert` and `model` parameters are kept for
#         backwards compatibility but are effectively ignored
#         (Sentence-BERT is always used).

#     Args:
#         text: Text to embed
#         use_sbert: Ignored (kept for compatibility)
#         model: Ignored (no OpenAI is used)

#     Returns:
#         List of floats representing the embedding.
#     """
#     if not SENTENCE_BERT_AVAILABLE:
#         raise RuntimeError(
#             "Sentence-BERT is required for embeddings but is not available. "
#             "Install it with: pip install sentence-transformers"
#         )

#     embedding = get_embedding_sbert(text)
#     return embedding.tolist()


# def compute_cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
#     """
#     Compute cosine similarity between two embeddings.
#     """
#     vec1 = np.array(embedding1, dtype=float)
#     vec2 = np.array(embedding2, dtype=float)

#     dot_product = float(np.dot(vec1, vec2))
#     norm1 = float(np.linalg.norm(vec1))
#     norm2 = float(np.linalg.norm(vec2))

#     if norm1 == 0.0 or norm2 == 0.0:
#         return 0.0

#     return dot_product / (norm1 * norm2)


# def get_paper_cache_key(paper: Dict) -> str:
#     """
#     Generate a cache key for a paper based on its unique identifier.
#     """
#     # Prefer paperId, then link, then title
#     if paper.get("paperId"):
#         return f"paper_{paper['paperId']}"
#     elif paper.get("link"):
#         # Extract arXiv ID from link if present
#         link = paper["link"]
#         if "arxiv.org" in link:
#             arxiv_id = link.split("/")[-1]
#             return f"arxiv_{arxiv_id}"
#         return f"link_{hash(link)}"

#     return f"title_{hash(paper.get('title', ''))}"


# async def get_cached_embedding(paper: Dict) -> Optional[List[float]]:
#     """
#     Check if embedding for this paper is cached.
#     Returns embedding if found, None otherwise.
#     """
#     cache_key = get_paper_cache_key(paper)
#     cache_file = CACHE_DIR / f"{cache_key}.pkl"

#     if cache_file.exists():
#         try:
#             with open(cache_file, "rb") as f:
#                 cached_data = pickle.load(f)
#                 return cached_data.get("embedding")
#         except Exception as e:
#             print(f"Error loading cached embedding: {e}")

#     return None


# async def cache_embedding(paper: Dict, embedding: List[float]):
#     """
#     Cache the embedding for a paper.
#     """
#     cache_key = get_paper_cache_key(paper)
#     cache_file = CACHE_DIR / f"{cache_key}.pkl"

#     try:
#         cache_data = {
#             "embedding": embedding,
#             "paper": {
#                 "title": paper.get("title", ""),
#                 "link": paper.get("link", ""),
#                 "paperId": paper.get("paperId", ""),
#             },
#         }
#         with open(cache_file, "wb") as f:
#             pickle.dump(cache_data, f)
#     except Exception as e:
#         print(f"Error caching embedding: {e}")


# async def get_or_compute_embedding(
#     paper: Dict,
#     use_sbert: bool = True,
# ) -> List[float]:
#     """
#     Get embedding for a paper, using cache if available.
#     """
#     # Check cache first
#     cached_embedding = await get_cached_embedding(paper)
#     if cached_embedding is not None:
#         return cached_embedding

#     # Compute new embedding from summary/abstract/title
#     text = paper.get("summary", paper.get("abstract", "")) or paper.get("title", "")

#     embedding = await get_embedding(text, use_sbert=use_sbert)

#     # Cache it
#     await cache_embedding(paper, embedding)

#     return embedding


# def rank_by_similarity(
#     query_embedding: List[float],
#     papers: List[Dict],
#     paper_embeddings: List[List[float]],
#     top_k: int = 10,
# ) -> List[Dict]:
#     """
#     Rank papers by cosine similarity to query embedding.

#     Args:
#         query_embedding: Query embedding vector
#         papers: List of paper dictionaries
#         paper_embeddings: List of embeddings corresponding to papers
#         top_k: Number of top results to return

#     Returns:
#         List of papers sorted by similarity (highest first), with 'score' field added.
#     """
#     if len(papers) != len(paper_embeddings):
#         raise ValueError("Papers and embeddings lists must have same length")

#     scored_papers: List[Dict] = []
#     for paper, embedding in zip(papers, paper_embeddings):
#         score = compute_cosine_similarity(query_embedding, embedding)
#         paper_copy = paper.copy()
#         paper_copy["score"] = float(score)
#         scored_papers.append(paper_copy)

#     ranked = sorted(scored_papers, key=lambda x: x["score"], reverse=True)
#     return ranked[:top_k]


from typing import List, Optional, Dict
import numpy as np
from pathlib import Path
import pickle

from sklearn.feature_extraction.text import HashingVectorizer

# ------------------------------------------------------------------
# Lightweight local embeddings using HashingVectorizer (no torch)
# ------------------------------------------------------------------

# Cache directory for embeddings (relative to this file)
CACHE_DIR = Path(__file__).parent.parent.parent / "cache" / "embeddings"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Global hashing vectorizer (no fitting needed)
_vectorizer = HashingVectorizer(
    n_features=1024,
    alternate_sign=False,
    norm="l2",
)


def _text_to_embedding(text: str) -> List[float]:
    """
    Convert text to a fixed-size embedding vector using HashingVectorizer.
    """
    if text is None:
        text = ""
    vec = _vectorizer.transform([text])
    # Convert sparse matrix to dense numpy array
    dense = vec.toarray()[0]
    return dense.astype(float).tolist()


async def get_embedding(
    text: str,
    use_sbert: bool = True,
    model: str = "text-embedding-3-large",
) -> List[float]:
    """
    Get embedding for text.

    NOTE:
        This version uses ONLY a local hashing-based embedding.
        Parameters `use_sbert` and `model` are kept for compatibility
        but are ignored.
    """
    return _text_to_embedding(text)


def compute_cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Compute cosine similarity between two embeddings.
    """
    vec1 = np.array(embedding1, dtype=float)
    vec2 = np.array(embedding2, dtype=float)

    dot_product = float(np.dot(vec1, vec2))
    norm1 = float(np.linalg.norm(vec1))
    norm2 = float(np.linalg.norm(vec2))

    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0

    return dot_product / (norm1 * norm2)


def get_paper_cache_key(paper: Dict) -> str:
    """
    Generate a cache key for a paper based on its unique identifier.
    """
    if paper.get("paperId"):
        return f"paper_{paper['paperId']}"
    elif paper.get("link"):
        link = paper["link"]
        if "arxiv.org" in link:
            arxiv_id = link.split("/")[-1]
            return f"arxiv_{arxiv_id}"
        return f"link_{hash(link)}"

    return f"title_{hash(paper.get('title', ''))}"


async def get_cached_embedding(paper: Dict) -> Optional[List[float]]:
    """
    Check if embedding for this paper is cached.
    Returns embedding if found, None otherwise.
    """
    cache_key = get_paper_cache_key(paper)
    cache_file = CACHE_DIR / f"{cache_key}.pkl"

    if cache_file.exists():
        try:
            with open(cache_file, "rb") as f:
                cached_data = pickle.load(f)
                return cached_data.get("embedding")
        except Exception as e:
            print(f"Error loading cached embedding: {e}")

    return None


async def cache_embedding(paper: Dict, embedding: List[float]):
    """
    Cache the embedding for a paper.
    """
    cache_key = get_paper_cache_key(paper)
    cache_file = CACHE_DIR / f"{cache_key}.pkl"

    try:
        cache_data = {
            "embedding": embedding,
            "paper": {
                "title": paper.get("title", ""),
                "link": paper.get("link", ""),
                "paperId": paper.get("paperId", ""),
            },
        }
        with open(cache_file, "wb") as f:
            pickle.dump(cache_data, f)
    except Exception as e:
        print(f"Error caching embedding: {e}")


async def get_or_compute_embedding(
    paper: Dict,
    use_sbert: bool = True,
) -> List[float]:
    """
    Get embedding for a paper, using cache if available.
    """
    cached_embedding = await get_cached_embedding(paper)
    if cached_embedding is not None:
        return cached_embedding

    text = paper.get("summary", paper.get("abstract", "")) or paper.get("title", "")

    embedding = await get_embedding(text, use_sbert=use_sbert)

    await cache_embedding(paper, embedding)

    return embedding


def rank_by_similarity(
    query_embedding: List[float],
    papers: List[Dict],
    paper_embeddings: List[List[float]],
    top_k: int = 10,
) -> List[Dict]:
    """
    Rank papers by cosine similarity to query embedding.
    """
    if len(papers) != len(paper_embeddings):
        raise ValueError("Papers and embeddings lists must have same length")

    scored_papers: List[Dict] = []
    for paper, embedding in zip(papers, paper_embeddings):
        score = compute_cosine_similarity(query_embedding, embedding)
        paper_copy = paper.copy()
        paper_copy["score"] = float(score)
        scored_papers.append(paper_copy)

    ranked = sorted(scored_papers, key=lambda x: x["score"], reverse=True)
    return ranked[:top_k]