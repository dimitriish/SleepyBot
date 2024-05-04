import os

import psycopg2
import torch
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
# Database connection parameters
conn_params = "dbname='postgres' user='postgres' host='localhost' password='0000'"


class FaissRag:
    def __init__(self, path_to_index="faiss.idx"):
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.conn_params = "dbname='postgres' user='postgres' host='localhost' password='0000'"
        if os.path.exists(path_to_index):
            self.faiss_index = faiss.read_index(path_to_index)
        documents = self.fetch_documents()
        embeddings = self.encode_documents(documents)
        self.faiss_index = self.create_faiss_index(embeddings)

    def fetch_documents(self):
        """ Fetches all documents from PostgreSQL for indexing """
        with psycopg2.connect(self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, content FROM documents")
                documents = cur.fetchall()
        return documents

    def encode_documents(self, documents):
        """ Encodes documents into embeddings using BERT """
        embeddings = []
        for _, content in documents:
            with torch.no_grad():
                embedding = self.model.encode(content)
                embeddings.append(embedding)
        return np.array(embeddings)

    @staticmethod
    def create_faiss_index(embeddings):
        """ Creates and saves a FAISS index from embeddings """
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)  # Flat index, L2 distance
        index.add(embeddings)  # Adding the embeddings to the index
        faiss.write_index(index, 'faiss.idx')
        return index

    def retrieve_documents(self, query, k=3):
        with psycopg2.connect(conn_params) as conn:
            # Query to vector
            query_vec = np.array(self.model.encode(query)).reshape(1, 384)
            # Searching in FAISS
            _, indices = self.faiss_index.search(query_vec, k)
            with conn.cursor() as cur:
                # Fetch documents by IDs retrieved from FAISS
                cur.execute("SELECT content FROM documents WHERE id = ANY(%s)", (list(map(int, indices[0])),))
                results = cur.fetchall()
        return [doc[0] for doc in results]
