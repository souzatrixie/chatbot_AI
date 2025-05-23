import streamlit as st
import json
import asyncio
from config import settings
from app.controllers.query_controller import generate_response
from app.controllers.rag_controller import RAGController
from streamlit_chat import message
from interface.login_page import render_login_page  # Importa a página de login
from pandas import ExcelFile
from db.reader import file_upload_manager

# Configurações globais
settings = settings.settings

# Configuração da página
st.set_page_config(
    page_title="MAITE",
    page_icon=settings["paths"]["logo_path"],
    layout="wide"
)

# Carregar CSS personalizado
def load_custom_css():
    try:
        with open(settings["paths"]["style_path"], "r") as f:
            custom_css = f.read()
        st.markdown(f'<style>{custom_css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("Arquivo de estilo não encontrado.")

# Sidebar com controles
def load_sidebar():
    with st.sidebar:
        st.image(settings["paths"]["logo_path"], use_container_width=True)
        st.header("Controles")

        # Controle deslizante para ajustar a temperatura
        st.session_state.temperature = st.slider(
            "Temperatura do modelo", 
            min_value=0.0, 
            max_value=1.0, 
            value=0.7, 
            step=0.1
        )
        
        # Exibir o valor atual da temperatura
        st.write(f"Temperatura atual: **{st.session_state.temperature:.1f}**")

        # Adicionar seletor de idioma
        language_option = st.radio("Escolha o idioma da resposta:", ["Português", "Inglês"])
        st.session_state.language = "pt" if language_option == "Português" else "en"
        
        # Upload de novos projetos
        if "uploader_key" not in st.session_state:
            st.session_state.uploader_key = 0
        
        project_file = st.file_uploader("Adicionar novos DFMEAs", ['xlsx', 'xls', 'ods'], key=st.session_state.uploader_key)
        if project_file is not None:
            upload_status = file_upload_manager(project_file)
            if upload_status == True:
                st.write("DFMEA inserido com sucesso")
            if upload_status is not None:
                st.session_state.uploader_key += 1
                st.rerun()
        
        # Se der errado, tente essa versão mais simples
        '''
        if "uploader_key" not in st.session_state:
            st.session_state.uploader_key = 0
        
        project_file = st.file_uploader("Adicionar novos DFMEAs", ['xlsx', 'xls', 'ods'], key=st.session_state.uploader_key)
        if project_file is not None:
            connection = get_db_connection()
            if connection is None:
                st.write("falha ao conectar com o banco de dados")
            else:
                insert_dfmeas_into_db(project_file, connection, overwrite_mode='full')
                st.session_state.uploader_key += 1
                st.rerun()
        '''

        # Botões de download do histórico
        history_json = json.dumps(st.session_state.get("messages", []), indent=4)
        st.download_button("Baixar Histórico JSON", data=history_json, file_name="chat_history.json", mime="application/json")

        history_txt = "\n".join([f'{msg["role"]}: {msg["content"]}' for msg in st.session_state.get("messages", [])])
        st.download_button("Baixar Histórico TXT", data=history_txt, file_name="chat_history.txt", mime="text/plain")

        # Botão para limpar histórico
        if st.button("Limpar histórico"):
            st.session_state.messages = []
            st.success("Histórico apagado!")

# Renderizar mensagens no chat
def render_message(msg, key, avatar_url=None, user_avatar=None):
    """
    Renderiza mensagens no chat com avatar e estilo personalizado.

    Args:
        msg (dict): Mensagem contendo o conteúdo e o papel (user ou assistant).
        key (str): Chave única para o componente Streamlit.
        avatar_url (str): URL do avatar do assistente.
        user_avatar (str): Caminho ou URL do avatar do usuário.
    """
    if msg["role"] == "user":
        # Usar o avatar do usuário definido em settings["paths"]["user_path"]
        user_avatar = user_avatar or settings["paths"]["user_path"]
        col1, col2 = st.columns([9, 1], gap="small")
        with col1:
            st.markdown(
                f"""
                <div style="background-color: #005a9c; color: white; padding: 10px; border-radius: 10px; text-align: right;">
                    {msg['content']}
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.image(user_avatar, width=64, use_container_width=False)
        
    elif msg["role"] == "assistant":
        col1, col2 = st.columns([1, 9], gap="small")
        with col1:
            if avatar_url:
                st.image(avatar_url, width=64, use_container_width=False)
        with col2:
            st.markdown(
                f"""
                <div style="background-color: #f0f0f0; color: black; padding: 10px; border-radius: 10px;">
                    {msg['content']}
                </div>
                """,
                unsafe_allow_html=True,
            )

# Chat Principal
async def display_chat():
    avatar_url = settings["paths"]["avatar_url"]
    user_avatar = settings["paths"]["user_path"]
    rag_controller = RAGController()  # Instância do controlador RAG

    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": (
                "Olá! Eu sou a MAITE, sua assistente de IA da TE Connectivity. "
                "Posso te ajudar com perguntas gerais ou conduzir um DFMEA. Para iniciar o DFMEA, digite 'iniciar DFMEA'."
            )
        }]

    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None

    # Mostrar histórico de mensagens
    for i, msg in enumerate(st.session_state.messages):
        render_message(msg, f"msg_{i}", avatar_url=avatar_url, user_avatar=user_avatar)

    # Capturar nova entrada do usuário
    prompt = st.chat_input("Digite sua mensagem...")

    # Se o usuário enviou algo, salva como pendente e faz rerun
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Verificar se o usuário quer iniciar o DFMEA
        if "iniciar DFMEA" in prompt.lower():
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Iniciando o processo de DFMEA. Por favor, responda às perguntas abaixo."
            })
            rag_controller.conduct_dfmea()  # Chama o método para conduzir o DFMEA
            return  

        st.session_state.pending_prompt = prompt
        st.rerun()

    # Processar mensagem pendente
    if st.session_state.pending_prompt:
        with st.spinner("MAITE está pensando..."):
            extended_prompt = f"Pergunta: {st.session_state.pending_prompt}\nResposta:"
            assistant_response = generate_response(
                extended_prompt,
                st.session_state.temperature,  # Passa a temperatura ajustada
                st.session_state.language
            )
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        st.session_state.pending_prompt = None
        st.rerun()

# Controle de autenticação
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    render_login_page()  # Redireciona para a página de login
else:
    # Início do app
    load_custom_css()
    load_sidebar()
    asyncio.run(display_chat())