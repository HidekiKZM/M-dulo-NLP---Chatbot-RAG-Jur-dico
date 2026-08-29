# backend/api/routers_chat.py
from __future__ import annotations

import os
import traceback
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

# Gemini (opcional)
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except Exception:
    HAS_GEMINI = False

# Import CORRETO para sua estrutura (services dentro de backend)
from services.router import RAGRouter, RouterConfig


router = APIRouter(prefix="/chat", tags=["chat"])


# -----------------------------
# Schemas
# -----------------------------
class ChatReq(BaseModel):
    question: str
    top_k: int = 6
    label_hint: Optional[str] = None  # sugestão do /classify


# -----------------------------
# Endpoints (/chat e /chat/)
# -----------------------------
@router.post("")     # aceita POST /chat
@router.post("/")    # e POST /chat/
def chat(req: ChatReq, request: Request):
    app = request.app

    # Lazy init (reaproveita entre requests)
    if not hasattr(app.state, "model"):
        app.state.model = SentenceTransformer(
            os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        )
    if not hasattr(app.state, "qdrant"):
        app.state.qdrant = QdrantClient(
            host=os.getenv("QDRANT_HOST", "qdrant"),
            port=int(os.getenv("QDRANT_PORT", "6333")),
            grpc_port=int(os.getenv("QDRANT_GRPC_PORT", "6334")),
            prefer_grpc=os.getenv("QDRANT_USE_GRPC", "true").lower() == "true",
            timeout=float(os.getenv("QDRANT_TIMEOUT", "180")),
        )
    if not hasattr(app.state, "rag_router"):
        app.state.rag_router = RAGRouter(
            model=app.state.model,
            qdrant=app.state.qdrant,
            config=RouterConfig(),  # <-- nome correto do parâmetro
        )

    model: SentenceTransformer = app.state.model
    qdrant: QdrantClient = app.state.qdrant
    rag_router: RAGRouter = app.state.rag_router

    collection = os.getenv("QDRANT_COLLECTION", "juribot_chunks")

    # 0) Decide modo (RAG vs No-RAG)
    decision = rag_router.decide(req.question, classified_label=req.label_hint)
    mode = decision.get("mode", "rag")

    # 1) Se modo = RAG → busca fontes primeiro
    sources: List[Dict[str, Any]] = []
    if mode == "rag":
        vec = model.encode(req.question).tolist()
        hits = qdrant.search(
            collection_name=collection,
            query_vector=vec,
            limit=req.top_k,
            with_payload=True,
        )
        sources = [
            {
                "score": float(getattr(h, "score", 0.0)),
                "title": (h.payload or {}).get("title"),
                "page": (h.payload or {}).get("page"),
                "uri": (h.payload or {}).get("uri"),
                "snippet": ((h.payload or {}).get("content") or "")[:400],
            }
            for h in (hits or [])
        ]

    # 2) Sem LLM configurada → devolve fontes (RAG) ou msg (no-rag)
    key = os.getenv("GEMINI_API_KEY", "")
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    if not HAS_GEMINI or not key:
        if mode == "rag":
            return {
                "answer": "LLM não configurada. Aqui estão as fontes mais relevantes.",
                "sources": sources,
                "routing": decision,
            }
        else:
            return {
                "answer": "LLM não configurada. Configure GEMINI_API_KEY para respostas diretas.",
                "sources": [],
                "routing": decision,
            }

    # 3) Geração com Gemini
    try:
        genai.configure(api_key=key)
        gmodel = genai.GenerativeModel(model_name)

        if mode == "rag":
            ctx = "\n\n".join(
                f"[{i+1}] {s.get('snippet','')}" for i, s in enumerate(sources)
            )
            prompt = (
                "Você é um assistente jurídico. Responda de forma objetiva e cite as fontes "
                "entre colchetes como [1], [2]… quando forem utilizadas.\n\n"
                f"FONTES:\n{ctx}\n\nPERGUNTA: {req.question}\n\nRESPOSTA:"
            )
        else:
            prompt = (
                "Você é um assistente jurídico. Responda de forma objetiva, baseada em conhecimento geral. "
                "Se necessário, sugira buscar fontes.\n\n"
                f"PERGUNTA: {req.question}\n\nRESPOSTA:"
            )

        resp = gmodel.generate_content(prompt)
        answer = (getattr(resp, "text", "") or "").strip() or (
            "Não consegui gerar resposta. "
            + ("Veja as fontes abaixo." if mode == "rag" else "Tente reformular a pergunta.")
        )

        return {
            "answer": answer,
            "sources": sources if mode == "rag" else [],
            "routing": decision,
        }

    except Exception as e:
        print("LLM error:", repr(e))
        traceback.print_exc()
        if mode == "rag":
            return {
                "answer": "Falha ao gerar com a LLM. Veja as fontes mais relevantes abaixo.",
                "sources": sources,
                "routing": decision,
            }
        return {
            "answer": "Falha ao gerar com a LLM e sem fontes (No-RAG). Tente novamente.",
            "sources": [],
            "routing": decision,
        }
