from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
from time import monotonic
from adapters import generation_queue
from adapters.sockets import send_ws_message
from adapters import GENERATED_MUSIC_DIR
from adapters import generation_queue
import uuid


class MusicGen:
    def __init__(self, model_name, device):
        print(f"Initializing MusicGen model '{model_name}' on device '{device}'...")
        self.model_name = model_name
        self.device = device
        self.duration = 0

    @classmethod
    def get_pretrained(cls, model_name, device):
        # Simulate a delay for model loading
        # await asyncio.sleep(2)
        return cls(model_name, device)

    def set_generation_params(self, duration):
        self.duration = duration
        print(f"MusicGen generation duration set to {duration} seconds.")




