from vectorstore import VectorStore
from config import load_config
from rich.console import Console
from document_collections import input_collection

console = Console()

if __name__ == "__main__":
    config = load_config()
    collection_name = input_collection(config, console)

    store = VectorStore(config, collection_name)
    store.add_documents()