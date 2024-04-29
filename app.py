import time
import threading
import numpy as np
import whisper
import sounddevice as sd
from queue import Queue
from rich.console import Console
import logging
from datetime import datetime
from config import load_config
from llm import LllService

console = Console()
model = whisper.load_model("base")
config = load_config()

llm_service = LllService(config, verbose=True)
filename_pattern = config["filename_pattern"]

def setup_logging():
    """Sets up the logging configuration to log to both the console and a file."""
    log_filename = datetime.now().strftime(filename_pattern)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            # logging.StreamHandler(),  # Log to console
            logging.FileHandler(log_filename)  # Log to file
        ]
    )

def record_audio(device, stop_event, data_queue):
    """Captures stereo audio data from the user's microphone and adds it to a queue for processing."""
    def callback(indata, frames, time, status):
        if status:
            console.print(status)
        data_queue.put(bytes(indata))

    with sd.RawInputStream(samplerate=16000, device=device, channels=2, dtype='int16', callback=callback):
        while not stop_event.is_set():
            time.sleep(0.1)

def transcribe_channel(audio_data, channel=None):
    """Transcribes the given audio data using the Whisper speech recognition model."""
    if channel is not None:
        audio_data = audio_data[:, channel]
    else:
        audio_data = np.mean(audio_data, axis=1)

    audio_data = audio_data.astype(np.float32) / 32768.0

    sample_rate = 16000
    chunk_size = sample_rate * 30

    full_transcript = []

    for start in range(0, len(audio_data), chunk_size):
        end = min(start + chunk_size, len(audio_data))
        chunk = audio_data[start:end]
        result = model.transcribe(chunk, fp16=False)
        full_transcript.append(result["text"].strip())

    return " ".join(full_transcript)

def main():
    setup_logging()

    console.print("Available audio devices:", sd.query_devices())
    device = int(console.input("Please select audio device: "))
    console.print("[cyan]Assistant started! Press Ctrl+C to exit.")

    try:
        while True:
            console.input("Press Enter to start recording, then press Enter again to stop.")

            data_queue = Queue()
            stop_event = threading.Event()
            recording_thread = threading.Thread(target=record_audio, args=(device, stop_event, data_queue,))
            recording_thread.start()

            input()  # Wait for another Enter to stop recording
            stop_event.set()
            recording_thread.join()

            audio_data = b"".join(list(data_queue.queue))
            if len(audio_data) > 0:
                audio_np = np.frombuffer(audio_data, dtype=np.int16).reshape(-1, 2)

                with console.status("Transcribing...", spinner="earth"):
                    text = transcribe_channel(audio_np)
                dialogue = f"Speaker: {text}"

                logging.info(f"Speaker:\n{text}")
                console.print(f"[red]Speaker:\n[cyan]{text}")

                with console.status("Generating response...", spinner="earth"):
                    response = llm_service.get_response(dialogue)
                logging.info(f"Assistant:\n{response}")
                console.print(f"[red]Assistant:\n[yellow]{response}")
            else:
                logging.error("No audio recorded. Please ensure your microphone is working.")
                console.print("[red]No audio recorded. Please ensure your microphone is working.")

    except KeyboardInterrupt:
        logging.info("Exiting...")
        console.print("\n[red]Exiting...")

    console.print("[blue]Session ended.")

if __name__ == "__main__":
    main()