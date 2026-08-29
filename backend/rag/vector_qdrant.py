# rag/vector_qdrant.py
import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

class QdrantManager:
    def __init__(self, collection_name: str | None = None):
        self.collection = collection_name or os.getenv("QDRANT_COLLECTION", "juribot_chunks")
        host = os.getenv("QDRANT_HOST", "qdrant")
        port = int(os.getenv("QDRANT_PORT", "6333"))
        grpc_port = int(os.getenv("QDRANT_GRPC_PORT", "6334"))
        prefer_grpc = os.getenv("QDRANT_USE_GRPC", "true").lower() == "true"
        timeout = float(os.getenv("QDRANT_TIMEOUT", "180"))

        self.client = QdrantClient(
            host=host,
            port=port,
            grpc_port=grpc_port,
            prefer_grpc=prefer_grpc,
            timeout=timeout,
        )

    def ensure_collection_exists(self, vector_size: int = 384):
        try:
            self.client.get_collection(self.collection)
            print(f"INFO: Coleção '{self.collection}' já existe.")
        except Exception:
            print(f"INFO: Coleção '{self.collection}' não encontrada. Criando...")
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            print("INFO: Coleção criada com sucesso.")

    def upsert_points(self, vectors, payloads):
        batch_size = int(os.getenv("QDRANT_BATCH_SIZE", "256"))
        parallel = int(os.getenv("QDRANT_PARALLEL", "2"))

        # ✅ IDs estáveis como UUID v5 (válidos para o Qdrant)
        ids = [
            str(uuid.uuid5(uuid.NAMESPACE_URL, f"{p.get('doc_id','id')}:{p.get('chunk_no', i)}"))
            for i, p in enumerate(payloads)
        ]

        self.client.upload_collection(
            collection_name=self.collection,
            vectors=vectors,
            payload=payloads,
            ids=ids,                 # <- agora são UUIDs válidos
            batch_size=batch_size,
            parallel=parallel,
            max_retries=3,
        )
        print("✅ Upload para Qdrant concluído.")
