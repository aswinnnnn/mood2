from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import Optional
from test1 import EmotionalSupportService
import asyncio
from dotenv import load_dotenv
import os
from auth import router as auth_router, get_current_user
from pathlib import Path
from db.database import Database
from models.user_preferences import UserPreferences
from models.user_activity import UserActivity
from db.operations import UserOperations
from utils.encryption import encrypt_data, decrypt_data
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the absolute path to the backend directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    try:
        logger.info("Starting up database connection...")
        await Database.connect_db()
        logger.info("Database connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_db_client():
    await Database.close_db()

# Configure CORS with more specific settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Add your frontend URL
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

# Mount the auth router with a prefix
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

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
async def root():
    return {"message": "Welcome to MoodScribe API"}

@app.post("/api/preferences")
async def save_preferences(
    preferences: UserPreferences,
    current_user: dict = Depends(get_current_user)
):
    preferences.user_id = current_user["_id"]
    success = await UserOperations.save_preferences(preferences)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save preferences")
    return {"message": "Preferences saved successfully"}

@app.get("/api/suggestions")
async def get_suggestions(current_user: dict = Depends(get_current_user)):
    suggestions = await UserOperations.get_well_being_suggestions(str(current_user["_id"]))
    return suggestions

@app.get("/api/activity-log")
async def get_activity_log(
    current_user: dict = Depends(get_current_user),
    limit: int = 10
):
    db = Database.get_db()
    activities = await db.user_activities.find(
        {"user_id": str(current_user["_id"])}
    ).sort("timestamp", -1).limit(limit).to_list(length=limit)
    return activities

@app.get("/api/preferences/{user_id}")
async def get_preferences(user_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access these preferences")
    return await UserOperations.get_preferences(user_id)

@app.put("/api/preferences/{user_id}")
async def update_preferences(
    user_id: str, 
    preferences: UserPreferences,
    current_user: dict = Depends(get_current_user)
):
    if current_user["_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update these preferences")
    success = await UserOperations.save_preferences(preferences)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update preferences")
    return {"message": "Preferences updated successfully"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"} 