from app.controllers.rag_controller import RAGController

rag_controller = RAGController()

def generate_response(prompt, temperature):
    """
    Gera uma resposta usando o modelo de consulta (RAG).

    Args:
        prompt (str): A mensagem do usuário.
        temperature (float): A temperatura para controlar a aleatoriedade da resposta.

    Returns:
        str: A resposta gerada pelo modelo.
    """
    
    return rag_controller.get_response(prompt, temperature)