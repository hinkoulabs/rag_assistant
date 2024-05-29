from vectorstore import VectorStore
from config import load_config
from rich.console import Console
from utils import input_contexts

console = Console()

if __name__ == "__main__":
    config = load_config()
    context = input_contexts(config, console)

    store = VectorStore(config, context)
    store.add_documents()