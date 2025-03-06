import json
from typing import List, Optional
from pydantic import BaseModel
import os

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

def setup_user_context():
    print("Welcome! Let's set up your personal context to provide better recommendations.")
    
    # Get user ID
    user_id = input("\nPlease enter your user name: ").strip()
    
    # Initialize context
    context = UserContext()
    
    # Get current mood
    context.mood = "happy"
    
    # Get favorite movie genres
    valid_genres = ["action", "comedy", "drama", "horror", "romance", "sci-fi", "thriller", 
                   "documentary", "animation", "fantasy", "family", "adventure"]
    print("\nWhat are your favorite movie genres?")
    print(f"Options: {', '.join(valid_genres)}")
    context.favorite_genres = []
    while len(context.favorite_genres) < 5:
        genre = get_valid_input(f"Enter genre {len(context.favorite_genres) + 1}/5:", valid_genres)
        if genre not in context.favorite_genres:
            context.favorite_genres.append(genre)
    
    # Get recent activities
    context.recent_activities = get_valid_input(
        "What activities have you been doing lately?", is_list=True
    )
    
    # Get watched movies
    context.watched_movies = get_valid_input(
        "What are some movies you've watched recently?", is_list=True
    )
    
    # Get stress level
    context.stress_level = 5
    
    # Get goals
    context.goals = get_valid_input(
        "What are some of your current goals or things you'd like to work on?", is_list=True
    )
    
    # Save to file
    context_file = "user_context.json"
    try:
        if os.path.exists(context_file):
            with open(context_file, 'r') as f:
                contexts = json.load(f)
        else:
            contexts = {}
        
        contexts[user_id] = context.dict(exclude_none=True)
        
        with open(context_file, 'w') as f:
            json.dump(contexts, f, indent=2)
        
        print("\nContext saved successfully!")
        print("\nYour context:")
        print(json.dumps(context.dict(exclude_none=True), indent=2))
        
    except Exception as e:
        print(f"Error saving context: {e}")

if __name__ == "__main__":
    setup_user_context() 