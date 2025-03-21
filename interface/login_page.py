import streamlit as st
from streamlit import dialog
from config import settings

settings = settings.settings

st.set_page_config(page_title="Login", page_icon=settings["paths"]["logo_path"])

with open(settings["paths"]["style_path"], "r") as f:
   custom_css = f.read()
st.markdown(f'<style>{custom_css}</style>', unsafe_allow_html=True)

textos = {
    "Português": {
        "titulo": "Bem-vindo(a), eu sou a MAITE!",
        "instrucao": "Por favor, insira seu usuário e senha.",
        "usuario": "Usuário",
        "senha": "Senha",
        "botao_entrar": "Entrar",
        "lembrar_senha": "Lembrar senha",
        "esqueci_senha": "Esqueceu sua senha?",
        "cadastro": "Cadastre-se",
        "erro_login": "Por favor, insira seu usuário e senha.",
        "sucesso_login": "Login realizado com sucesso.",
        "alerta": "Alerta"
    },
    "English": {
        "titulo": "Welcome, I am MAITE!",
        "instrucao": "Please, enter your username and password.",
        "usuario": "Username",
        "senha": "Password",
        "botao_entrar": "Login",
        "lembrar_senha": "Remember password",
        "esqueci_senha": "Forgot your password?",
        "cadastro": "Sign up",
        "erro_login": "Please enter your username and password.",
        "sucesso_login": "Login successful.",
        "alerta": "Alert"
    },
}

with st.container(key="topbar"):
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

    with col1:
        st.image(settings["paths"]["logo_path"], width=190)
    
    with col2:
        st.markdown(f'<p style="margin-top:7px', unsafe_allow_html=True)
        idioma = st.selectbox("🌍 Selecione o idioma:", list(textos.keys()))

st.markdown("<br>", unsafe_allow_html=True)  # Adiciona uma quebra de linha
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

t = textos[idioma] 

@st.dialog(t['alerta'])

def validacao (usuario,senha):
    if usuario == '' or senha == '':
        st.error(t["erro_login"])
    else:
        st.success(t["sucesso_login"])

with st.form('sign_in'):
    st.title(t["titulo"])
    st.caption(t["instrucao"])
    st.divider()
    username = st.text_input(t["usuario"])
    password = st.text_input(t["senha"],
                         type='password')
    submit_btn = st.form_submit_button(label=t["botao_entrar"],
                                       type="primary",
                                       use_container_width=True)
    col1, col2, col3, col4 = st.columns (4)
    with col1:
        lembrar_senha = st.checkbox(t["lembrar_senha"])
    with col4:
        esqueci_senha = st.markdown(f'<p style="margin-top:7px"><a href="">{t["esqueci_senha"]}</a></p>', unsafe_allow_html=True)

if submit_btn:
    validacao(username, password)

st.button(label=t["cadastro"], type="secondary", use_container_width=False)
