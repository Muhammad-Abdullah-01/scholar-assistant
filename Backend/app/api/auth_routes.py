from fastapi import APIRouter,Depends,Path,HTTPException,Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List,Optional

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.get("/")
async def return_auth_api_status():
    return {"status": "AUTH API is running"}