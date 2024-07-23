"""
Convert asset files to json format for database insertion.
Execute from command line.
"""

import argparse
import json
from pathlib import Path

import pandas as pd


def main():
    # Get command line arguments
    parser = argparse.ArgumentParser(description="Convert asset files to json format for database insertion. "
                                                 "Example usage: "
                                                 "python jsonify.py ../assets/emoji/emoji.csv --text-col demojized "
                                                 "--desc-col description")
    parser.add_argument("path", type=str, help="Path to asset file.")
    parser.add_argument("--chunk-size", type=int, default=250, help="(.txt) Size of text chunks to upsert.")
    parser.add_argument("--chunk-overlap", type=int, default=50, help="(.txt) Size of overlap between text chunks.")
    parser.add_argument("--text-col", type=str, default=None, help="(.csv) Column to use as text.")
    parser.add_argument("--desc-col", type=str, default=None, help="(.csv) Column to use as description.")
    parser.add_argument("--asset-name", type=str, default=None, help="VectorDB name.")
    parser.add_argument("--asset-author", type=str, default=None, help="VectorDB author.")
    parser.add_argument("--asset-topic", type=str, default=None, help="VectorDB topic.")
    parser.add_argument("--asset-description", type=str, default=None, help="VectorDB description.")
    args = parser.parse_args()

    asset_path = Path(args.path)
    asset_extension = asset_path.suffix
    chunk_size = args.chunk_size
    chunk_overlap = args.chunk_overlap
    text_col = args.text_col
    desc_col = args.desc_col

    # Check asset exists
    if not asset_path.exists():
        raise FileNotFoundError(f"VectorDB {asset_path} does not exist.")
    else:
        print(f"VectorDB {asset_path} found.")

    # Check metadata provided
    if args.asset_name is None:
        print("Warning: VectorDB name not provided.")
    if args.asset_author is None:
        print("Warning: VectorDB author not provided.")
    if args.asset_topic is None:
        print("Warning: VectorDB topic not provided.")
    if args.asset_description is None:
        print("Warning: VectorDB description not provided.")

    # Convert asset to json format
    if asset_extension == ".txt":
        with open(asset_path, "r", encoding="utf-8") as f:
            asset_text = f.read()
        # Split into chunks of word count chunk_size
        texts = []
        asset_words = asset_text.split()
        for i in range(0, len(asset_words), chunk_size - chunk_overlap):
            texts.append(" ".join(asset_words[i:i + chunk_size]))
        descriptions = texts
    elif asset_extension == ".csv":
        asset_df = pd.read_csv(asset_path)
        if text_col is None:
            raise ValueError("Must specify text column for csv assets.")
        if desc_col is None:
            raise ValueError("Must specify description column for csv assets.")
        texts = asset_df[text_col].tolist()
        descriptions = asset_df[desc_col].tolist()
    else:
        raise ValueError(f"VectorDB extension {asset_extension} not supported.")

    # Write asset chunks to json file
    asset_json_path = asset_path.with_suffix(".jsonl")
    with open(asset_json_path, "w") as f:
        for text, description in zip(texts, descriptions):
            json.dump({"text": text, "description": description}, f)
            f.write("\n")
    print(f"VectorDB {asset_path} converted to {asset_json_path}.")

    # Create asset metadata json file
    asset_metadata = {
        "name": args.asset_name,
        "author": args.asset_author,
        "topic": args.asset_topic,
        "description": args.asset_description
    }

    asset_metadata_path = asset_path.parent / "metadata.jsonl"
    with open(asset_metadata_path, "w") as f:
        json.dump(asset_metadata, f)
    print(f"VectorDB metadata {asset_metadata_path} created.")


if __name__ == "__main__":
    main()
