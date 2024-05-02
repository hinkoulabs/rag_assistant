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
from document_collections import input_collection

console = Console()
model = whisper.load_model("base.en")
config = load_config()

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

    with sd.RawInputStream(samplerate=16000, device=device, dtype='int16', callback=callback):
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

    console.print("[cyan]Available audio devices:", sd.query_devices())
    device = int(console.input("Please select audio device: "))
    collection_name = input_collection(config, console)

    llm_service = LllService(config, collection_name, verbose=False)

    console.print("[cyan]Assistant started! Press Ctrl+C to exit.")

    try:
        while True:
            console.input("[cyan]Press Enter to start recording, then press Enter again to stop.")

            data_queue = Queue()
            stop_event = threading.Event()
            recording_thread = threading.Thread(target=record_audio, args=(device, stop_event, data_queue,))
            recording_thread.start()

            input()  # Wait for another Enter to stop recording
            stop_event.set()
            recording_thread.join()

            audio_data = b"".join(list(data_queue.queue))
            if len(audio_data) > 0:
                # Checking if mono or stereo
                try:
                    audio_np = np.frombuffer(audio_data, dtype=np.int16)

                    # Check if the data length is divisible by 2 to ensure it's stereo
                    if len(audio_np) % 2 == 0:
                        audio_np = audio_np.reshape(-1, 2)
                    else:
                        # If not, process it as mono
                        console.print("[red]Data is not stereo, processing as mono \n")
                        audio_np = audio_np.reshape(-1, 1)

                    with console.status("Transcribing...", spinner="earth"):
                        text = transcribe_channel(audio_np)

                    if len(text) > 0:    
                        question = f"Speaker: {text}"

                        logging.info(f"Speaker:\n{text}")
                        console.print(f"[red]Speaker:\n")
                        console.print(text)

                        console.print(f"[red]\nAssistant:\n")
                        response = llm_service.get_response(question)
                        console.print("\n")

                        logging.info(f"Assistant:\n{response}")
                    else:
                        console.print(f"[red]Question is missing!\n")    
                except Exception as e:
                    logging.error(f"Audio processing error: {str(e)}")
                    console.print(f"[red]Audio processing error: {str(e)}")

            else:
                logging.error("No audio recorded. Please ensure your microphone is working.")
                console.print("[red]No audio recorded. Please ensure your microphone is working.")

    except KeyboardInterrupt:
        logging.info("[cyan]Exiting...")
        console.print("\n[red]Exiting...")

    console.print("[cyan]Session ended.")

if __name__ == "__main__":
    main()