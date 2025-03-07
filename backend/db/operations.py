from db.database import Database
from models.user_preferences import UserPreferences
from models.user_activity import UserActivity
from datetime import datetime
from bson import ObjectId

class UserOperations:
    @staticmethod
    async def save_preferences(preferences: UserPreferences) -> bool:
        try:
            db = Database.get_db()
            # Convert to dict and handle ObjectId
            preferences_dict = preferences.dict()
            preferences_dict["user_id"] = str(preferences_dict["user_id"])
            preferences_dict["last_updated"] = datetime.now()
            
            # Upsert the preferences (update if exists, insert if not)
            result = await db.user_preferences.update_one(
                {"user_id": preferences_dict["user_id"]},
                {"$set": preferences_dict},
                upsert=True
            )
            
            # Log the activity
            activity = UserActivity(
                user_id=preferences_dict["user_id"],
                activity_type="preference_update",
                timestamp=datetime.now()
            )
            await db.user_activities.insert_one(activity.dict())
            
            return True
        except Exception as e:
            print(f"Error saving preferences: {e}")
            return False

    @staticmethod
    async def get_preferences(user_id: str) -> dict:
        try:
            db = Database.get_db()
            preferences = await db.user_preferences.find_one({"user_id": str(user_id)})
            if preferences:
                preferences["_id"] = str(preferences["_id"])
            return preferences
        except Exception as e:
            print(f"Error getting preferences: {e}")
            return None 