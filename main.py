import streamlit as st
from app.controllers.query_controller import QueryController

st.title("IA Generativa - Pergunte algo!")

controller = QueryController()
question = st.text_input("Qual é a sua pergunta?")

if question:
    response = controller.process_query(question)
    st.write(response)
