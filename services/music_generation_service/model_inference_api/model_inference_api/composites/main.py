import asyncio
import os
import uuid
import json
import torch
import uvicorn
from time import monotonic
from typing import Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel
import torchaudio
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
from model_inference_api.model_inference_api import adapters
from model_inference_api.model_inference_api import application
from model_inference_api.model_inference_api.application import endpoints, app


origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000", 

]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Include the API router
app.include_router(endpoints.router, prefix="/api/v1", tags=["Music Generation"])

# TEMP Create directory for generated music if it doesn't exist
os.makedirs(adapters.GENERATED_MUSIC_DIR, exist_ok=True)

# TEMP Mount static files directory
app.mount("/static", StaticFiles(directory=adapters.GENERATED_MUSIC_DIR), name="static")