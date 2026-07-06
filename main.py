from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
import schema


Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get('/health')
def health():
    return{"status":"OK"}

@app.post("/api/v1/tasks", response_model=schema.TaskResponce)
def create_task(task: schema.TaskCreate, db: Session = Depends(get_db)):
    new_task = models.Task(title=task.title, description=task.description, owner_id=1)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task
