import streamlit as st
import json
import asyncio
from config import settings
from app.controllers.query_controller import generate_response
from streamlit_chat import message

settings = settings.settings
# Configuração da página
st.set_page_config(page_title="MAITE", page_icon=settings["paths"]["logo_path"], layout="wide")

# Carregar CSS personalizado
try:
    with open(settings["paths"]["style_path"], "r") as f:
        custom_css = f.read()
    st.markdown(f'<style>{custom_css}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    st.error("Arquivo de estilo não encontrado.")

# Função para carregar a Sidebar
def load_sidebar():
    with st.sidebar:
        st.image(settings["paths"]["logo_path"], use_container_width=True)
        st.header("Controles")
        st.session_state.temperature = st.slider("Temperatura do modelo", 0.0, 1.0, 0.7, 0.1)

        history_json = json.dumps(st.session_state.get("messages", []), indent=4)
        st.download_button("Baixar Histórico JSON", data=history_json, file_name="chat_history.json", mime="application/json")

        history_txt = "\n".join([f'{msg["role"]}: {msg["content"]}' for msg in st.session_state.get("messages", [])])
        st.download_button("Baixar Histórico TXT", data=history_txt, file_name="chat_history.txt", mime="text/plain")
        
        if st.button("Limpar histórico"):
            st.session_state.messages = []
            st.success("Histórico apagado!")

# Função para renderizar mensagens
def render_message(msg, key, avatar_url=None):
    if msg["role"] == "user":
        message(msg["content"], is_user=True, key=key)
    elif msg["role"] == "assistant" and avatar_url:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <img src="{avatar_url}" style="width: 64px; height: 64px; border-radius: 50%;" />
                <div style="flex: 1; background-color: #f0f0f0; padding: 10px; border-radius: 10px;">
                    {msg['content']}
                </div>
            </div>
        """, unsafe_allow_html=True)

# Função para exibir o Chat
async def display_chat():
    avatar_url = settings["paths"]["avatar_url"]

    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = [{"role": "assistant", "content": "Olá! Eu sou a MAITE, sua assistente de IA da TE Connectivity. Como posso te ajudar hoje?"}]

    # Exibir as mensagens do histórico
    for i, msg in enumerate(st.session_state.messages):
        render_message(msg, f"hist_{i}", avatar_url=avatar_url)
        
    # Campo de entrada fixo no final da tela
    prompt = st.text_input("Digite sua mensagem...", key="chat_input")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        render_message({"role": "user", "content": prompt}, f"user_{len(st.session_state.messages) - 1}")

        with st.spinner("MAITE está pensando..."):
            extended_prompt = f"Pergunta: {prompt}\nResposta:"
            assistant_response = generate_response(extended_prompt, st.session_state.temperature)

            # Adicionar resposta do assistente ao estado da sessão
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            render_message({"role": "assistant", "content": assistant_response}, f"assistant_{len(st.session_state.messages) - 1}", avatar_url=avatar_url)

load_sidebar()
asyncio.run(display_chat())