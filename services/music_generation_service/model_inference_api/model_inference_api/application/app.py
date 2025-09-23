from fastapi import FastAPI
import torch
import asyncio
from audiocraft.models import MusicGen
from .services import music_generation_worker
from contextlib import asynccontextmanager
from model_inference_api.model_inference_api.application.model import config
from model_inference_api.model_inference_api.adapters import MODEL_NAME, DEVICE

@asynccontextmanager
async def lifespan(app: FastAPI, config=config.GenModelConfig()):
    """
    Context manager for application startup and shutdown events.
    Used to load the model asynchronously and manage its lifecycle.
    """
    # --- Startup Logic (runs before the 'yield') ---
    print(f"Loading MusicGen model '{MODEL_NAME}' on device '{DEVICE}'...")
    try:
        # Store the model directly on the app state
        app.state.music_gen_model = MusicGen.get_pretrained(config.model_name, device=config.device)
        app.state.music_gen_model.set_generation_params(config.default_duration) # Set default duration
        print("MusicGen model loaded successfully.")

        # Start the background worker
        # You might want to store the task in app.state if you need to cancel it later
        app.state.music_worker_task = asyncio.create_task(
            music_generation_worker(app))
        print("Music generation worker task created.")

    except Exception as e:
        print(f"Failed to load MusicGen model: {e}")
        # If the model is critical for your application to function,
        # it's better to raise an exception here to prevent the server from starting
        # in an uninitialized state.
        raise RuntimeError(f"Critical: Failed to load ML model: {e}")

    # --- Application Runs Here (after 'yield') ---
    yield

    # --- Shutdown Logic (runs after the 'yield' when the application is stopping) ---
    print("Shutting down...")

    # Clean up model
    if hasattr(app.state, 'music_gen_model') and app.state.music_gen_model:
        del app.state.music_gen_model
        print("MusicGen model deleted.")

    # Clear GPU memory if using CUDA
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        print("CUDA cache emptied.")

    # Cancel the background worker task
    if hasattr(app.state, 'music_worker_task') and app.state.music_worker_task:
        app.state.music_worker_task.cancel()
        try:
            await app.state.music_worker_task # Await cancellation to ensure it's handled
            print("Music generation worker task cancelled.")
        except asyncio.CancelledError:
            print("Music generation worker task finished cancellation.")


# --- Background Task for Music Generation ---
app = FastAPI(
    title="Text-to-Music Generation Service",
    description="API for generating music from text prompts using an AI model.",
    version="1.0.0",
    lifespan=lifespan # Register the lifespan context manager
)