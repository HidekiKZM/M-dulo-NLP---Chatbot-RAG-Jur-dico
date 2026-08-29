import os
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

COL = os.getenv("QDRANT_COLLECTION","juribot_chunks")
q = "prazo de arrependimento em compra online"

model = SentenceTransformer(os.getenv("EMBEDDING_MODEL","sentence-transformers/all-MiniLM-L6-v2"))
vec = model.encode(q).tolist()

client = QdrantClient(
    host=os.getenv("QDRANT_HOST","qdrant"),
    port=int(os.getenv("QDRANT_PORT","6333")),
    grpc_port=int(os.getenv("QDRANT_GRPC_PORT","6334")),
    prefer_grpc=True
)

hits = client.search(collection_name=COL, query_vector=vec, limit=5, with_payload=True)
for i, h in enumerate(hits, 1):
    print(i, round(h.score,4), h.payload.get("title"), h.payload.get("page"), (h.payload.get("uri") or "")[:80])
