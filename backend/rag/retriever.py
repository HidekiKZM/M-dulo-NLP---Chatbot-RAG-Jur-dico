# Arquivo: backend/rag/retriever.py

from .embeddings import EmbeddingGenerator
from .vector_qdrant import QdrantManager
# A classe LexicalSearch ainda não será usada ativamente, mas já a importamos.
from .lexical import LexicalSearch

class HybridRetriever:
    """
    Orquestra a recuperação de informações usando diferentes estratégias.
    Por enquanto, implementaremos apenas a busca vetorial (semântica).
    """
    def __init__(self):
        """
        Inicializa os componentes necessários para a recuperação.
        """
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = QdrantManager()
        # A busca lexical será integrada em um passo futuro
        # self.lexical_search = LexicalSearch()

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Recebe uma consulta de texto e retorna os documentos mais relevantes.
        
        Args:
            query (str): A pergunta do usuário.
            top_k (int): O número de documentos a serem recuperados.
            
        Returns:
            list[dict]: Uma lista de dicionários, onde cada um representa um
                        documento relevante com seu score e metadados (payload).
        """
        print(f"DEBUG: Recebendo consulta para recuperação: '{query}'")

        # 1. Gerar o embedding para a consulta do usuário.
        # Este vetor representa o significado da pergunta em um espaço multidimensional.
        query_vector = self.embedding_generator.generate(query)
        print(f"DEBUG: Vetor da consulta gerado com sucesso (dimensão: {len(query_vector)}).")

        # 2. Realizar a busca semântica (vetorial) no Qdrant.
        # O Qdrant irá comparar o vetor da consulta com todos os vetores de
        # documentos armazenados e retornar os 'top_k' mais próximos (mais similares).
        semantic_results = self.vector_store.search(
            query_vector=query_vector,
            limit=top_k
        )
        print(f"DEBUG: Busca semântica retornou {len(semantic_results)} resultados.")

        # --- Lógica de Busca Híbrida (Passo Futuro) ---
        # Aqui é onde combinaríamos os resultados da busca lexical e semântica.
        # Por exemplo, poderíamos pegar o top 5 de cada, remover duplicatas
        # e usar um reranker para reordená-los.
        # Por enquanto, retornaremos apenas os resultados semânticos.
        
        final_results = semantic_results

        # 3. Formatar e retornar os resultados.
        # O formato já está bom, mas poderíamos adicionar mais lógica aqui se necessário.
        return final_results

    def get_context_from_results(self, results: list[dict]) -> str:
        """
        Formata os resultados da busca em uma única string de contexto
        para ser enviada ao LLM.
        
        Args:
            results (list[dict]): A lista de documentos recuperados.
        
        Returns:
            str: Uma string formatada contendo o conteúdo e os metadados
                 dos documentos, pronta para ser inserida no prompt.
        """
        context_parts = []
        for result in results:
            payload = result.get("payload", {})
            content = payload.get("content", "Conteúdo indisponível")
            source = payload.get("source", "Fonte desconhecida")
            page = payload.get("page", "N/A")

            # Formata cada pedaço de informação de forma clara para o LLM.
            part = f"--- INÍCIO DO DOCUMENTO ---\n"
            part += f"Fonte: {source}, Página: {page}\n"
            part += f"Conteúdo: {content}\n"
            part += f"--- FIM DO DOCUMENTO ---\n\n"
            context_parts.append(part)

        return "".join(context_parts)