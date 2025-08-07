import os
import traceback  # <-- Import traceback here
from celery import Celery
from dotenv import load_dotenv
from rag_pipeline import generate_readme_from_repo

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_track_started=True,
    result_expires=3600,
)

@celery_app.task(name="create_readme_task")
def create_readme_task(repo_url: str) -> str:
    """
    Celery task that runs the RAG pipeline and captures any exceptions.
    """
    try:
        # Attempt to run the main function
        return generate_readme_from_repo(repo_url)
    except Exception:
        # If any error occurs, format the full traceback as a string
        error_details = traceback.format_exc()
        
        # Print it to the worker log for good measure
        print(f"--- TASK FAILED: An exception occurred for repo {repo_url} ---")
        print(error_details)
        
        # Return the detailed error string as the task's final result
        return f"TASK FAILED:\n\n{error_details}"