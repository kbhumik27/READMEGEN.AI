from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from celery.result import AsyncResult
from celery_worker import create_readme_task
from fastapi.middleware.cors import CORSMiddleware

# This is the corrected line
app = FastAPI(
    title="RAG README Generator API",
    description="An API to generate GitHub READMEs using a RAG pipeline.",
    version="1.0.0"
)

# --- Add this CORS middleware section ---
origins = [
    "http://localhost:3000",  # The address of your React frontend
    # Add your deployed frontend URL here when you deploy
    # "https://your-frontend-app.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)
# --- End of CORS section ---

# Pydantic model for request body validation
class RepoRequest(BaseModel):
    repo_url: HttpUrl # Ensures the URL is valid

# Pydantic model for response
class TaskResponse(BaseModel):
    task_id: str

class StatusResponse(BaseModel):
    task_id: str
    status: str
    result: str | None = None


@app.post("/generate", response_model=TaskResponse, status_code=202)
async def start_generation(request: RepoRequest):
    """
    Accepts a GitHub repository URL and starts the README generation task.
    Returns a task ID for status polling.
    """
    task = create_readme_task.delay(str(request.repo_url))
    return {"task_id": task.id}


@app.get("/status/{task_id}", response_model=StatusResponse)
async def get_task_status(task_id: str):
    """
    Polls the status of a background task using its ID.
    Returns the status and the final README content if completed.
    """
    task_result = AsyncResult(task_id, app=create_readme_task.app)
    
    result = None
    if task_result.successful():
        result = task_result.get()
    elif task_result.failed():
        # Provide a more generic error to the user
        result = "Task failed. Please check the logs for details."

    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": result
    }

@app.get("/")
def read_root():
    return {"message": "Welcome to the RAG README Generator API. Post a repo_url to /generate."}