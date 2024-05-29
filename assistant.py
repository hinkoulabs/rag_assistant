from rich.console import Console
from config import load_config
from llm import LllService
from input_formats.audio import Audio
from input_formats.text import Text
from utils import setup_logging, input_contexts, select_from_list

console = Console()
config = load_config()

def main():
    setup_logging(config["filename_pattern"])

    input_type = select_from_list(
        ["audio", "text"], 
        console,
        {
            "available": "[cyan]Available inputs:",
            "select": "[cyan]Please select input by number: "
        }
    )
    
    context = input_contexts(config, console)
    llm_service = LllService(config, context, verbose=False)

    service = Audio(console) if input_type == 'audio' else Text(console)

    service.action(llm_service)

if __name__ == "__main__":
    main()
