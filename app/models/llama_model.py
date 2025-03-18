import tiktoken
import streamlit as st
from groq import Groq

class GroqModel:
    def __init__(self):
        groq_api_key = st.secrets["api_keys"]["GROQ_API_KEY"]
        if not groq_api_key:
            raise ValueError("Chave de API da Groq não encontrada.")

        self.groq_client = Groq(api_key=groq_api_key)
        self.tokenizer = tiktoken.get_encoding("cl100k_base")  

    def count_tokens(self, text):
        """Conta o número de tokens no texto."""
        return len(self.tokenizer.encode(text))

    def generate_response(self, prompt, temperature=0.7):
        """Envia o prompt ao modelo Groq e retorna a resposta."""
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=temperature
            )

            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            return f"Erro ao chamar a Groq API: {str(e)}"
