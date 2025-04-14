import tiktoken
import streamlit as st
from groq import Groq


class GroqModel:
    def __init__(self):
        """Inicializa a conexão com a API da Groq."""
        try:
            groq_api_key = st.secrets["api_keys"].get("GROQ_API_KEY")
            if not groq_api_key:
                raise ValueError("Chave de API da Groq não encontrada. Certifique-se de configurar 'GROQ_API_KEY' em secrets.")
            
            self.groq_client = Groq(api_key=groq_api_key)  # Inicializa o cliente Groq com a chave de API
            self.tokenizer = tiktoken.get_encoding("cl100k_base")  # Define o tokenizador
            
        except KeyError as e:
            raise KeyError(f"Erro ao buscar configuração no Streamlit secrets: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Erro ao inicializar o GroqModel: {str(e)}")

    def count_tokens(self, text):
        """
        Conta o número de tokens no texto.

        Args:
            text (str): O texto para ser tokenizado.

        Returns:
            int: O número de tokens no texto.
        """
        try:
            return len(self.tokenizer.encode(text))
        except Exception as e:
            raise RuntimeError(f"Erro ao contar os tokens: {str(e)}")

    def generate_response(self, prompt, temperature=None, language="en"):
        """
        Gera uma resposta usando a API da Groq.
    
        Args:
            prompt (str): A mensagem do usuário.
            temperature (float): A temperatura para controlar a aleatoriedade da resposta.
            language (str): Idioma da resposta desejada.
    
        Returns:
            str: A resposta gerada pelo modelo.
    
        Raises:
            RuntimeError: Em caso de falha na API da Groq.
        """
        try:
            # Definir temperatura padrão com base no tipo de consulta
            if temperature is None:
                if "dfmea" in prompt.lower():
                    temperature = 0.3  # Respostas mais previsíveis para DFMEA
                else:
                    temperature = 0.7  # Valor padrão para outras consultas
    
            # Configura o modelo e realiza a chamada à API
            chat_completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",  # Modelo definido
                temperature=temperature
            )
            # Retorna o conteúdo gerado pela API
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Erro ao chamar a Groq API: {str(e)}"