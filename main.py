from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
# from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
import schema
from security import hash_Password, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from fastapi.security import HTTPBearer
oauth2_scheme = HTTPBearer()
from fastapi.exceptions import RequestValidationError


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"details":"Something went wrong, please try again later"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    simplified = [{"field": err["loc"][-1], "message": err["msg"]} for err in errors]
    return JSONResponse(status_code=422, content={"detail": simplified})

def get_current_user(token = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )

    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception

    return user

@app.get("/api/v1/users/me", response_model=schema.UserResponce)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.get('/health')
def health():
    return{"status":"OK"}

@app.get("/api/v1/tasks", response_model=list[schema.TaskResponce])
def list_All_Tasks(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    tasks = db.query(models.Task).filter(models.Task.owner_id == current_user.id).all()
    return tasks

@app.get("/api/v1/tasks/{id}", response_model= schema.TaskResponce)
def get_Task(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.owner_id == current_user.id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this task")

    return task

@app.post("/api/v1/tasks", response_model=schema.TaskResponce)
def create_task(task: schema.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_task = models.Task(title=task.title, description=task.description, owner_id=current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.put("/api/v1/tasks/{id}", response_model= schema.TaskResponce)
def update_Task(id: int, updated_task: schema.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this task")
    
    task.title = updated_task.title
    task.description = updated_task.description

    db.commit()
    db.refresh(task)
    return task

@app.delete("/api/v1/tasks/{id}")
def delete_Task(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == id).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")

    db.delete(task)
    db.commit()

    return {"Details":"Task Deleted Succesfully"}

@app.post("/api/v1/auth/register", response_model= schema.UserResponce)
def register(user: schema.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_pw = hash_Password(user.password)
    new_user = models.User(
        username = user.username,
        email = user.email,
        hashed_password = hashed_pw
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/v1/auth/login")
def login(credentials: schema.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == credentials.username).first()

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid Username or Password")
    
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid Username or Password")
    
    access_token = create_access_token({"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}
