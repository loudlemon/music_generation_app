# src/api/schemas.py
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.domain.models import MusicGenerationStatus  # Import domain enum


class GenerateMusicRequest(BaseModel):
    """
    API request schema for initiating music generation.
    """

    prompt: str = Field(
        ...,
        min_length=10,
        max_length=500,
        example="A chill lo-fi beat with a jazzy piano melody and a subtle rain sound in the background.",
        description="Text prompt describing the desired music.",
    )
    duration_seconds: int = Field(
        30,
        ge=10,
        le=180,
        example=60,
        description="Desired duration of the music in seconds (10-180).",
    )
    genre: Optional[str] = Field(
        None,
        example="lo-fi hip-hop",
        description="Optional genre hint (e.g., 'orchestral', 'electronic', 'jazz').",
    )
    tempo: Optional[int] = Field(
        None, ge=40, le=200, example=90, description="Optional tempo in BPM (40-200)."
    )


class GenerateMusicResponse(BaseModel):
    """
    API response schema for the initial music generation request.
    Indicates the task has been accepted.
    """

    task_id: UUID = Field(
        ...,
        example="123e4567-e89b-12d3-a456-426614174000",
        description="Unique identifier for the music generation task.",
    )

    status: MusicGenerationStatus = Field(
        ...,
        example=MusicGenerationStatus.QUEUED,
        description="Current status of the generation task.",
    )
    message: str = Field(
        ...,
        example="Music generation task initiated successfully.",
        description="A user-friendly message.",
    )


class GetMusicStatusResponse(BaseModel):
    """
    API response schema for checking the status of a music generation task.
    """

    task_id: UUID = Field(
        ...,
        example="123e4567-e89b-12d3-a456-426614174000",
        description="Unique identifier for the music generation task.",
    )
    status: MusicGenerationStatus = Field(
        ...,
        example=MusicGenerationStatus.COMPLETED,
        description="Current status of the generation task.",
    )
    prompt_used: str = Field(
        ...,
        example="A chill lo-fi beat with a jazzy piano melody and a subtle rain sound in the background.",
        description="The prompt effectively used for generation.",
    )
    audio_url: Optional[str] = Field(
        None,
        example="http://your-service.com/audio/123e4567-e89b-12d3-a456-426614174000.mp3",
        description="URL to the generated audio file, if status is 'completed'.",
    )
    duration_seconds_generated: Optional[int] = Field(
        None,
        example=58,
        description="Actual duration of the generated music in seconds, if completed.",
    )
    error_message: Optional[str] = Field(
        None,
        example="Model inference failed due to memory constraints.",
        description="Error message if the generation failed.",
    )
