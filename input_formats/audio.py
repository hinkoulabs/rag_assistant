import time
import threading
import numpy as np
import whisper
import sounddevice as sd
from queue import Queue
import logging
from config import load_config
from input_formats.base import Base

class Audio(Base):
    def __init__(self, console) -> None:
        super().__init__(console)
        self.model = whisper.load_model("base.en")
        self.config = load_config()
        self.messages.update(
            {
                "loop_start": "[cyan]Press Enter to start recording, then press Enter again to stop.",
                "started": "[cyan]Assistant started! Press Ctrl+C to exit.",
                "audio_devices": "[cyan]Available audio devices:",
                "select_audio_device": "Please select audio device by number: "
            }
        )

    def pre_action(self):
        self.console.print(self.messages["audio_devices"], sd.query_devices())
        device = int(self.console.input(self.messages["select_audio_device"]))

        self.console.print(self.messages["started"])

        return {
            "device": device
        }

    def loop_action(self, llm_service, pre_args, question):
        device = pre_args['device']
        data_queue = Queue()
        stop_event = threading.Event()
        recording_thread = threading.Thread(target=self._record_audio, args=(device, stop_event, data_queue,))
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
                    self.console.print("[red]Data is not stereo, processing as mono \n")
                    audio_np = audio_np.reshape(-1, 1)

                with self.console.status("Transcribing...", spinner="earth"):
                    text = self._transcribe_channel(audio_np)

                if len(text) > 0:    
                    question = f"Speaker: {text}"

                    logging.info(f"Speaker:\n{text}")
                    self.console.print(f"[red]Speaker:\n")
                    self.console.print(text)

                    self.console.print(f"[red]\nAssistant:\n")
                    response = llm_service.get_response(question)
                    self.console.print("\n")

                    logging.info(f"Assistant:\n{response}")
                else:
                    self.console.print(f"[red]Question is missing!\n")    
            except Exception as e:
                logging.error(f"Audio processing error: {str(e)}")
                self.console.print(f"[red]Audio processing error: {str(e)}")

        else:
            logging.error("No audio recorded. Please ensure your microphone is working.")
            self.console.print("[red]No audio recorded. Please ensure your microphone is working.")


    def _record_audio(self, device, stop_event, data_queue):
        """Captures stereo audio data from the user's microphone and adds it to a queue for processing."""
        def callback(indata, frames, time, status):
            if status:
                self.console.print(status)
            data_queue.put(bytes(indata))

        with sd.RawInputStream(samplerate=16000, device=device, dtype='int16', callback=callback):
            while not stop_event.is_set():
                time.sleep(0.1)


    def _transcribe_channel(self, audio_data, channel=None) -> str:
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
            result = self.model.transcribe(chunk, fp16=False)
            full_transcript.append(result["text"].strip())

        return " ".join(full_transcript)