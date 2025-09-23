import torch
from audiocraft.models import MusicGen
from fastapi import WebSocket, WebSocketDisconnect
import uuid
import asyncio
from fastapi import FastAPI

from model_inference_api.model_inference_api.adapters import active_connections
from model_inference_api.model_inference_api.adapters.sockets import send_ws_message
from model_inference_api.model_inference_api.adapters import generation_queue
from fastapi import APIRouter


router = APIRouter()


# --- WebSocket Endpoint ---
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(uuid.uuid4())  # Generate a unique ID for this client
    active_connections[client_id] = websocket
    print(f"Client {client_id} connected via WebSocket.")

    await websocket.accept()
    await send_ws_message(client_id, "connected", {"client_id": client_id, "message": "Connected to MusicGen service."})

    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "generate" and "prompt" in data:
                prompt = data["prompt"]
                print(f"Client {client_id} requested generation for prompt: '{prompt}'")
                await send_ws_message(client_id, "status", {"message": "Added to queue...", "progress": 0})
                await generation_queue.put((client_id, prompt))
            else:
                print(f"Client {client_id} sent unknown message type: {data.get('type')}")

    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected.")
    except Exception as e:
        print(f"WebSocket error for client {client_id}: {e}")
    finally:
        if client_id in active_connections:
            del active_connections[client_id]
        print(f"Client {client_id} connection cleaned up.")



# --- Root HTML (optional, for serving the React app directly) ---
# If you build your React app, you can put the build output in a "frontend_build" directory
# and uncomment the following to serve it directly from FastAPI.
# For local development, it's easier to run React and FastAPI separately.
# @app.get("/main")
# async def read_root():
#     return FileResponse("frontend_build/index.html")
