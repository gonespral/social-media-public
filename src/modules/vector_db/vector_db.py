"""
Vector Database Module
Built on HyperDB (https://github.com/jdagdelen/hyperDB/tree/main)
"""

import gzip
import pickle
import json
import random

import numpy as np
import openai
from pathlib import Path

MAX_BATCH_SIZE = 2048  # OpenAI batch endpoint max size https://github.com/openai/openai-python/blob/main/openai


def _get_norm_vector(vector):
    if len(vector.shape) == 1:
        return vector / np.linalg.norm(vector)
    else:
        return vector / np.linalg.norm(vector, axis=1)[:, np.newaxis]


def _dot_product(vectors, query_vector):
    similarities = np.dot(vectors, query_vector.T)
    return similarities


def _cosine_similarity(vectors, query_vector):
    norm_vectors = _get_norm_vector(vectors)
    norm_query_vector = _get_norm_vector(query_vector)
    similarities = np.dot(norm_vectors, norm_query_vector.T)
    return similarities


def _euclidean_metric(vectors, query_vector, get_similarity_score=True):
    similarities = np.linalg.norm(vectors - query_vector, axis=1)
    if get_similarity_score:
        similarities = 1 / (1 + similarities)
    return similarities


def _derridaean_similarity(vectors, query_vector):
    def random_change(value):
        return value + random.uniform(-0.2, 0.2)

    similarities = _cosine_similarity(vectors, query_vector)
    derrida_similarities = np.vectorize(random_change)(similarities)
    return derrida_similarities


def _adams_similarity(vectors, query_vector):
    def adams_change(value):
        return 0.42

    similarities = _cosine_similarity(vectors, query_vector)
    adams_similarities = np.vectorize(adams_change)(similarities)
    return adams_similarities


def _hyper_SVM_ranking_algorithm_sort(vectors, query_vector, top_k=5, metric=_cosine_similarity):
    """HyperSVMRanking (Such Vector, Much Ranking) algorithm proposed by Andrej Karpathy (2023)
    https://arxiv.org/abs/2303.18231"""
    similarities = metric(vectors, query_vector)
    top_indices = np.argsort(similarities, axis=0)[-top_k:][::-1]
    return top_indices.flatten(), similarities[top_indices].flatten()


def _get_embedding(documents, key=None, model="text-embedding-ada-002"):
    """Default embedding function that uses OpenAI Embeddings."""
    if isinstance(documents, list):
        if isinstance(documents[0], dict):
            texts = []
            if isinstance(key, str):
                if "." in key:
                    key_chain = key.split(".")
                else:
                    key_chain = [key]
                for doc in documents:
                    for key in key_chain:
                        doc = doc[key]
                    texts.append(doc.replace("\n", " "))
            elif key is None:
                for doc in documents:
                    text = ", ".join([f"{key}: {value}" for key, value in doc.items()])
                    texts.append(text)
        elif isinstance(documents[0], str):
            texts = documents
    batches = [
        texts[i: i + MAX_BATCH_SIZE] for i in range(0, len(texts), MAX_BATCH_SIZE)
    ]
    embeddings = []
    for batch in batches:
        response = openai.Embedding.create(input=batch, model=model)
        embeddings.extend(np.array(item["embedding"]) for item in response["data"])
    return embeddings


