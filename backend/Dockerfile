# backend/Dockerfile
# ==========================================
# Juribot - FastAPI + Qdrant + Gemini
# Dockerfile multi-stage (builder + runtime)
# ==========================================

# ---------- Estágio 1: Builder ----------
FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Dependências do sistema (para compilar libs Python)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Instala dependências Python (com cache em layer separado)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt


# ---------- Estágio 2: Runtime ----------
FROM python:3.11-slim AS runtime

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Dependências de runtime (OCR + PDF + TLS)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-por \
 && rm -rf /var/lib/apt/lists/*

# Copia as libs do builder (Python já com dependências)
COPY --from=builder /usr/local /usr/local

# Copia o código do backend
COPY . .

# Define usuário não-root (boa prática de segurança)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Porta exposta (FastAPI)
EXPOSE 8000

# CMD padrão (docker-compose pode sobrescrever)
CMD ["uvicorn", "app_main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
