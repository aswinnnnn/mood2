from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum

class ActivityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class UserPreferences(BaseModel):
    user_id: str
    name: str
    location: Optional[str]
    hobbies: List[str] = []
    likes: List[str] = []
    dislikes: List[str] = []
    favorite_genres: List[str] = []
    activity_level: ActivityLevel = ActivityLevel.MEDIUM
    preferred_meditation_time: Optional[int] = None  # in minutes
    preferred_notification_time: Optional[str] = None  # HH:MM format
    last_updated: datetime = datetime.now()

    @validator('preferred_notification_time')
    def validate_time_format(cls, v):
        if v:
            try:
                hour, minute = map(int, v.split(':'))
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError
            except:
                raise ValueError("Time must be in HH:MM format")
        return v 