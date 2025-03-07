from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserActivity(BaseModel):
    user_id: str
    activity_type: str  # login, logout, preference_update, etc.
    timestamp: datetime = datetime.now()
    ip_address: Optional[str]
    device_info: Optional[str]
    location: Optional[str]
    is_suspicious: bool = False 