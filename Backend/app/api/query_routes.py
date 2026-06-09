from fastapi import APIRouter,Depends,Path,HTTPException,Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List,Optional
from app.services.summarizer_service import summarize_text,enhance_prompt

router = APIRouter(
    prefix="/queries",
    tags=["queries"],
)


@router.get("/")
async def return_query_api_status():
    return {"status": "Query API is running"}

@router.get("/summarize")
async def summarize_text_endpoint(text: str = Query(..., min_length=1)):
    """
    Summarize the provided text using a language model.
    """
    try:
        summary = summarize_text(text)
        return {
            "original_text": text,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")
    
@router.post("/ehance_prompt")
async def enhance_prompt_endpoint(prompt: str = Query(..., min_length=1)):
    """
    Enhance the provided prompt using a language model.
    """
    try:
        enhanced_prompt = enhance_prompt(prompt)  #
        return {
            "original_prompt": prompt,
            "enhanced_prompt": enhanced_prompt
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enhancing prompt: {str(e)}")