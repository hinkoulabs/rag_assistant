from rich.console import Console
from datetime import datetime
import logging

console = Console()

def setup_logging(filename_pattern):
    log_filename = datetime.now().strftime(filename_pattern)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(log_filename)]
    )

def input_contexts(config, console) -> str:
    return select_from_list(
        list(config["contexts"]["data"].keys()), 
        console,
        {
            "available": "[cyan]Available contexts:",
            "select": "[cyan]Please select context by number: "
        }
    )

def select_from_list(list, console, custom_messages=None) -> str:
    if custom_messages is None:
        custom_messages = {}
        
    default_messages = {
        "available": "[cyan]Available:",
        "select": "[cyan]Please select by number: ",
        "value_error": "Invalid selection. Please enter a valid number."
    }
    
    messages = {**default_messages, **custom_messages}

    console.print(messages["available"])
    
    for index, name in enumerate(list, start=1):
        console.print(f"[yellow]{index}: {name}")
        
    try:
        collection_index = int(console.input(messages["select"]))
        if not 1 <= collection_index <= len(list):
            raise ValueError
    except ValueError:
        raise Exception(messages["value_error"])
    
    return list[collection_index - 1]
