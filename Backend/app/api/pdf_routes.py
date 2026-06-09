from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List,Optional
from app.services.pdf_service import extract_texts_from_multiple_pdfs,extract_text_from_pdf
from app.services.summarizer_service import summarize_pdf, answer_question
import tempfile
import os
from pydantic import BaseModel


router = APIRouter(
    prefix="/pdf",
    tags=["pdf"]
)

class QuestionRequest(BaseModel):
    pdf_texts: List[str]
    question: str
    conversation_history: Optional[str] = ""


class QuestionResponse(BaseModel):
    answer: str

# Upload PDFs and get summaries
@router.post("/upload")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")
    
    texts = []
    summaries = []
    
    for file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        text = extract_text_from_pdf(tmp_path)
        texts.append(text)
        summary = summarize_pdf(text)
        summaries.append(summary)
        os.remove(tmp_path)
    
    return {"summaries": summaries, "pdf_texts": texts}



@router.post("/question", response_model=QuestionResponse)
async def ask_question(req: QuestionRequest):
    if not req.pdf_texts or not req.question.strip():
        raise HTTPException(status_code=400, detail="PDFs or question missing.")
    try:
        answer = answer_question(req.pdf_texts, req.question, req.conversation_history or "")
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {e}")