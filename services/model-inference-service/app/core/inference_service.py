# src/core/inference_service.py
import asyncio
from typing import Optional
from uuid import UUID
from app.domain.models import (
    MusicGenerationRequest,
    MusicGenerationResult,
    MusicGenerationStatus,
)


class ModelNotReadyError(Exception):
    """Custom exception for when the model is not loaded or ready."""

    pass


class InvalidTaskError(Exception):
    """Custom exception for when a task ID is not found."""

    pass


class InferenceService:
    """
    Orchestrates the music generation process.
    In a real app, this would interact with model_loader, preprocessor, etc.
    For this example, it's a mock.
    """

    _instance = None
    _is_model_loaded: bool = False
    _mock_tasks: dict[UUID, MusicGenerationResult] = {}  # In-memory mock for tasks

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(InferenceService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):  # Prevent re-initialization
            print("InferenceService initialized.")
            # In a real app, this would trigger model loading,
            # potentially in a background task or on startup.
            # self.load_model()
            self._initialized = True

    async def load_model(self):
        """Simulates loading the AI model."""
        print("Simulating model loading...")
        await asyncio.sleep(2)  # Simulate async loading
        self._is_model_loaded = True
        print("Model loaded successfully.")

    def is_model_ready(self) -> bool:
        return self._is_model_loaded

    async def generate_music(
        self, request: MusicGenerationRequest
    ) -> MusicGenerationResult:
        """
        Initiates a music generation task.
        In a real app, this might push a task to a message queue (e.g., Celery, Kafka).
        """
        if not self.is_model_ready():
            raise ModelNotReadyError(
                "AI model is not loaded or ready. Please try again later."
            )

        # Create a new task result with PENDING/QUEUED status
        task_result = MusicGenerationResult(
            prompt_used=request.prompt, status=MusicGenerationStatus.QUEUED
        )
        self._mock_tasks[task_result.task_id] = task_result

        # Simulate background processing (in a real app, this would be a separate worker)
        asyncio.create_task(self._simulate_generation(task_result.task_id, request))

        return task_result

    async def _simulate_generation(
        self, task_id: UUID, request: MusicGenerationRequest
    ):
        """Simulates the actual music generation process."""
        task = self._mock_tasks.get(task_id)
        if not task:
            return  # Should not happen if called internally

        task.status = MusicGenerationStatus.PROCESSING
        print(f"Task {task_id}: Processing music for prompt '{request.prompt}'")
        try:
            # Simulate actual AI inference time
            await asyncio.sleep(
                request.duration_seconds / 5
            )  # Faster than real time for demo

            # Simulate success or failure
            if "fail" in request.prompt.lower():
                raise ValueError("Simulated failure due to keyword 'fail'.")

            task.audio_url = f"http://localhost:8000/static/audio/{task_id}.mp3"
            task.duration_seconds_generated = request.duration_seconds
            task.status = MusicGenerationStatus.COMPLETED
            print(f"Task {task_id}: Completed. Audio URL: {task.audio_url}")
        except Exception as e:
            task.status = MusicGenerationStatus.FAILED
            task.error_message = f"Generation failed: {str(e)}"
            print(f"Task {task_id}: Failed. Error: {task.error_message}")

    async def get_generation_status(self, task_id: UUID) -> MusicGenerationResult:
        """Retrieves the status of a music generation task."""
        task = self._mock_tasks.get(task_id)
        if not task:
            raise InvalidTaskError(f"Task with ID {task_id} not found.")
        return task


# Global instance for dependency injection (or use a proper DI framework)
inference_service = InferenceService()
