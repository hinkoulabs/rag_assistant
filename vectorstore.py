from langchain_elasticsearch import ElasticsearchStore
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.document_loaders import PDFMinerLoader
import sys
import os
from multiprocessing import Pool
from glob import glob
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.console import Console

# Global variables for embedding and console output
embedding = GPT4AllEmbeddings()
console = Console()

class VectorStore:
    def __init__(self, config: dict, context: str) -> None:
        self.config = config
        self.vectorstore_config = config["vectorstore"]
        self.documents_config = config["contexts"]
        self.context = context

    def as_retriever(self):
        return ElasticsearchStore(
            es_url=self.vectorstore_config["url"],
            index_name=self.context,
            embedding=embedding
        ).as_retriever()

    def add_documents(self) -> None:
        # Get list of files from the specified folder
        document_path = self.documents_config["data"][self.context]["folder_path"]
        document_formats = self.documents_config.get("formats", ["pdf"])

        # Collect files with the specified formats
        document_files = []
        for fmt in document_formats:
            document_files.extend(glob(f"{document_path}/*.{fmt}"))

        if not document_files:
            console.print("No documents found to index.")
            return

        worker_count = self.documents_config.get("worker_count", 4)

        # Progress tracking
        with Progress(
            TextColumn("[progress.description]{task.description}"), 
            BarColumn(), 
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), 
            TimeElapsedColumn(),
            expand=True,
        ) as progress:

            task = progress.add_task("Processing files", total=len(document_files))

            # Process documents concurrently with progress updates
            with Pool(worker_count) as pool:
                # Map document processing and track progress
                for document in pool.imap_unordered(process_file, [(file, self.vectorstore_config, self.context) for file in document_files]):
                    console.print(f"Document processed: {document}")
                    progress.update(task, advance=1)

def process_file(args):
    """Standalone function to handle document processing and indexing."""
    document_path, vectorstore_config, context = args
    # console.print(f"Processing document: {document_path}")

    loader = PDFMinerLoader(document_path)
    documents = loader.load_and_split()

    valid_documents = [doc for doc in documents if doc.page_content]  # Filtering out empty content

    if not valid_documents:
        console.print(f"No valid content found in document: {document_path}")
        return

    with SuppressStdout():
        db = ElasticsearchStore.from_documents(
            valid_documents, 
            embedding, 
            es_url=vectorstore_config["url"],
            index_name=context
        )

        db.client.indices.refresh(index=context)

    return document_path

class SuppressStdout:
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stdout
