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

2. **Create multi-output devise to stream call into the program:**

- Donwload and install blackhole from `https://github.com/ExistentialAudio/BlackHole`
- Use utility "Audio MIDI Setup" to add multi-output devise with blackhole and other audio outputs (MacOS only)
- Activate the multi-output devise to use the one as default speaker

3. **Install ollama:**

- Donwload and intasll ollama from `https://ollama.com/` (Docker version of ollama works slowly that's why I recomend to use the one directly on laptop)
- Pull model `llama2:13b`

```bash
ollama pull llama2:13b
```

4. **Running assistant services:**

- Start vectore store for RAG:

```bash
# run services
docker-compose up --build
```

5. **Configuration:**

- Create a config.yaml file in the project's root directory, including the following content:

```yaml
# llm prompt
template: |
  You are a helpful and friendly AI assistant to pass interview.

  Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer. 
    Use three sentences maximum and keep the answer as concise as possible (provide concise responses of less than 30 words). 
    Please use language of question to build the answer.
    {context}
  Question: {question}

  Your response:

filename_pattern: "interviews/%Y_%m_%d_%H_%M_%S.txt"

# vector storage setings
vectorstore:
  url: "http://localhost:9200"
 
# llm settings
llm:
  model: "llama2:13b"  

# RAG documents settings
documents:
  # collections are used to split scopes based on interview themes
  collections:
    collection1:
      folder_path: "documents/collection1"
    collection2:
      folder_path: "documents/collection2"      
  formats: ["pdf"]    
  worker_count: 4
```

6. **Create folders:**

- Create folder to store interviews:

```bash
mkdir interviews
```

- Create folders to store RAG documents based on collections from config:

```bash
# create a folder to store docs for collection "collection1"
mkdir documents/collection1

# create a folder to store docs for collection "collection2"
mkdir documents/collection2
```

- Add pdf documents related to `collection1` to folder `documents/collection1`. The ones will be used to generate a context for llm answers.
- Add pdf documents related to `collection2` to folder `documents/collection2`. The ones will be used to generate a context for llm answers.

7. **Index documents**

- Index documents from folder `documents` to vectore storage

```bash
python index_docs.py
```

8. **Running the Program:**

- Start the assistant by executing the main script:

```bash
python assistant.py
```

9. **Generating Responses:**

- Press Enter to start recording audio, and press Enter again to stop.

- The assistant will transcribe the audio, generate a response, and log information to both the console and a file.

## Extension

### Logging

The program can be extended to log information to a file named "interviews/YYYY_MM_DD_HH_SS.txt", where the filename dynamically reflects the current date and time. This is controlled via the filename_pattern field in the config.yaml file.

### Customization

- **Templates:** Modify the conversation template in config.yaml to suit different interview styles or scenarios.

- **Language Models:** Swap the Ollama model for other language models, adapting the assistant to specific contexts.

## Contributing

Contributions are welcome! For feedback or enhancements, please feel free to open a pull request or an issue.

## License

This project is released under the MIT License.
