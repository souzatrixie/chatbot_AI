import streamlit as st
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login  # Para autenticação

class HuggingFaceModel:
    def __init__(self):
        model_name = "meta-llama/Llama-3.3-70B-Instruct"

        # Recupera o token do Hugging Face do arquivo secrets
        huggingface_token = st.secrets["huggingface"]["HF_API_TOKEN"]
        if not huggingface_token:
            raise ValueError("Token da Hugging Face não encontrado nos secrets.")

        # Faz login no Hugging Face usando o token
        login(token=huggingface_token)

        # Carrega o modelo e tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=True)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=True)

        # Cria a pipeline para geração de texto
        self.pipeline = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)

    def generate_response(self, prompt, temperature=0.7):
        try:
            response = self.pipeline(prompt, max_length=512, temperature=temperature, do_sample=True)
            return response[0]['generated_text']
        except Exception as e:
            return f"Erro ao chamar o modelo da Hugging Face: {str(e)}"
