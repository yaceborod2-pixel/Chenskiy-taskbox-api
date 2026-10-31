from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="TaskBox API", version="1.0.0")




class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=80)
    description: str = Field(default="", max_length=300)
    
    
    
    
class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=80)
    description: str | None = Field(default=None, max_length=300)
    completed: bool | None = None
    
    
    
    
class Task(TaskCreate):
    id: int
    completed: bool = False
    
    
    
    
tasks: dict[int, Task] = {}

next_id = 1


@app.get("/")
def root():
    return {"service": "TaskBox API", "status": "running"}



@app.get("/health")
def health():
    return {"ok": True}



@app.get("/tasks", response_model=list[Task])
def list_tasks(completed: bool | None = None):
    result = list(tasks.values())
    if completed is not None:
        result = [task for task in result if task.completed == completed]
    return result



@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,        
)
def create_task(data: TaskCreate):
    global next_id
    task = Task(id=next_id, **data.model_dump())
    tasks[next_id] = task
    next_id += 1
    return task



@app.patch("/tasks/{task_id})", response_model=Task)
def update_task(task_id: int, data: TaskUpdate):
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    updated = task.model_copy(update=changes)
    tasks[task_id] = updated
    return updated



@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks[task_id]
