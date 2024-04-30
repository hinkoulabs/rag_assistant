from vectorstore import VectorStore
from config import load_config

if __name__ == "__main__":
    config = load_config()
    store = VectorStore(config)
    store.add_documents()