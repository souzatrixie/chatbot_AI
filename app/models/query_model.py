import random

def get_response(prompt, temperature):
    """
    Simula uma resposta de modelo com base na temperatura.

    Args:
        prompt (str): A mensagem do usuário.
        temperature (float): A temperatura para controlar a aleatoriedade da resposta.

    Returns:
        str: Uma resposta simulada.
    """
    responses = [
        "Olá! Como posso te ajudar hoje?",
        "Oi! Precisa de alguma coisa?",
        "Estou aqui para ajudar! O que deseja saber?",
        "Como posso te auxiliar hoje?",
        "Se precisar de algo, estou por aqui!"
    ]
    if temperature > 0.7:
        return random.choice(responses)
    else:
        return responses[0]  # Resposta mais previsível