# ⚖️ Juribot — Assistente Jurídico com RAG e Busca Semântica

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20DB-red?logo=qdrant)
![Docker](https://img.shields.io/badge/Docker-Supported-blue?logo=docker)

Assistente jurídico inteligente baseado em **Busca Semântica** e **Geração Aumentada por Recuperação (RAG)**. O projeto integra técnicas de NLP e banco de dados vetorial para consultas contextualizadas em documentos jurídicos.

---

## 🛠️ Tecnologias e Ferramentas

| Componente | Tecnologia | Função no Sistema |
| :--- | :--- | :--- |
| **Framework Web** | FastAPI | Exposição da API RESTful para recebimento de consultas |
| **Embeddings** | Sentence Transformers | Vetorização e representação semântica dos textos |
| **Vector Database** | Qdrant DB | Armazenamento e busca por similaridade vetorial |
| **Pipeline RAG** | Python / LLM | Recuperação de contexto e geração de resposta fundamentada |

---

## 🏗️ Arquitetura do Sistema

```mermaid
graph TD
    A[👤 Usuário / Interface / API] -->|Envia consulta| B[⚡ FastAPI API]
    B -->|Processa texto| C[🧠 Sentence Transformers]
    C -->|Gera embeddings semânticos| D[(🗄️ Qdrant DB)]
    D -->|Realiza busca por similaridade| E[🔍 Gerador RAG]
    E -->|Recupera contexto & gera resposta| A
