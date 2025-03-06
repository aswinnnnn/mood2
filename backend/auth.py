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
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
        
    user = await get_user_from_db(token_data.username)
    if user is None:
        raise credentials_exception
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

@router.post("/register")
async def register(user_data: UserCreate):
    try:
        # Generate user ID (MongoDB will handle this with _id)
        hashed_password = pwd_context.hash(user_data.password)
        user_dict = {
            "email": user_data.email,
            "username": user_data.username,
            "name": user_data.name,
            "hashed_password": hashed_password
        }
        
        user_id = await save_user_to_db(user_dict)
        
        return {
            "success": True,
            "user": {
                "id": user_id,
                "email": user_data.email,
                "username": user_data.username,
                "name": user_data.name
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login")
async def login(user_data: UserLogin):
    user = await get_user_from_db(user_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if not pwd_context.verify(user_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {
        "success": True,
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "username": user["username"],
            "name": user["name"]
        },
        "token": access_token
    } 