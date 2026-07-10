from pydantic import BaseModel, Field, EmailStr

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)

class TaskResponce(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    owner_id: int

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(min_length=8)

class UserResponce(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str