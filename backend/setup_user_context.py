from typing import List, Optional
from pydantic import BaseModel
import os
from db.database import Database
from models.user_preferences import UserPreferences
from datetime import datetime
import asyncio

class UserContext(BaseModel):
    mood: Optional[str] = None
    recent_activities: Optional[List[str]] = None  
    favorite_genres: Optional[List[str]] = None
    watched_movies: Optional[List[str]] = None
    stress_level: Optional[int] = None
    goals: Optional[List[str]] = None

def get_valid_input(prompt: str, valid_options: List[str] = None, is_list: bool = False) -> any:
    while True:
        if is_list:
            print(f"\n{prompt}")
            print("Enter items one by one. Press Enter twice when done.")
            items = []
            while True:
                item = input("> ").strip()
                if not item and items:  # Empty input and we have items
                    return items
                elif item:  # Non-empty input
                    items.append(item)
        else:
            user_input = input(f"\n{prompt}\n> ").strip().lower()
            if not valid_options or user_input in valid_options:
                return user_input
            print(f"Please choose from: {', '.join(valid_options)}")

async def setup_user_context():
    print("Welcome! Let's set up your personal context to provide better recommendations.")
    
    # Initialize database connection
    await Database.connect_db()
    
    try:
        # Get user ID
        user_id = input("\nPlease enter your user name: ").strip()
        
        # Initialize preferences
        preferences = UserPreferences(
            user_id=user_id,
            name=user_id,  # Using username as name for simplicity
            favorite_genres=[],
            hobbies=[],
            likes=[],
            dislikes=[],
            activity_level="medium"
        )
        
        # Get favorite movie genres
        valid_genres = ["action", "comedy", "drama", "horror", "romance", "sci-fi", "thriller", 
                       "documentary", "animation", "fantasy", "family", "adventure"]
        print("\nWhat are your favorite movie genres?")
        print(f"Options: {', '.join(valid_genres)}")
        
        preferences.favorite_genres = []
        while len(preferences.favorite_genres) < 5:
            genre = get_valid_input(f"Enter genre {len(preferences.favorite_genres) + 1}/5:", valid_genres)
            if genre not in preferences.favorite_genres:
                preferences.favorite_genres.append(genre)
        
        # Get hobbies/activities
        preferences.hobbies = get_valid_input(
            "What activities have you been doing lately?", is_list=True
        )
        
        # Get likes
        preferences.likes = get_valid_input(
            "What are some things you like?", is_list=True
        )
        
        # Get dislikes
        preferences.dislikes = get_valid_input(
            "What are some things you dislike?", is_list=True
        )
        
        # Save to database
        result = await Database.get_db().user_preferences.update_one(
            {"user_id": user_id},
            {"$set": preferences.dict()},
            upsert=True
        )
        
        # Check if the operation was acknowledged
        if result.acknowledged:
            print("\nPreferences saved successfully!")
            print("\nYour preferences:")
            print(preferences.dict(exclude_none=True))
        else:
            print("\nError saving preferences: Operation not acknowledged")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close database connection
        await Database.close_db()

if __name__ == "__main__":
    asyncio.run(setup_user_context()) 