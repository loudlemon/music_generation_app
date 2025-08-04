# src/api/endpoints.py
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.api.schemas import (
    GenerateMusicRequest,
    GenerateMusicResponse,
    GetMusicStatusResponse,
)
from app.core.inference_service import (
    InferenceService,
    ModelNotReadyError,
    InvalidTaskError,
)
from app.domain.models import (
    MusicGenerationRequest,
)  # Import domain model for internal use

router = APIRouter()


# Dependency for injecting the InferenceService
# In a larger app, you might use a dependency injection container.
def get_inference_service() -> InferenceService:
    return InferenceService()  # Returns the singleton instance


@router.post(
    "/generate",
    response_model=GenerateMusicResponse,
    status_code=status.HTTP_202_ACCEPTED,  # 202 Accepted for async tasks
    summary="Initiate music generation from text prompt",
    description="Submits a text prompt to the AI model to generate a piece of music. The task is queued for asynchronous processing.",
)
async def generate_music(
    request: GenerateMusicRequest,
    inference_service: InferenceService = Depends(get_inference_service),
):
    """
    Handles the request to generate music.
    """
    try:
        # Convert API schema to domain model for the core service
        domain_request = MusicGenerationRequest(
            prompt=request.prompt,
            duration_seconds=request.duration_seconds,
            genre=request.genre,
            tempo=request.tempo,
        )
        task_result = await inference_service.generate_music(domain_request)

        return GenerateMusicResponse(
            task_id=task_result.task_id,
            status=task_result.status,
            message="Music generation task initiated successfully. Check status using GET /status/{task_id}",
        )
    except ModelNotReadyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )
    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


@router.get(
    "/status/{task_id}",
    response_model=GetMusicStatusResponse,
    summary="Get status of a music generation task",
    description="Retrieves the current status, and if completed, the URL to the generated music file.",
)
async def get_music_status(
    task_id: UUID, inference_service: InferenceService = Depends(get_inference_service)
):
    """
    Retrieves the status of a previously initiated music generation task.
    """
    try:
        task_result = await inference_service.get_generation_status(task_id)

        return GetMusicStatusResponse(
            task_id=task_result.task_id,
            status=task_result.status,
            prompt_used=task_result.prompt_used,
            audio_url=task_result.audio_url,
            duration_seconds_generated=task_result.duration_seconds_generated,
            error_message=task_result.error_message,
        )
    except InvalidTaskError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


@router.get(
    "/health",
    summary="Health check",
    description="Checks the health and model readiness of the service.",
)
async def health_check(
    inference_service: InferenceService = Depends(get_inference_service),
):
    """
    Provides a simple health check endpoint.
    """
    status_msg = "OK"
    model_ready = inference_service.is_model_ready()
    if not model_ready:
        status_msg = "Model not loaded"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": status_msg, "model_ready": model_ready},
        )

    return {"status": status_msg, "model_ready": model_ready}
