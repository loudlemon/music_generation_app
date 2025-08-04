# src/domain/models.py
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field


class MusicGenerationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    QUEUED = "queued"  # For async task queues


class MusicGenerationRequest(BaseModel):
    """
    Represents the core request for music generation.
    Used internally by the core inference service.
    """

    prompt: str = Field(
        ...,
        min_length=5,
        max_length=30,
        description="Text prompt for music generation.",
    )
    duration_seconds: int = Field(
        10, ge=5, le=180, description="Desired duration of the music in seconds."
    )
    genre: Optional[str] = Field(
        None, description="Optional genre ('orchestral', 'electronic', 'jazz')."
    )
    tempo: Optional[int] = Field(
        None, ge=40, le=200, description="Optional tempo in BPM."
    )


class MusicGenerationResult(BaseModel):
    """
    Represents the core result of a music generation task.
    """

    task_id: UUID = Field(
        default_factory=uuid4, description="Unique identifier for the generation task."
    )
    status: MusicGenerationStatus = Field(
        MusicGenerationStatus.PENDING,
        description="Current status of the generation task.",
    )
    audio_url: Optional[str] = Field(
        None, description="URL to the generated audio file, if completed."
    )
    error_message: Optional[str] = Field(
        None, description="Error message if the generation failed."
    )
    prompt_used: str = Field(
        ..., description="The prompt effectively used for generation."
    )
    duration_seconds_generated: Optional[int] = Field(
        None, description="Actual duration of the generated music in seconds."
    )
