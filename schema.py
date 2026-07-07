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

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponce(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class config:
        from_attributes = True