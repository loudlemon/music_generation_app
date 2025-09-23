
from audiocraft.data.audio import audio_write
from time import monotonic
from fastapi import FastAPI
from model_inference_api.model_inference_api.adapters import generation_queue
from model_inference_api.model_inference_api.adapters.sockets import send_ws_message
from model_inference_api.model_inference_api.adapters import GENERATED_MUSIC_DIR
from model_inference_api.model_inference_api.adapters import generation_queue
import uuid



async def music_generation_worker(app):
    print("Music generation worker started.")
    while True:
        client_id, prompt = await generation_queue.get()
        print(f"Worker received request from {client_id} for prompt: '{prompt}'")

        await send_ws_message(client_id, "status", {"message": "Starting generation...", "progress": 0})

        try:
            start_time = monotonic()

            # Simulate progress updates (MusicGen doesn't have built-in progress callbacks)
            # For a real-time progress bar, you might need to modify audiocraft or estimate time.
            # Here, we'll just send a few updates.
            await send_ws_message(client_id, "status", {"message": "Processing prompt...", "progress": 25})

            # Generate music
            model_output = app.state.music_gen_model.generate([prompt])

            await send_ws_message(client_id, "status", {"message": "Saving audio...", "progress": 75})

            # Save the generated audio
            unique_id = str(uuid.uuid4())
            audio_filename = f"{GENERATED_MUSIC_DIR}/{unique_id}"

            # audiocraft's audio_write saves to a file
            for idx, one_wav in enumerate(model_output):
                # We're generating only one for a single prompt, so idx will be 0
                audio_write(
                    audio_filename,
                    one_wav.cpu(),
                    app.state.music_gen_model.sample_rate,
                    strategy="loudness",
                    loudness_compressor=True
                    )

            # Construct the URL for the generated file
            audio_url = f"/static/{unique_id}.wav" # audiocraft adds .wav automatically

            end_time = monotonic()
            duration = end_time - start_time
            print(f"Generation for '{prompt}' by {client_id} done in {duration:.2f} seconds. Saved to {audio_url}")

            await send_ws_message(client_id, "complete", {
                "prompt": prompt,
                "url": audio_url,
                "duration": f"{duration:.2f} seconds",
                "message": "Generation complete!"
            })

        except Exception as e:
            print(f"Error during music generation for {client_id} (prompt: '{prompt}'): {e}")
            await send_ws_message(client_id, "error", {"message": f"Generation failed: {str(e)}"})
        finally:
            generation_queue.task_done()  # Mark the task as done