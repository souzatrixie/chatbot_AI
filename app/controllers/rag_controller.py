from app.models import embedding_model, rerank_model, llama_model
from db import database

class RAGController:
    def __init__(self):
        self.embedding_model = embedding_model.EmbeddingModel()
        self.rerank_model = rerank_model.RerankModel(database.get_all_documents())
        self.llama_model = llama_model.GroqModel()

    def get_response(self, query, temperature):
        query_embedding = self.embedding_model.get_embeddings([query])[0]
        relevant_documents = self.rerank_model.rerank(query)
        context = "\n".join(relevant_documents)

        # Prompt inicial com contexto
        prompt = f"""
        Você é um assistente pessoal de consulta da empresa TE Connectivity. 
        Responda a perguntas sobre produtos e serviços da empresa com base nas informações fornecidas.
        Use um tom formal e profissional. Se não souber a resposta, diga que não tem informações suficientes.

        Informações:
        {context}

        Pergunta: {query}
        Resposta:
        """

        response = self.llama_model.generate_response(prompt, temperature)

        # Prompt de reformulação para clareza
        reform_prompt = f"""
        Reformule a seguinte resposta para torná-la mais clara e concisa:

        Resposta: {response}
        Reformulação:
        """
        response = self.llama_model.generate_response(reform_prompt, temperature)

        # Prompt para evitar alucinações
        aluc_prompt = f"""
        Verifique se a seguinte resposta contém informações precisas e relevantes. 
        Se a resposta incluir informações irrelevantes ou fabricadas, corrija ou diga que não tem informações suficientes.

        Resposta: {response}
        Verificação:
        """
        verification = self.llama_model.generate_response(aluc_prompt, temperature)
        if "informações suficientes" in verification.lower():
            return "Não tenho informações suficientes para responder a essa pergunta."

        return response