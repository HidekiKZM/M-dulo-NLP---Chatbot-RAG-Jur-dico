# Arquivo: backend/rag/classifier.py

import re

class QueryClassifier:
    """
    Classifica a pergunta do usuário para decidir se o pipeline de RAG deve ser acionado.
    """
    def __init__(self):
        # Listas de palavras-chave e padrões para cada categoria
        self.greetings = [
            "oi", "ola", "bom dia", "boa tarde", "boa noite", "tudo bem",
            "e aí", "eae", "opa", "salve"
        ]
        self.legal_triggers = [
            "art.", "artigo", "lei", "decreto", "constituição", "código", "cf",
            "cdc", "clt", "cpc", "cpp", "eca", "inciso", "parágrafo", "§",
            "o que diz a lei sobre", "qual o direito", "posso processar",
            "indenização", "usucapião", "habeas corpus", "jurisprudência"
        ]

    def classify(self, query: str) -> str:
        """
        Executa a classificação da pergunta.

        Args:
            query (str): A pergunta do usuário.

        Returns:
            str: Uma das categorias: 'rag_required', 'general_conversation', 'out_of_scope'.
        """
        # Normaliza a query para minúsculas para uma comparação sem distinção de caso
        lower_query = query.lower().strip()

        # 1. Verifica se é uma saudação simples
        if lower_query in self.greetings:
            return "general_conversation"

        # 2. Verifica se contém gatilhos jurídicos
        # Usamos 'any' para parar na primeira correspondência, o que é mais eficiente
        if any(trigger in lower_query for trigger in self.legal_triggers):
            return "rag_required"
        
        # 3. Verifica padrões mais complexos com expressões regulares (ex: Lei nº 12.345)
        if re.search(r'lei\s+nº?\s*\d+', lower_query):
            return "rag_required"

        # 4. Se não for nenhuma das anteriores, podemos considerar fora de escopo
        # ou, para uma experiência mais aberta, tratar como RAG para ver se algo é encontrado.
        # Para um bot estritamente jurídico, a melhor abordagem é ser conservador.
        # Se a pergunta for curta, provavelmente é conversa geral.
        if len(lower_query.split()) < 4:
            return "general_conversation"

        # 5. Por padrão, se a pergunta for mais elaborada, tentamos o RAG.
        return "rag_required"