"""Client for interacting with Google Cloud Firestore."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Callable

from absl import logging
from google.cloud import firestore
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from google.cloud.firestore_v1.vector import Vector

if TYPE_CHECKING:
    from google.cloud.firestore_v1.base_query import BaseQuery
    from google.cloud.firestore_v1.document import DocumentReference


class FirestoreClient:
    """Client to interact with a database collection in Firestore.

    Example Usage:
        project_id = "your-project-id"  # Replace with your project ID
        client = FirestoreClient(project_id)
        ref = client.create(data={"media_uri": "gs://path/to/file.jpg"})
        client.update(ref.id, data={"embedding": [0.231, 0.123]})
        results = client.query(
            query_fun=lambda q: q.where("media_uri", "==", "gs://path/to/file.jpg"),
        )
        client.delete(ref.id)
    """

    def __init__(self) -> None:
        """Instantiates the FirestoreClient."""
        self.project_id = os.environ.get("PROJECT_ID")
        self.database_name = os.environ.get("DB_NAME")
        self.db = firestore.Client(project=self.project_id, database=self.database_name)
        self.collection_name = "image-metadata"

    def create(
        self,
        document_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> DocumentReference:
        """Creates a new document in the specified collection.

        Args:
            collection_name: The name of the collection.
            document_id (optional): The ID of the document.
                If None, Firestore will generate one.
            data: A dictionary containing the document data.

        Returns:
            The DocumentReference of the created document.

        Raises:
            Exception: If the operation fails.
        """
        try:
            if document_id:
                doc_ref = self.db.collection(self.collection_name).document(document_id)
                doc_ref.set(data)
            else:
                _, doc_ref = self.db.collection(self.collection_name).add(
                    data,
                )
            return doc_ref
        except Exception as e:
            logging.exception(f"Error creating document: {e}")
            raise

    def update(
        self,
        document_id: str,
        data: dict[str, Any],
    ) -> None:
        """Updates an existing document.

        Args:
            document_id: The ID of the document to update.
            data: A dictionary containing the fields to update and their new values.

        Raises:
            google.cloud.exceptions.NotFound: If the document does not exist.
            Other exceptions if the update fails.
        """
        try:
            doc_ref = self.db.collection(self.collection_name).document(document_id)
            doc_ref.update(data)
        except Exception as e:
            logging.exception("Error updating document: %s", e)
            raise

    def delete(self, document_id: str) -> None:
        """Deletes a document.

        Args:
            document_id: The ID of the document to delete.

        Raises:
            google.cloud.exceptions.NotFound: If the document does not exist.
            Other exceptions if the delete fails.
        """
        try:
            doc_ref = self.db.collection(self.collection_name).document(document_id)
            doc_ref.delete()
        except Exception as e:
            logging.exception("Error deleting document: %s", e)
            raise

    def nn_search(
        self,
        embedding: list[float],
    ) -> list[dict[str, Any]]:
        """Runs a nearest neigbor search against image embeddings in the collection.

        Args:
            embedding: The embedding to search nearest neighbors for.
            min_similarity: (Optional) The mininum cosine similarity.

        Returns:
            A list of nearst neigbors and their distance.
        """
        vector_query = self.db.collection(self.collection_name).find_nearest(
            vector_field="image_embeddings",
            query_vector=Vector(embedding),
            distance_measure=DistanceMeasure.COSINE,
            limit=50,
            distance_result_field="vector_distance",
        )
        docs = vector_query.stream()
        results = []
        for doc in docs:
            result = doc.to_dict()
            logging.info("FirestoreClient: Got result: %s", result)
            # Remove embeddings from response, since they are
            # large and aren't used after ANN search.
            keys_to_remove = [
                key
                for key in result
                if key in ("image_embeddings", "prompt_embeddings")
            ]
            for key in keys_to_remove:
                del result[key]
            results.append(result)
        logging.info("FirestoreClient: Got results: %s", results)
        return sorted(results, key=lambda item: item["vector_distance"])

    def query(
        self,
        query_fun: Callable[[BaseQuery], BaseQuery],
    ) -> list[dict[str, Any]]:
        """Runs a query against the specified collection.

        Args:
            collection_name: The name of the collection.
            query_fun: A function that takes a Firestore query object and returns a modified query (e.g., with where clauses, order_by, etc.)

        Returns:
            A list of document dictionaries that match the query. Returns an empty list if no documents match or raises exception if query fails.
        """
        try:
            collection_ref = self.db.collection(self.collection_name)
            query = query_fun(collection_ref)
            docs = query.stream()
            results = [doc.to_dict() for doc in docs]
            return results
        except Exception as e:
            logging.exception("Error running query: %s", e)
            raise



