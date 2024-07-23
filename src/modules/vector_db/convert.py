"""
Converts asset .jsonl to VectorDB object
Execute from command line.
"""

import argparse
import json
from pathlib import Path

import openai

from .vector_db import VectorDB


def main():
    # Get command line arguments
    parser = argparse.ArgumentParser(description="Generate vector embedding database from asset .jsonl files.")
    parser.add_argument("path", type=str, help="Path to asset file.")
    parser.add_argument("--openai-api-key", type=str, default=None, help="OpenAI API key.")
    args = parser.parse_args()

    openai.api_key = args.openai_api_key
    asset_path = Path(args.path)
    asset_name = asset_path.stem

    # Check asset exists
    if not asset_path.exists():
        raise FileNotFoundError(f"VectorDBAsset {asset_path} does not exist.")
    elif asset_path.suffix != ".jsonl":
        raise ValueError(f"VectorDBAsset {asset_path} must be a .jsonl file.")

    # Load documents from .jsonl
    documents = []
    with open(asset_path, "r") as f:
        for line in f:
            documents.append(json.loads(line))

    # Instantiate VectorDB with the list of documents
    # Note: VectorDB will automatically create embeddings using the openAI API
    db = VectorDB(documents,
                  key="description",
                  similarity_metric="cosine")

    # Save the VectorDB instance to a .pkl file
    db_path = f"{asset_path.parent}/{asset_name}.pickle.gz"
    db.save(db_path)
    print(f"VectorDB instance saved to {db_path}.")


if __name__ == "__main__":
    main()
