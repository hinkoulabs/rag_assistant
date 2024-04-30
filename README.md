# Interview Assistant

This project creates an AI-powered assistant to help prepare for interviews. The assistant offers functionalities such as audio transcription, conversation management, and response generation based on a predefined template. It can be extended to log data both to the console and a file, providing comprehensive support for reviewing and refining interview responses.

## Features

### 1. Audio Recording and Transcription

- **Recording:** The assistant captures stereo audio data from the interviewer's microphone, storing it in a queue for processing.
- **Transcription:** The recorded audio is transcribed using OpenAI's Whisper model, converting audio into text efficiently, including converting stereo to mono and processing audio in chunks.

### 2. Conversational Management

- **Prompt Templates:** The assistant uses a predefined template for conversation management. This template guides the flow of conversation, helping to structure both user inputs and AI responses.
- **Memory:** The assistant incorporates a conversation buffer memory to manage and track conversation history, allowing it to maintain context.

### 3. Response Generation

- **Language Model:** The assistant uses the Ollama language model to generate responses based on conversation history and current input.
- **Template-Based:** The responses are generated in line with a concise, professional template, aiming to mimic real-world interview settings.

### 4. Logging and Output

- **Console and File Logging:** The assistant can be extended to log information both to the console and a timestamped file. This ensures comprehensive record-keeping for review and evaluation.
- **Structured Logging:** Logging configuration can direct messages to both the console and file, capturing conversation transcripts, system statuses, and other messages.

## How to Use

1. **Setup:** Install the necessary dependencies:

```bash
python3 -m venv venv

source venv/bin/activate

poetry install
```

2. **Configuration:**

- Create a config.yaml file in the project's root directory, including the following content:

```yaml
template: |
  You are a helpful and friendly AI assistant to pass interview. You are polite, respectful, and aim to provide concise responses of less than 30 words.

  The conversation transcript is as follows:
  {history}

  And here is the user's follow-up: {input}

  Your response:

filename_pattern: "interviews/%Y_%m_%d_%H_%M_%S.txt"
```

3. **Running assistant services:**

- Start vectore store and ollama:

```bash
# run services
docker-compose up --build
```

4. **Running the Program:**

- Start the assistant by executing the main script:

```bash
python main.py
```

5. **Generating Responses:**

- Press Enter to start recording audio, and press Enter again to stop.

- The assistant will transcribe the audio, generate a response, and log information to both the console and a file.

## Extension

### Logging

The program can be extended to log information to a file named "interviews/YYYY_MM_DD_HH_SS.txt", where the filename dynamically reflects the current date and time. This is controlled via the filename_pattern field in the config.yaml file.

### Customization

- **Templates:** Modify the conversation template in config.yaml to suit different interview styles or scenarios.

- **Language Models:** Swap the Ollama model for other language models, adapting the assistant to specific contexts.

## Helpers

```bash
# open terminal on ollama
docker exec -it interview-assistant-ollama-1 bash
```

## Contributing

Contributions are welcome! For feedback or enhancements, please feel free to open a pull request or an issue.

## License

This project is released under the MIT License.
