from pydantic import BaseModel
from datetime import datetime
from app.models.schema.user import UserBasicResponse


class EventParticipantBase(BaseModel):
    event_id: int

class EventParticipantCreate(EventParticipantBase):
    pass

class ParticipantsResponse(BaseModel):
    id: int
    event_id: int
    registered_at: datetime
    user: UserBasicResponse

    class Config:
        from_attributes = True
