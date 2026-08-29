# backend/api/routes_classify.py
from __future__ import annotations
from typing import Dict, List
import re
import math

from fastapi import APIRouter
from pydantic import BaseModel

# ---------------------------
# Configuração do Router
# ---------------------------
router = APIRouter(prefix="/classify", tags=["nlp"])

# ---------------------------
# Labels e Padrões
# ---------------------------
LABELS: List[str] = [
    "Consulta Legal Factual",
    "Jurisprudência/Precedentes",
    "Conceitual/Teoria",
    "Redação/Modelo",
    "Procedimental/Prática Forense",
    "Metaperguntas/Sistema",
    "Opinião/Explicação Geral",
]

KEYWORDS = {
    "Consulta Legal Factual": r"\b(art\.?|§|lei\s*n[ºo]|cpc|clt|prazo|compet[eê]ncia|caput|inciso|al[ií]nea)\b",
    "Jurisprudência/Precedentes": r"\b(s[úu]mula|ac[óo]rd[ãa]o|precedente|tese|tema|stj|stf|tj)\b",
    "Conceitual/Teoria": r"\b(defini[çc][ãa]o|conceito|natureza jur[ií]dica|esp[eé]cie)\b",
    "Redação/Modelo": r"\b(modelo|minuta|peti[cç][ãa]o|pe[cç]a|t[êe]mplate|fundamentar|argumentar)\b",
    "Procedimental/Prática Forense": r"\b(e-proc|pje|custas|protocolo|guia|distribui[cç][ãa]o|prazo no sistema)\b",
    "Metaperguntas/Sistema": r"\b(como usar|limite|privacidade|dados|pol[ií]tica|vers[aã]o|lat[êe]ncia)\b",
    "Opinião/Explicação Geral": r"\b(ach[ao]|opini[aã]o|explique|resuma|comente)\b",
}

# ---------------------------
# Modelos de Entrada/Saída
# ---------------------------
class ClassifyIn(BaseModel):
    text: str


class ClassifyOut(BaseModel):
    label: str
    confidence: float
    scores: Dict[str, float]


# ---------------------------
# Endpoint principal
# ---------------------------
@router.post("/", response_model=ClassifyOut)
def classify(in_: ClassifyIn) -> ClassifyOut:
    txt = in_.text.lower()
    scores: Dict[str, float] = {label: 0.0 for label in LABELS}

    # 1) Regras por regex (0/1)
    for label, pattern in KEYWORDS.items():
        if re.search(pattern, txt):
            scores[label] += 1.0

    # 2) Sinais gerais (ajustes heurísticos)
    if len(txt) > 160:
        # Textos longos frequentemente pedem modelo/redação
        scores["Redação/Modelo"] += 0.2

    if any(k in txt for k in ["art.", "§", "lei n", "súmula", "acórdão", "precedente"]):
        scores["Consulta Legal Factual"] += 0.2

    # 3) Normalização simples → softmax aproximada
    exps = {k: math.exp(v) for k, v in scores.items()}
    z = sum(exps.values()) or 1.0
    probs = {k: exps[k] / z for k in scores}

    # 4) Escolha do rótulo
    label = max(probs, key=probs.get)
    confidence = float(probs[label])

    return ClassifyOut(label=label, confidence=confidence, scores=probs)
