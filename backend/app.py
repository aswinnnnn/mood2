from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import Optional
from test1 import EmotionalSupportService
import asyncio
from dotenv import load_dotenv
import os
from auth import router as auth_router
from pathlib import Path
from db.database import Database

# Get the absolute path to the backend directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    await Database.connect_db()

@app.on_event("shutdown")
async def shutdown_db_client():
    await Database.close_db()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load API key from environment variable
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

# Initialize the service
service = EmotionalSupportService.get_instance(API_KEY)

# Include the auth router
app.include_router(router=auth_router, prefix="/api/auth", tags=["auth"])

class DiaryEntry(BaseModel):
    user_id: str
    content: str

class ChatResponse(BaseModel):
    response: str
    context: dict

@app.post("/api/diary-entry", response_model=ChatResponse)
async def process_diary_entry(entry: DiaryEntry):
    try:
        response = await service.get_support_response(
            user_id=entry.user_id,
            user_message=entry.content
        )
        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user-context/{user_id}")
async def get_user_context(user_id: str):
    try:
        context = service._load_context(user_id)
        return context.model_dump(exclude_none=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversation-history/{user_id}")
async def get_conversation_history(user_id: str):
    try:
        history = service._load_conversation(user_id)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI application!"} 