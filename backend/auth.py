from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from db.database import Database
from db.operations import UserOperations
from models.user_preferences import UserPreferences
import logging
from fastapi.middleware.cors import CORSMiddleware
from utils.security import pwd_context, create_access_token
from bson import ObjectId

logger = logging.getLogger(__name__)

# Get the absolute path to the backend directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
print(f"Current working directory: {os.getcwd()}")
print(f"Looking for .env file in: {BASE_DIR}")
print(f"JWT_SECRET_KEY loaded: {'Yes' if SECRET_KEY else 'No'}")

if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable not set")

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    db = Database.get_db()
    user = await db.users.find_one({"_id": user_id})
    if user is None:
        raise credentials_exception
        
    # Convert ObjectId to string for JSON serialization
    user["_id"] = str(user["_id"])
    return user

class UserCreate(BaseModel):
    email: str
    username: str
    name: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: str
    email: str
    username: str
    name: str

async def get_user_from_db(username: str) -> Optional[dict]:
    try:
        users_collection = Database.get_db().users
        user = await users_collection.find_one({"username": username})
        return user
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

async def save_user_to_db(user_data: dict):
    try:
        users_collection = Database.get_db().users
        # Check if username already exists
        existing_user = await users_collection.find_one({"username": user_data["username"]})
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
            
        result = await users_collection.insert_one(user_data)
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error saving user: {e}")
        raise e

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class UserRegistration(BaseModel):
    user: dict
    preferences: dict = {}

@router.post("/register")
async def register_user(registration_data: UserRegistration):
    try:
        # Ensure database is connected
        if Database.client is None:
            await Database.connect_db()
        
        # Extract user and preferences data
        user = registration_data.user
        preferences = registration_data.preferences
        
        # Check if username already exists
        db = Database.get_db()
        existing_user = await db.users.find_one({"username": user["username"]})
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # Create user
        hashed_password = pwd_context.hash(user["password"])
        user_doc = {
            "username": user["username"],
            "email": user["email"],
            "hashed_password": hashed_password,
            "name": user["name"],
            "created_at": datetime.now()
        }
        
        result = await db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)
        
        # Save preferences with user_id if provided
        if preferences:
            preferences["user_id"] = user_id
            preferences["name"] = user["name"]
            await UserOperations.save_preferences(UserPreferences(**preferences))
        
        # Create initial token
        access_token = create_access_token(data={"sub": user_id})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

class LoginCredentials(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login_user(credentials: LoginCredentials):
    logger.info(f"Login attempt for user: {credentials.username}")
    try:
        # Ensure database is connected
        if Database.client is None:
            await Database.connect_db()
        
        # Get user from database
        db = Database.get_db()
        user = await db.users.find_one({"username": credentials.username})
        
        if not user:
            logger.warning(f"User not found: {credentials.username}")
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Verify password
        if not pwd_context.verify(credentials.password, user["hashed_password"]):
            logger.warning(f"Invalid password for user: {credentials.username}")
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Create access token
        user_id = str(user["_id"])
        access_token = create_access_token(data={"sub": user_id})
        
        logger.info(f"Successful login for user: {credentials.username}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
            
        db = Database.get_db()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "name": user["name"]
        }
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(status_code=401, detail="Could not validate credentials") 