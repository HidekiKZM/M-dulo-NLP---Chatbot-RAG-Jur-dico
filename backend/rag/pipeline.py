# Arquivo: backend/rag/pipeline.py

from .classifier import QueryClassifier
from .retriever import HybridRetriever
from .generator_gemini import GeminiGenerator

class RAGPipeline:
    """
    Orquestra o pipeline completo de Retrieval-Augmented Generation.
    """
    def __init__(self):
        """
        Inicializa todos os componentes do pipeline.
        """
        print("INFO: Inicializando o Pipeline de RAG...")
        self.classifier = QueryClassifier()
        self.retriever = HybridRetriever()
        self.generator = GeminiGenerator()
        print("INFO: Pipeline de RAG inicializado com sucesso.")

    def run(self, query: str, stream: bool = False):
        """
        Executa o pipeline completo para uma dada consulta.

        Args:
            query (str): A pergunta do usuário.
            stream (bool): Flag para ativar a resposta em modo streaming.

        Returns:
            dict or generator: Um dicionário com a resposta final ou um gerador
                               de chunks de resposta em modo streaming.
        """
        # 1. Classificar a consulta do usuário
        classification = self.classifier.classify(query)
        print(f"DEBUG: Classificação da consulta: {classification}")

        context = ""
        retrieved_docs = []
        rag_used = False

        # 2. Se necessário, executar o passo de recuperação (Retrieval)
        if classification == "rag_required":
            rag_used = True
            # a. Recupera os documentos relevantes
            retrieved_docs = self.retriever.retrieve(query)
            
            if retrieved_docs:
                # b. Formata os documentos em uma string de contexto
                context = self.retriever.get_context_from_results(retrieved_docs)
                print(f"DEBUG: Contexto gerado a partir de {len(retrieved_docs)} documentos.")
            else:
                print("DEBUG: Nenhum documento relevante encontrado na base de dados.")
        
        # 3. Gerar a resposta usando o LLM
        response_data = self.generator.generate_response(
            question=query,
            context=context,
            stream=stream
        )

        # 4. Empacotar a resposta final
        if stream:
            # Em modo streaming, retornamos um gerador que produz os dados
            def stream_wrapper():
                # O primeiro chunk contém os metadados
                yield {
                    "rag_used": rag_used,
                    "citations": [doc.get("payload", {}) for doc in retrieved_docs],
                    "answer_chunk": "" # O primeiro chunk não tem texto
                }
                # Os chunks seguintes contêm o texto da resposta
                for chunk in response_data:
                    yield {"answer_chunk": chunk}
            
            return stream_wrapper()
        else:
            # Em modo não-streaming, retornamos um dicionário completo
            return {
                "answer": response_data,
                "rag_used": rag_used,
                "citations": [doc.get("payload", {}) for doc in retrieved_docs]
            }