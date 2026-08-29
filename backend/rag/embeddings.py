# Arquivo: backend/rag/embeddings.py

from sentence_transformers import SentenceTransformer
from functools import lru_cache
from core.config import settings

@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Carrega e retorna o modelo de embedding SentenceTransformer.
    
    Usa lru_cache para garantir que o modelo, que pode ser grande e demorado
    para carregar, seja carregado na memória apenas uma vez (padrão Singleton).
    
    Returns:
        SentenceTransformer: A instância do modelo de embedding.
    """
    print(f"INFO: Carregando modelo de embedding: {settings.EMBEDDING_MODEL}...")
    # O modelo será baixado do Hugging Face na primeira vez que for executado
    # e armazenado em cache localmente.
    model = SentenceTransformer(settings.EMBEDDING_MODEL)
    print("INFO: Modelo de embedding carregado com sucesso.")
    return model

class EmbeddingGenerator:
    """
    Classe para gerar embeddings a partir de texto usando um modelo pré-carregado.
    """
    def __init__(self):
        """
        Inicializa o gerador, obtendo o modelo singleton.
        """
        self.model = get_embedding_model()

    def generate(self, text: str) -> list[float]:
        """
        Gera o embedding para um único pedaço de texto.

        Args:
            text (str): O texto a ser convertido em vetor.

        Returns:
            list[float]: O vetor de embedding.
        """
        # O método .encode() do SentenceTransformer faz a mágica de converter o texto.
        # tolist() converte o array numpy resultante em uma lista Python padrão.
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def generate_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Gera embeddings para um lote de textos de forma otimizada.
        É muito mais eficiente do que gerar um por um em um loop.

        Args:
            texts (list[str]): Uma lista de textos.

        Returns:
            list[list[float]]: Uma lista de vetores de embedding.
        """
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()