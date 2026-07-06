from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description: str | None = None

class TaskResponce(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    owner_id: int

    class Config:
        from_attributes = True