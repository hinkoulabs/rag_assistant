# RAG Assistant

RAG Assistant is an AI-powered console tool designed to answer questions based on specific contexts (e.g., PDF files) and input types (text or audio). It offers functionalities such as audio transcription, conversation management, and response generation using a predefined template. The assistant also supports comprehensive logging to both the console and files, facilitating review and refinement of question responses.

The primary purpose of this project is to test RAG integration and enable the use of AI for sensitive data without exposing it to public platforms.

## Table of Contents
1. [Features](#features)
    - [Audio Recording and Transcription](#1-audio-recording-and-transcription)
    - [Conversational Management](#2-conversational-management)
    - [Response Generation](#3-response-generation)
    - [Logging and Output](#4-logging-and-output)
2. [How to Use](#how-to-use)
    - [Setup](#1-setup)
    - [Install Ollama](#2-install-ollama)
    - [Running Assistant Services Using Docker](#3-running-assistant-services-using-docker)
    - [Create Folders to Store Context Documents](#4-create-folders-to-store-context-documents)
    - [Configuration](#5-configuration)
    - [Index Documents](#6-index-documents)
    - [Create Multi-Output Device for Audio Input (for Calls)](#7-create-multi-output-device-for-audio-input-for-calls)
    - [Running the Program](#8-running-the-program)
    - [Generating Responses (Text Input)](#9-generating-responses-text-input)
    - [Generating Responses (Audio Input)](#10-generating-responses-audio-input)
3. [Extension](#extension)
    - [Logging](#logging)
    - [Customization](#customization)
4. [Contributing](#contributing)
5. [License](#license)

## Features

### 1. Audio Recording and Transcription

- **Recording:** Captures stereo audio data from the user's microphone, storing it in a queue for processing.
- **Transcription:** Utilizes OpenAI's Whisper model to transcribe recorded audio into text, efficiently converting stereo to mono and processing audio in chunks.

### 2. Conversational Management

- **Prompt Templates:** Uses a predefined template to guide the flow of conversation, structuring both user inputs and AI responses.
- **Memory:** Incorporates a conversation buffer memory to track conversation history and maintain context.

### 3. Response Generation

- **Language Model:** Utilizes the Ollama language model to generate responses based on conversation history and current input.
- **Template-Based:** Generates responses in line with a concise, professional template, mimicking real-world interview settings.

### 4. Logging and Output

- **Console and File Logging:** Logs information to both the console and timestamped files, ensuring comprehensive record-keeping for review and evaluation.
- **Structured Logging:** Configurable to direct messages to both console and file, capturing conversation transcripts, system statuses, and other messages.

## How to Use

### 1. Setup

Install the necessary dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
poetry install
```

### 2. Install Ollama

Donwload and install [Ollama](https://ollama.com/) (Docker version of ollama works slowly that's why I recomend to use the one directly on laptop)

Pull model `llama2:13b`

```bash
ollama pull llama2:13b
```

### 3. Running Assistant Services Using Docker

Start the vector store for RAG:

```bash
# run services
docker-compose up --build
```

### 4. Create Folders to Store Context Documents

Create folders to store context documents:

```bash
# example of creation a folder to store docs for context "my_private_data"
mkdir contexts/my_private_data

# example of creation a folder to store docs for context "laws"
mkdir contexts/laws
```

Add PDF documents to the respective folders (e.g., contexts/my_private_data and contexts/laws).

### 5. Configuration

Create a config.yaml file in the project's root directory with the following content:

```yaml
template: |
  You are a helpful and friendly AI assistant to answer questions.

  Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Please provide a response that contains 2 parts:
    1. short answer of the question (provide concise responses of less than 30 words)
    2. please build full answer using 3-5 sentences maximum and keep the answer as concise as possible 
    Please use language of question to build the answer.
    {context}
  Question: {question}

  Your response:

filename_pattern: "logs/%Y_%m_%d_%H_%M_%S.txt"

vectorstore:
  url: "http://localhost:9200"
  
llm:
  model: "llama3"  

contexts:
  data:
    my_private_data:
      folder_path: "contexts/my_private_data"
    laws:
      folder_path: "contexts/laws"      
  formats: ["pdf"]    
  worker_count: 4
```

### 6. Index Documents

Index documents from the contexts folder to the vector storage:

```bash
python index_docs.py
```

### 7. Create Multi-Output Device for Audio Input (for Calls)

If using the assistant during calls (e.g., Google Meet, Zoom, Slack), add a multi-output device to stream input audio into the assistant.

Donwload and install [Blackhole](https://github.com/ExistentialAudio/BlackHole).

Use "Audio MIDI Setup" to add a multi-output device with BlackHole and other audio outputs (MacOS only).

Set the multi-output device as the default speaker.

### 8. Running the Program

Start the assistant by executing the main script:

```bash
python assistant.py
```

Select the input type when prompted:

```bash
Available inputs:
1: audio
2: text
Please select input by number: 
```

### 9. Generating Responses (Text Input)

Select the context from the config:

```bash
Available contexts:
1: my_private_data
2: laws
Please select context by number: 
```

Input your question and press Enter. The assistant will generate a response and log information to both the console and a file.

### 10. Generating Responses (Audio Input)

Select the context from the config:

```bash
Available contexts:
1: my_private_data
2: laws
Please select context by number: 
```

Select the available audio device:

```bash
Available audio devices:
  0 BlackHole 2ch, Core Audio (2 in, 2 out)
> 1 MacBook Pro Microphone, Core Audio (1 in, 0 out)
< 2 MacBook Pro Speakers, Core Audio (0 in, 2 out)
  3 My iPhone Microphone, Core Audio (1 in, 0 out)
  4 Multi-Output Device, Core Audio (0 in, 2 out)
Please select audio device by number: 
```

Follow the instructions to start and stop recording. The assistant will transcribe the audio, generate a response, and log information to both the console and a file.

## Extension

### Logging

The program can log information to files named "logs/YYYY_MM_DD_HH_SS.txt", controlled via the filename_pattern field in the config.yaml file.

### Customization

- **Templates:** Modify the conversation template in config.yaml to suit different interview styles or scenarios.

- **Language Models:** Swap the Ollama model for other language models, adapting the assistant to specific contexts.

## Contributing

Contributions are welcome! For feedback or enhancements, please feel free to open a pull request or an issue.

## License

This project is released under the MIT License.
