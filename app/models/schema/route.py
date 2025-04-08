from pydantic import BaseModel, Field
from typing import Optional

class RouteBase(BaseModel):
    name: str
    start_point: str
    end_point: str
    duration: int

class RouteCreate(RouteBase):
    pass

class RouteUpdate(BaseModel):
    name: Optional[str]=None
    start_point: Optional[str]=None
    end_point: Optional[str]=None
    duration: Optional[int]=None

class RouteResponse(RouteBase):
    id: int

    class Config:
        from_attributes = True
