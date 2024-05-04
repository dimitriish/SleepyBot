import os.path

import faiss
import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer

from src.rag.faiss_index import FaissRag
faiss_instance = FaissRag()
query = "On which side i should sleep?"
response = faiss_instance.retrieve_documents(query)
print(response)
