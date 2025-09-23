from typing import Dict
import asyncio
from fastapi import WebSocket
import torch

active_connections: Dict[str, WebSocket] = {}
# A queue to hold generation requests
generation_queue: asyncio.Queue = asyncio.Queue()


# --- Configuration ---
GENERATED_MUSIC_DIR = "components/model-inference-api/model-inference-api/storage"
MODEL_NAME = 'facebook/musicgen-small'
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'