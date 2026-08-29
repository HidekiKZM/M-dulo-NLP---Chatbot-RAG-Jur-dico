# backend/services/router.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class RouterConfig:
    metric: str = "cosine"
    k: int = 5
    min_score: float = 0.3


class RAGRouter:
    def __init__(self, model, qdrant, config: Optional[RouterConfig] = None):
        self.model = model
        self.qdrant = qdrant
        self.config = config or RouterConfig()

    def decide(self, question: str, classified_label: Optional[str] = None) -> Dict[str, Any]:
        """
        Decisão simples: por padrão usa RAG.
        Se vier dica de rótulo que pareça 'Metaperguntas/Sistema', opta por no-rag.
        (Você pode sofisticar depois.)
        """
        label = (classified_label or "").lower()
        if "metaperguntas" in label or "sistema" in label:
            return {"mode": "no_rag", "why": "label_hint"}
        # Heurística boba: perguntas muito curtas tendem a no-rag
        if len(question.strip()) < 12:
            return {"mode": "no_rag", "why": "short_query"}
        return {"mode": "rag", "why": "default"}

    def route(self, query: str) -> Dict[str, Any]:
        # Placeholder: aqui você decidiria BM25 vs Vetor etc.
        return {"strategy": "vector", "k": self.config.k, "query": query}
