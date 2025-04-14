import streamlit as st
from torch import cosine_similarity
import torch
from app.models import embedding_model
from db import database
from app.models.llama_model import GroqModel
import tiktoken
from db.database import fetch_documents_from_table
import pandas as pd


class RAGController:
    def __init__(self):
        self.embedding_model = embedding_model.EmbeddingModel()
        self.documents = database.get_all_documents()
        self.groq_model = GroqModel()
        self.max_tokens = 4096
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text):
        """Count the number of tokens in a text."""
        return len(self.tokenizer.encode(text))

    def get_relevant_context(self, query):
        """Fetch relevant context for the query."""
        try:
            if "dfmea" in query.lower():
                dfmea_info = (
                    "DFMEA (Design Failure Mode and Effects Analysis) é uma metodologia sistemática "
                    "usada para identificar modos de falha potenciais em um design, avaliar seus efeitos "
                    "e priorizar ações para mitigar riscos. O processo inclui:\n"
                    "1. Identificar funções do produto ou sistema.\n"
                    "2. Determinar modos de falha potenciais.\n"
                    "3. Avaliar os efeitos de cada falha.\n"
                    "4. Identificar causas das falhas.\n"
                    "5. Avaliar severidade, ocorrência e detecção.\n"
                    "6. Calcular o RPN (Número de Prioridade de Risco).\n"
                    "7. Implementar ações para reduzir riscos.\n"
                    "DFMEA é amplamente utilizado em indústrias para melhorar a confiabilidade e segurança do produto."
                )
                dfmea_documents = fetch_documents_from_table("failures", limit=100)
    
                # Reclassificar documentos
                ranked_documents = self.rerank_documents(query, dfmea_documents, top_k=10)
    
                # Extrair o texto relevante dos documentos reclassificados
                dfmea_context = " ".join(
                    doc.get("content", "") for doc in ranked_documents
                )
    
                return f"{dfmea_info}\n\nDados relevantes do banco de dados:\n{dfmea_context}"
            else:
                relevant_docs = [
                    doc for doc in self.documents if any(word in doc for word in query.lower().split())
                ]
                ranked_documents = self.rerank_documents(query, relevant_docs, top_k=5)
                return "\n".join(doc.get("content", "") for doc in ranked_documents)
        except Exception as e:
            print(f"Error fetching context: {str(e)}")
            return "An error occurred while fetching relevant context. Please try again."

    def get_response(self, query, temperature, language):
        """Generate a response based on the relevant context."""
        try:
            context = self.get_relevant_context(query)

            # Define prompts based on the language
            prompts = {
                "en": (
                    "You are MAITE, the AI assistant of TE Connectivity, a global leader in industrial technology, "
                    "specializing in the design and manufacturing of electronic and electrical components.\n"
                    "Interaction guidelines:\n"
                    "1. Respond in a clear, concise, and professional tone.\n"
                    "2. Avoid overly formal responses; be direct.\n"
                    "3. If the query relates to DFMEA, provide relevant details or suggest further reading.\n"
                    "4. If unsure, indicate insufficient information and suggest alternatives.\n"
                    f"Context:\n{context}\n\nQuestion: {query}\nResponse:"
                ),
                "pt": (
                    "Você é MAITE, a assistente de IA da TE Connectivity, uma líder global em tecnologia industrial, "
                    "especializada no design e fabricação de componentes eletrônicos e elétricos.\n"
                    "Diretrizes para interação:\n"
                    "1. Responda de forma clara, concisa e profissional.\n"
                    "2. Evite respostas excessivamente formais; seja direta.\n"
                    "3. Se a consulta for sobre DFMEA, forneça detalhes relevantes ou sugira leituras adicionais.\n"
                    "4. Se não souber, informe e sugira alternativas.\n"
                    f"Contexto:\n{context}\n\nPergunta: {query}\nResposta:"
                ),
            }

            prompt = prompts.get(language, prompts["en"])
            response = self.groq_model.generate_response(prompt, temperature, language)
            return response.strip() or ("No information available." if language == "en" else "Sem informações disponíveis.")
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return "An error occurred while processing your question. Please try again." if language == "en" else "Ocorreu um erro ao processar sua pergunta. Por favor, tente novamente."

    def conduct_dfmea(self):
        """
        Conduz o processo de DFMEA com o usuário.
        """
        st.write("**Iniciando o processo de DFMEA...**")
        st.write(
            "O DFMEA (Design Failure Mode and Effects Analysis) é uma metodologia sistemática para identificar "
            "modos de falha potenciais em um design, avaliar seus efeitos e priorizar ações para mitigar riscos."
        )

        # Perguntas do DFMEA
        questions = [
            "Quais são os modos de falha potenciais?",
            "Quais são os efeitos de cada modo de falha?",
            "Quais são as causas de cada falha?",
            "Como cada falha pode ser detectada?",
            "Qual é a severidade de cada falha?",
            "Qual é a probabilidade de ocorrência de cada falha?",
            "Quão eficaz é a detecção de cada falha?",
            "Quais são as ações recomendadas para reduzir os riscos?"
        ]

        # Capturar respostas
        responses = {}
        for question in questions:
            response = st.text_input(question)
            if response:
                responses[question] = response

        # Exibir resumo
        if st.button("Finalizar DFMEA"):
            st.write("**Resumo do DFMEA:**")
            for question, response in responses.items():
                st.write(f"- **{question}**: {response}")

        import torch
    
    def rerank_documents(self, query, documents, top_k=5):
        """
        Reclassifica os documentos com base na relevância em relação à consulta.

        Args:
            query (str): A consulta do usuário.
            documents (list): Lista de documentos a serem reclassificados.
            top_k (int): Número de documentos mais relevantes a retornar.

        Returns:
            list: Lista de documentos reclassificados.
        """
        if not documents:
            return []

        # Obter embeddings da consulta
        query_embedding = self.embedding_model.get_embeddings([query])[0]

        # Obter embeddings dos documentos
        document_texts = [doc.get("content", "") for doc in documents]
        document_embeddings = self.embedding_model.get_embeddings(document_texts)

        # Converter embeddings para tensores
        query_tensor = torch.tensor(query_embedding).unsqueeze(0)  # Adiciona uma dimensão para o batch
        document_tensors = torch.tensor(document_embeddings)

        # Calcular similaridade de cosseno
        similarities = torch.nn.functional.cosine_similarity(query_tensor, document_tensors)

        # Combinar documentos com suas pontuações
        scored_documents = [
            {"document": doc, "score": score.item()}  # Converte o tensor para float
            for doc, score in zip(documents, similarities)
        ]

        # Ordenar documentos por pontuação (decrescente)
        ranked_documents = sorted(
            scored_documents, key=lambda x: x["score"], reverse=True
        )

        # Retornar os top_k documentos mais relevantes
        return [doc["document"] for doc in ranked_documents[:top_k]]