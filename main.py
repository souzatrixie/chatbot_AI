import streamlit as st
import random
import time
import json
from config import settings
from app.controllers import query_controller

settings = settings.settings

st.set_page_config(page_title="Chat TE", page_icon="", layout="wide")

# Carregar CSS personalizado
with open(settings["paths"]["style_path"], "r") as f:
    custom_css = f.read()
st.markdown(f'<style>{custom_css}</style>', unsafe_allow_html=True)

with st.sidebar:
    st.image(settings["paths"]["logo_path"], use_container_width=True)
    st.header("Controles")
    temperature = st.slider("Temperatura do modelo", 0.0, 1.0, 0.7, 0.1)

    history_json = json.dumps(st.session_state.get("messages", []), indent=4)
    st.download_button("Baixar Histórico JSON", data=history_json, file_name="chat_history.json", mime="application/json")
    history_txt = "\n".join([f'{msg["role"]}: {msg["content"]}' for msg in st.session_state.get("messages", [])])
    st.download_button("Baixar Histórico TXT", data=history_txt, file_name="chat_history.txt", mime="text/plain")
    if st.button("Limpar histórico"):
        st.session_state.messages = []
        st.success("Histórico desativado!")

    # Adicionar botão para interromper a resposta
    if "stop_response" not in st.session_state:
        st.session_state.stop_response = False
    if st.button("Parar Resposta"):
        st.session_state.stop_response = True

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Eu sou MAITE, sua assistente de IA da TE Connectivity. Como posso te ajudar hoje?"}]

# Exibir histórico inline
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.text_input("Digite sua mensagem...", key="chat_input")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Personalizar a pergunta para incluir identidade da IA e informações da empresa
        extended_prompt = f"Você é MAITE, um assistente de IA desenvolvido para responder sobre a TE Connectivity. {prompt}"
        assistant_response = query_controller.generate_response(extended_prompt, temperature)
        
        for chunk in assistant_response.split():
            if st.session_state.stop_response:
                break
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.stop_response = False  # Resetar o estado após a resposta

if len(st.session_state.messages) > 1:
    if st.button("Regenerar última resposta"):
        last_user_message = next(msg["content"] for msg in reversed(st.session_state.messages) if msg["role"] == "user")
        st.session_state.messages.pop()
        st.session_state.messages.append({"role": "user", "content": last_user_message})
        st.rerun()
