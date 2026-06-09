from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Optional
from pathlib import Path
import json
import tempfile
import os
from app.services.evaluation_service import (
    evaluate_query,
    evaluate_from_file,
    precision_at_k,
    recall_at_k,
    calculate_rouge,
    calculate_bleu,
    verify_citations
)
from app.services.semantic_retrieval_service import unified_semantic_search

router = APIRouter(
    prefix="/evaluation",
    tags=["evaluation"],
)


class EvaluationRequest(BaseModel):
    query: str
    retrieved_papers: List[Dict]
    relevant_paper_ids: List[str]
    reference_summary: Optional[str] = None
    generated_summary: Optional[str] = None
    citations: Optional[List[Dict]] = None
    k_values: Optional[List[int]] = [5, 10, 20]

class EvaluationResponse(BaseModel):
    query: str
    precision_scores: Dict[str, float]
    recall_scores: Dict[str, float]
    rouge_scores: Dict[str, float]
    bleu_score: float
    citation_metrics: Dict[str, float]
    timestamp: str


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_single_query(request: EvaluationRequest):
    """
    Evaluate a single query with all metrics.
    """
    try:
        result = evaluate_query(
            query=request.query,
            retrieved_papers=request.retrieved_papers,
            relevant_paper_ids=request.relevant_paper_ids,
            reference_summary=request.reference_summary,
            generated_summary=request.generated_summary,
            citations=request.citations,
            k_values=request.k_values
        )
        
    
        precision_scores = {k: v for k, v in result.items() if k.startswith("precision@")}
        recall_scores = {k: v for k, v in result.items() if k.startswith("recall@")}
        rouge_scores = {
            "rouge1": result.get("rouge1", 0.0),
            "rougel": result.get("rougel", 0.0)
        }
        citation_metrics = {
            "citation_coverage": result.get("citation_coverage", 0.0),
            "title_match_rate": result.get("title_match_rate", 0.0),
            "author_overlap_rate": result.get("author_overlap_rate", 0.0)
        }
        
        return {
            "query": result["query"],
            "precision_scores": precision_scores,
            "recall_scores": recall_scores,
            "rouge_scores": rouge_scores,
            "bleu_score": result.get("bleu", 0.0),
            "citation_metrics": citation_metrics,
            "timestamp": result["timestamp"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating query: {str(e)}")


@router.post("/evaluate-batch")
async def evaluate_batch(file: UploadFile = File(...)):
    """
    Evaluate multiple queries from a test file.
    Returns evaluation results as CSV.
    """
    if not file.filename.endswith(('.json', '.jsonl')):
        raise HTTPException(status_code=400, detail="File must be JSON or JSONL format")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Create output file path
        output_dir = Path("Backend/evaluation_results")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"evaluation_{os.path.basename(file.filename)}.csv"
        
        # Define retrieval function
        async def retrieval_func(query: str):
            return await unified_semantic_search(query, top_k=20)
        
        # Run evaluation
        results = await evaluate_from_file(
            test_file=tmp_path,
            output_file=str(output_file),
            retrieval_function=retrieval_func
        )
        
        # Clean up temp file
        os.remove(tmp_path)
        
        return {
            "message": "Evaluation complete",
            "output_file": str(output_file),
            "num_queries": len(results),
            "results": results[:5]  # Return first 5 as sample
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in batch evaluation: {str(e)}")


@router.get("/")
async def evaluation_api_status():
    """Status endpoint for evaluation API."""
    return {"status": "Evaluation API is running"}

