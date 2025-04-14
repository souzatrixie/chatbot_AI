import streamlit as st
from config import settings

# Configurações globais
settings = settings.settings

def load_custom_css():
    """
    Carrega o arquivo CSS personalizado para estilizar a página.
    """
    try:
        with open(settings["paths"]["style_path"], "r") as f:
            custom_css = f.read()
        st.markdown(f'<style>{custom_css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("Custom CSS file not found.")

# Textos padrão em inglês
TEXTOS = {
    "titulo": "Welcome, I am MAITE!",
    "instrucao": "Please enter your username and password.",
    "usuario": "Username",
    "senha": "Password",
    "botao_entrar": "Login",
    "lembrar_senha": "Remember password",
    "esqueci_senha": "Forgot your password?",
    "cadastro": "Sign up",
    "erro_login": "Please enter your username and password.",
    "sucesso_login": "Login successful.",
}

def validar_login(usuario, senha):
    """
    Valida o login com base nas credenciais armazenadas no streamlit.secrets.

    Args:
        usuario (str): Nome de usuário fornecido pelo usuário.
        senha (str): Senha fornecida pelo usuário.

    Returns:
        bool: True se as credenciais forem válidas, False caso contrário.
    """
    valid_username = st.secrets["auth"]["username"]
    valid_password = st.secrets["auth"]["password"]

    return usuario == valid_username and senha == valid_password

def render_login_page():
    """
    Renderiza a página de login.
    """
    # Carregar CSS personalizado
    load_custom_css()

    # Container principal para o login
    with st.container():
        # Título com texto substituindo a logo
        st.markdown(
            f"""
            <div class="login-container">
                <h1 class="login-title">TE Connectivity</h1>
                <h2 class="login-title">{TEXTOS["titulo"]}</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Formulário de login
        with st.form('sign_in', clear_on_submit=True):
            st.markdown(
                f'<p class="login-instruction">{TEXTOS["instrucao"]}</p>',
                unsafe_allow_html=True,
            )
            st.divider()

            # Campos de entrada
            username = st.text_input(TEXTOS["usuario"], placeholder="Enter your username")
            password = st.text_input(TEXTOS["senha"], type='password', placeholder="Enter your password")

            # Botão de login
            submit_btn = st.form_submit_button(
                label=TEXTOS["botao_entrar"],
                type="primary",
                use_container_width=True
            )

            # Opções adicionais
            col1, col2 = st.columns([1, 1])
            with col1:
                lembrar_senha = st.checkbox(TEXTOS["lembrar_senha"])
            with col2:
                st.markdown(
                    f'<a href="#" class="forgot-password">{TEXTOS["esqueci_senha"]}</a>',
                    unsafe_allow_html=True,
                )

        # Validação do login
        if submit_btn:
            if username == "" or password == "":
                st.error(TEXTOS["erro_login"])
            elif validar_login(username, password):
                st.success(TEXTOS["sucesso_login"])
                st.session_state.authenticated = True
            else:
                st.error(TEXTOS["erro_login"])

        # Botão de cadastro
        st.markdown(
            f"""
            <div style="text-align: center; margin-top: 20px;">
                <button class="signup-button">{TEXTOS["cadastro"]}</button>
            </div>
            """,
            unsafe_allow_html=True,
        )