class VectorDB:
    """
    Rewritten HyperDB object.
    """

    def __init__(
            self,
            openai_api_key,
            documents=None,
            vectors=None,
            key=None,
            embedding_function=None,
            similarity_metric="cosine",
    ):
        """
        VectorDB object.
        :param openai_api_key: OpenAI API key
        :param documents: Documents to add to the database
        :param vectors: Vectors to add to the database
        :param key: Key to use for embedding function
        :param embedding_function: Embedding function to use
        :param similarity_metric: Similarity metric to use
        """
        openai.api_key = openai_api_key
        documents = documents or []
        self.documents = []
        self.vectors = None
        self.metadata = None
        self.embedding_function = embedding_function or (
            lambda docs: _get_embedding(docs, key=key)
        )
        if vectors is not None:
            self.vectors = vectors
            self.documents = documents
        else:
            self.add_documents(documents)

        if similarity_metric.__contains__("dot"):
            self.similarity_metric = _dot_product
        elif similarity_metric.__contains__("cosine"):
            self.similarity_metric = _cosine_similarity
        elif similarity_metric.__contains__("euclidean"):
            self.similarity_metric = _euclidean_metric
        elif similarity_metric.__contains__("derrida"):
            self.similarity_metric = _derridaean_similarity
        elif similarity_metric.__contains__("adams"):
            self.similarity_metric = _adams_similarity
        else:
            raise Exception(
                "Similarity metric not supported. Please use either 'dot', 'cosine', 'euclidean', 'adams', "
                "or 'derrida'."
            )

    def __repr__(self):
        return f"VectorDB(documents={self.documents}, vectors={self.vectors}, similarity_metric={self.similarity_metric})"

    def dict(self, vectors=False):
        if vectors:
            return [
                {"document": document, "vector": vector.tolist(), "index": index}
                for index, (document, vector) in enumerate(
                    zip(self.documents, self.vectors)
                )
            ]
        return [
            {"document": document, "index": index}
            for index, document in enumerate(self.documents)
        ]

    def add(self, documents, vectors=None):
        if not isinstance(documents, list):
            return self.add_document(documents, vectors)
        self.add_documents(documents, vectors)

    def add_document(self, document: dict, vector=None):
        vector = (
            vector if vector is not None else self.embedding_function([document])[0]
        )
        if self.vectors is None:
            self.vectors = np.empty((0, len(vector)), dtype=np.float32)
        elif len(vector) != self.vectors.shape[1]:
            raise ValueError("All vectors must have the same length.")
        self.vectors = np.vstack([self.vectors, vector]).astype(np.float32)
        self.documents.append(document)

    def remove_document(self, index):
        self.vectors = np.delete(self.vectors, index, axis=0)
        self.documents.pop(index)

    def add_documents(self, documents, vectors=None):
        if not documents:
            return
        vectors = vectors or np.array(self.embedding_function(documents)).astype(
            np.float32
        )
        for vector, document in zip(vectors, documents):
            self.add_document(document, vector)

    def save(self, storage_file):
        data = {"vectors": self.vectors, "documents": self.documents}
        if storage_file.endswith(".gz"):
            with gzip.open(storage_file, "wb") as f:
                pickle.dump(data, f)
        else:
            with open(storage_file, "wb") as f:
                pickle.dump(data, f)

    def load(self, file_location):
        """
        Load a database from a .pickle.gz file.
        :param file_location: Accepts either a path to a .pickle.gz file or a directory containing a .pickle.gz file.
        :return:
        """
        # Check if path is a directory
        if Path(file_location).is_dir():
            file_location = f"{file_location}/{Path(file_location).stem}.pickle.gz"

        # Load the database
        if file_location.endswith(".gz"):
            with gzip.open(file_location, "rb") as f:
                data = pickle.load(f)
        else:
            with open(file_location, "rb") as f:
                data = pickle.load(f)
        self.vectors = data["vectors"].astype(np.float32)
        self.documents = data["documents"]

        # Check if metadata exists and load it
        metadata_path = Path(file_location).parent / "metadata.jsonl"
        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                self.metadata = json.load(f)

    def query(self, query_text, top_k=5, return_similarities=False, return_text_only=True) -> list:
        """
        Query the database.
        :param query_text: Query text.
        :param top_k: Number of results to return.
        :param return_similarities: Return the similarity scores.
        :param return_text_only: Return only the text.
        :return: List of the top k results.
        """
        query_vector = self.embedding_function([query_text])[0]
        ranked_results, similarities = _hyper_SVM_ranking_algorithm_sort(self.vectors, query_vector, top_k=top_k,
                                                                         metric=self.similarity_metric)
        if return_similarities:
            return list(
                zip([self.documents[index] for index in ranked_results], similarities)
            )
        docs = [self.documents[index] for index in ranked_results]
        if return_text_only:
            return [doc["text"] for doc in docs]
        return docs
