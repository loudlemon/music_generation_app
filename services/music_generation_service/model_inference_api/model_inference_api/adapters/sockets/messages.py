from model_inference_api.model_inference_api.adapters import active_connections
from typing import Any

# --- Helper to send WebSocket messages ---
async def send_ws_message(client_id: str, message_type: str, data: Any):
    if client_id in active_connections:
        try:
            await active_connections[client_id].send_json({"type": message_type, "data": data})
        except RuntimeError as e:
            print(f"Failed to send message to client {client_id}: {e}")
            # Consider removing the connection if it's broken
            if client_id in active_connections:
                del active_connections[client_id]
