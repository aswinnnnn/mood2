from typing import List, Dict, Optional
import json
from datetime import datetime
from openai import AsyncOpenAI
import asyncio
from pydantic import BaseModel
import os
from db.database import Database

class UserContext(BaseModel):
    mood: Optional[str] = None
    recent_activities: Optional[List[str]] = None  
    favorite_genres: Optional[List[str]] = None
    watched_movies: Optional[List[str]] = None
    stress_level: Optional[int] = None
    goals: Optional[List[str]] = None
    recommended_genres: Optional[List[str]] = None

    class Config:
        extra = 'allow'

class EmotionalSupportService:
    _instance = None

    @classmethod
    def get_instance(cls, api_key: str):
        """Singleton pattern to reuse the same service instance"""
        if cls._instance is None:
            cls._instance = cls(api_key)
        return cls._instance

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.context_file = "data/user_context.json"
        self.conversation_file = "data/conversations.json"
        self._init_storage()

    def _init_storage(self):
        """Initialize storage files if they don't exist"""
        os.makedirs('data', exist_ok=True)
        if not os.path.exists(self.context_file):
            with open(self.context_file, 'w') as f:
                json.dump({}, f)
        
        if not os.path.exists(self.conversation_file):
            with open(self.conversation_file, 'w') as f:
                json.dump({}, f)

    async def _load_context(self, user_id: str) -> UserContext:
        """Load user context from MongoDB"""
        try:
            contexts_collection = Database.get_db().contexts
            context = await contexts_collection.find_one({"user_id": user_id})
            return UserContext(**(context or {}))
        except Exception as e:
            print(f"Error loading context: {e}")
            return UserContext()

    async def _save_context(self, user_id: str, context: UserContext):
        """Save user context to MongoDB"""
        try:
            contexts_collection = Database.get_db().contexts
            context_dict = context.model_dump()
            context_dict["user_id"] = user_id
            
            await contexts_collection.update_one(
                {"user_id": user_id},
                {"$set": context_dict},
                upsert=True
            )
        except Exception as e:
            print(f"Error saving context: {e}")

    async def _load_conversation(self, user_id: str) -> List[Dict]:
        """Load conversation history from MongoDB"""
        try:
            conversations_collection = Database.get_db().conversations
            conversation = await conversations_collection.find_one({"user_id": user_id})
            return conversation.get("messages", []) if conversation else []
        except Exception as e:
            print(f"Error loading conversation: {e}")
            return []

    async def _save_conversation(self, user_id: str, messages: List[Dict]):
        """Save conversation history to MongoDB"""
        try:
            conversations_collection = Database.get_db().conversations
            
            # Keep last 50 messages for context
            messages = messages[-50:]
            
            await conversations_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "user_id": user_id,
                        "messages": messages
                    }
                },
                upsert=True
            )
        except Exception as e:
            print(f"Error saving conversation: {e}")

    async def get_support_response(self, user_id: str, user_message: str) -> Dict:
        """
        Get an empathetic response with personalized recommendations
        """
        try:
            # First update the context based on the current message
            await self._update_context(user_id, user_message)
            
            # Then load the fresh context and conversation history
            context = await self._load_context(user_id)
            conversation = await self._load_conversation(user_id)
            
            # Prepare the system message with the mentor persona
            system_message = {
                "role": "system",
                "content": f"""You are an empathetic personal mentor named Joy 🌟. Your role is to:
                1. Provide emotional support and understanding
                2. Offer personalized movie, book, or activity recommendations based on the user's mood
                3. Help users process their emotions and develop coping strategies
                4. Remember previous conversations and user preferences
                5. Maintain a warm, supportive tone while being professional
                
                When recommending content:
                - Consider these genres that match the user's preferences and current mood: {', '.join(context.recommended_genres)}
                - Suggest specific movies/shows with brief explanations of why they might help
                - Consider the user's current emotional state: {context.mood}
                - Include a mix of uplifting and thoughtful content
                - Respect if users want distraction or deeper emotional processing
                
                Remember to:
                - Validate emotions before offering solutions
                - Ask gentle follow-up questions when appropriate
                - Celebrate small wins and progress
                - Maintain boundaries while being supportive"""
            }

            # Prepare messages including context
            messages = [system_message]
            
            # Add relevant context if available
            if context.model_dump(exclude_none=True):
                context_message = {
                    "role": "system",
                    "content": f"User Context: {json.dumps(context.model_dump(exclude_none=True))}"
                }
                messages.append(context_message)
            
            # Add recent conversation history (keep last 20 messages)
            messages.extend(conversation[-20:])
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Get AI response with conversation continuation
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=800,
                presence_penalty=0.6,  # Encourage new topics
                frequency_penalty=0.7,   # Discourage repetition
                top_p=0.9,  # Add nucleus sampling
                stream=False  # Ensure we get complete responses
            )

            assistant_reply = response.choices[0].message.content

            # Update conversation history
            conversation.append({"role": "user", "content": user_message})
            conversation.append({"role": "assistant", "content": assistant_reply})
            await self._save_conversation(user_id, conversation)

            # Update context based on the interaction
            await self._update_context(user_id, user_message)

            return {
                "response": assistant_reply,
                "context": context.model_dump(exclude_none=True)
            }

        except Exception as e:
            print(f"Error in get_support_response: {e}")
            return {
                "error": "Sorry, I'm having trouble processing your request right now.",
                "details": str(e)
            }

    async def _update_context(self, user_id: str, user_message: str):
        """Update user context based on the conversation"""
        context = await self._load_context(user_id)
        
        # Use ChatGPT to detect mood
        mood_prompt = {
            "role": "system",
            "content": """Analyze the following message and determine the primary emotion/mood of the speaker. 
            Choose ONLY ONE of these emotions: happy, sad, anxious, angry, bored, stressed, lonely, overwhelmed.
            Respond with just the emotion word in lowercase, nothing else."""
        }
        
        MOOD_TO_GENRES = {
            "happy": ["comedy", "musical", "adventure", "family"],  # Maintain the joy
            "sad": ["feel-good", "comedy", "inspirational", "drama"],  # Uplift spirits
            "anxious": ["animation", "comedy", "fantasy", "family"],  # Calming content
            "angry": ["comedy", "romance", "feel-good"],  # Lighten the mood
            "bored": ["action", "thriller", "sci-fi", "adventure"],  # Engaging content
            "stressed": ["nature-documentary", "animation", "fantasy"],  # Escapism
            "lonely": ["romance", "drama", "comedy", "feel-good"],  # Connection
            "overwhelmed": ["meditation", "nature-documentary", "gentle-comedy"]  # Calming
        }

        try:
            # Detect mood
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    mood_prompt,
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,  # Lower temperature for more consistent responses
                max_tokens=10     # We only need one word
            )
            
            detected_mood = response.choices[0].message.content.strip().lower()
            if detected_mood in MOOD_TO_GENRES:
                context.mood = detected_mood
                
                # Get recommended genres based on mood
                mood_genres = MOOD_TO_GENRES[detected_mood]
                user_genres = context.favorite_genres or []
                
                # Find common genres between mood recommendations and user preferences
                common_genres = list(set(mood_genres) & set(user_genres))
                
                # If no common genres, use mood genres
                context.recommended_genres = common_genres if common_genres else mood_genres

        except Exception as e:
            print(f"Error updating context: {e}")
        
        # Save updated context
        await self._save_context(user_id, context)

async def interactive_session():
    # Get API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    # TO-DO: need to add user login here to get user_id
    service = EmotionalSupportService.get_instance(api_key)  # Use singleton pattern here
    user_id = "moit"  # This should also come from user authentication
    
    while True:
        user_message = input("\nYou: ")
        if user_message.lower() in ['quit', 'exit', 'bye']:
            break
            
        response = await service.get_support_response(user_id, user_message)
        if "error" in response:
            print(f"Error: {response['error']}")
        else:
            print(f"\nJoy 🌟: {response['response']}")
        
if __name__ == "__main__":
    asyncio.run(interactive_session())



# Example usage:
# async def example_usage():
#     service = EmotionalSupportService(api_key="")
    
#     # Example interaction
#     response = await service.get_support_response(
#         user_id="user123",
#         user_message="I'm feeling really down today after a tough day at work. Could use some movie suggestions to lift my spirits."
#     )
    
#     print(response["response"])

# if __name__ == "__main__":
#     asyncio.run(example_usage())