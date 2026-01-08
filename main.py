from contextlib import asynccontextmanager
from typing import Annotated, List, Optional
from fastapi import FastAPI, HTTPException, Query, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select

# 1. Database setup (Sqllite):
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# check_same_thread=False is needed only for SQLite
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# A "Dependency" for our API endpoints to access the DB session
SessionDep = Annotated[Session, Depends(get_session)]


# 2. Data Models:
# The Base model contains fields common to DB and API
class TaskBase(SQLModel):
    title: str = Field(index=True)
    description: Optional[str] = None
    is_completed: bool = False

# The Model for the Database table (adds an ID)
class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

# The Model for Creating data (ID is not needed)
class TaskCreate(TaskBase):
    pass

# The Model for Updating data (All fields optional)
class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None


# 3. App Lifecycle:
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables() # Create tables on startup
    yield

app = FastAPI(lifespan=lifespan)


# 4. CRUD Endpoints:

# CREATE
@app.post("/tasks/", response_model=Task)
def create_task(task: TaskCreate, session: SessionDep):
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

# READ (All)
@app.get("/tasks/", response_model=List[Task])
def read_tasks(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    tasks = session.exec(select(Task).offset(offset).limit(limit)).all()
    return tasks

# READ (One)
@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# UPDATE
@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: TaskUpdate, session: SessionDep):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update only the fields that were sent
    task_data = task_update.model_dump(exclude_unset=True)
    db_task.sqlmodel_update(task_data)
    
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

# DELETE
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}

# Mock Task Analyzer:
def simple_ai_model(text: str) -> str:
    if "urgent" in text.lower() or "fail" in text.lower() or "error" in text.lower():
        return "Critical 🔴"
    elif "learn" in text.lower() or "buy" in text.lower():
        return "Growth 🟢"
    else:
        return "Neutral ⚪"

# Add a new endpoint to use this "AI"
@app.post("/tasks/analyze")
def analyze_task_sentiment(description: str):
    sentiment = simple_ai_model(description)
    return {"description": description, "predicted_sentiment": sentiment}