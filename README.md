🧩 Visão Geral

O Juribot é um assistente jurídico inteligente baseado em busca semântica e geração aumentada por recuperação (RAG).
Este projeto integra técnicas avançadas de Processamento de Linguagem Natural (NLP) com armazenamento vetorial para permitir consultas contextuais sobre documentos jurídicos, produzindo respostas precisas e fundamentadas.

O projeto foi desenvolvido no contexto da especialização em Inteligência Artificial, como parte do módulo de NLP (Natural Language Processing).

┌────────────────────────┐
│        Usuário         │
│   (interface ou API)   │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│       FastAPI API       │
│  - Recebe consultas     │
│  - Chama o módulo NLP   │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│  Sentence Transformers  │
│  - Gera embeddings sem. │
│  - Representa textos    │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│        Qdrant DB        │
│ - Armazena vetores      │
│ - Realiza busca semânt. │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│      Gerador RAG       │
│ - Recupera contexto     │
│ - Gera resposta final   │
└────────────────────────┘
