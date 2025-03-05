import streamlit as st
from groq import Groq

class GroqModel:
    def __init__(self):
        groq_api_key = st.secrets["secrets"]["GROQ_API_KEY"]
        if not groq_api_key:
            raise ValueError("Chave de API da Groq não encontrada.")

        # Configuração do cliente Groq
        self.groq_client = Groq(api_key=groq_api_key)

    def generate_response(self, prompt, temperature=0.7):
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",  # Modelo Groq a ser usado
                temperature=temperature  # Controle de temperatura para variação da resposta
            )

            return chat_completion.choices[0].message.content  # Retorna a resposta da Groq

        except Exception as e:
            return f"Erro ao chamar a Groq API: {str(e)}"