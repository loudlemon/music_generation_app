# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.api.endpoints import router
from app.core.inference_service import inference_service # Import the singleton instance

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for application startup and shutdown events.
    Used to load the model asynchronously.
    """
    print("Application startup: Loading AI model...")
    await inference_service.load_model()
    print("AI model loaded. Application ready.")
    yield
    print("Application shutdown: Cleaning up resources...")
    # Add any cleanup logic here if needed

app = FastAPI(
    title="Text-to-Music Generation Service",
    description="API for generating music from text prompts using an AI model.",
    version="1.0.0",
    lifespan=lifespan # Register the lifespan context manager
)

# Include the API router
app.include_router(router, prefix="/api/v1", tags=["Music Generation"])

# Mount a static directory for serving generated audio files (for demonstration)
# In a real production environment, audio files would likely be served from S3, GCS, etc.
app.mount("/static", StaticFiles(directory="static_audio"), name="static_audio")

# Create a dummy directory for static audio files
import os
os.makedirs("static_audio", exist_ok=True)
# You might want to put a dummy .mp3 file in 'static_audio' for testing the URL.
# e.g., touch static_audio/dummy.mp3
