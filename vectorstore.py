from langchain_elasticsearch import ElasticsearchStore
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.document_loaders import PyPDFLoader
import sys
import os
from multiprocessing import Pool
from glob import glob
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

embedding = GPT4AllEmbeddings()

class SuppressStdout:
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr

class VectorStore:
    def __init__(self, config) -> None:
        self.config = config
        self.vectorstore_config = config["vectorstore"]
        self.documents_config = config["documents"]

    def as_retriever(self):
        return ElasticsearchStore(
            es_url=self.vectorstore_config["url"],
            index_name=self.vectorstore_config["index_name"],
            embedding=embedding
        ).as_retriever()

    def add_documents(self) -> None:
        # Get list of files from the specified folder
        document_path = self.documents_config["folder_path"]
        document_formats = self.documents_config.get("formats", ["pdf"])
        
        # Collect files with the specified formats
        document_files = []
        for format in document_formats:
            document_files.extend(glob(f"{document_path}/*.{format}"))

        if not document_files:
            print("No documents found to index.")
            return

        # Prepare for multiprocessing with progress tracking
        worker_count = self.documents_config.get("worker_count", 4)
        
        with Progress(
            TextColumn("[progress.description]{task.description}"), 
            BarColumn(), 
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), 
            TimeElapsedColumn(), 
            expand=True,
        ) as progress:

            task = progress.add_task("Processing files", total=len(document_files))

            # Handling progress updates separately
            with Pool(worker_count) as pool:
                pool.starmap(process_file, [(file, self.vectorstore_config) for file in document_files])

            # Manually advancing progress bar after processing
            for _ in range(len(document_files)):
                progress.update(task, advance=1)

def process_file(document_path: str, vectorstore_config: dict) -> None:
    """Standalone function to handle document processing and indexing."""
    loader = PyPDFLoader(document_path)
    documents = loader.load()

    valid_documents = [doc for doc in documents if doc.page_content]  # Filtering out empty content

    if not valid_documents:
        print(f"No valid content found in document: {document_path}")
        return

    with SuppressStdout():
        db = ElasticsearchStore.from_documents(
            valid_documents, 
            embedding, 
            es_url=vectorstore_config["url"],
            index_name=vectorstore_config["index_name"]
        )

        db.client.indices.refresh(index=vectorstore_config["index_name"])