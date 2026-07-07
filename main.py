from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
import schema
from security import hash_Password, verify_password

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get('/health')
def health():
    return{"status":"OK"}

@app.get("/api/v1/tasks", response_model=list[schema.TaskResponce])
def list_All_Tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Task).all()
    return tasks

@app.get("/api/v1/tasks/{id}", response_model= schema.TaskResponce)
def get_Task(id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/api/v1/tasks", response_model=schema.TaskResponce)
def create_task(task: schema.TaskCreate, db: Session = Depends(get_db)):
    new_task = models.Task(title=task.title, description=task.description, owner_id=1)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.put("/api/v1/tasks/{id}", response_model= schema.TaskResponce)
def update_Task(id: int, updated_task: schema.TaskCreate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.title = updated_task.title
    task.description = updated_task.description

    db.commit()
    db.refresh(task)
    return task

@app.delete("/api/v1/tasks/{id}")
def delete_Task(id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == id).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
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
