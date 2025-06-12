import argparse
import os
from pathlib import Path
from uuid import uuid4

from . import load_file
from src.embeddings.embedder import Embedder
from src.vectorstore.chroma_manager import ChromaManager


def chunk_text(text: str, size: int = 1000, overlap: int = 200):
    """Yield consecutive chunks of ``size`` characters with ``overlap``."""

    step = size - overlap
    for start in range(0, len(text), step):
        yield text[start : start + size]


def index_directory(directory: str, persist_dir: str = "chroma_db"):
    """Walk ``directory`` and index all supported files into ChromaDB."""

    embedder = Embedder()
    store = ChromaManager(persist_dir=persist_dir)

    for root, _, files in os.walk(directory):
        for name in files:
            path = Path(root) / name
            try:
                content = load_file(str(path))
            except Exception as e:
                print(f"Skipped {path}: {e}")
                continue

            chunks = list(chunk_text(content))
            if not chunks:
                continue

            embeddings = embedder.encode(chunks)
            ids = [str(uuid4()) for _ in chunks]
            metadatas = [{"source": str(path), "chunk": i} for i in range(len(chunks))]

            store.add(
                ids=ids,
                texts=chunks,
                embeddings=embeddings,
                metadatas=metadatas,
            )


def cli() -> None:
    """Entry point for the command line."""

    parser = argparse.ArgumentParser(description="Index documents into ChromaDB")
    parser.add_argument("directory", help="Directory containing files to index")
    parser.add_argument(
        "--persist-dir",
        default="chroma_db",
        help="Destination directory for the Chroma database",
    )
    args = parser.parse_args()

    index_directory(args.directory, args.persist_dir)


if __name__ == "__main__":
    cli()
