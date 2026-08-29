# backend/tools/qdrant_check.py
"""
Verifica a métrica e dimensão da coleção do Qdrant.
Uso:
  - Dentro do container API:
      docker compose exec api python backend/tools/qdrant_check.py
  - No Windows (fora do Docker), se mapeou a porta 6333:
      set QDRANT_HOST=localhost
      python backend/tools/qdrant_check.py
"""
import os
from qdrant_client import QdrantClient

host = os.getenv("QDRANT_HOST", "qdrant")
port = int(os.getenv("QDRANT_PORT", "6333"))
collection = os.getenv("QDRANT_COLLECTION", "juribot_chunks")

c = QdrantClient(host=host, port=port)

try:
    info = c.get_collection(collection)
except Exception as e:
    print(f"[ERRO] Não foi possível obter a coleção '{collection}' em {host}:{port}.\n{e}")
    raise SystemExit(1)

metric = info.config.params.vectors.distance.value  # ex.: 'Distance.COSINE'
dim = info.config.params.vectors.size

print(f"Collection={collection} | metric={metric} | dim={dim}")
print("OK se metric=Distance.COSINE. Caso contrário, recrie a coleção com COSINE.")
