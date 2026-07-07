from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
import schema


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
