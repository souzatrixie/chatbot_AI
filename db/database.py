import mysql.connector
import streamlit as st
from concurrent.futures import ThreadPoolExecutor

def get_db_connection():
    # Carregar as credenciais do Streamlit secrets
    db_config = st.secrets["myysql"]

    # Conectar ao banco de dados usando as credenciais do secrets.toml
    return mysql.connector.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["name"]
    )

def fetch_documents_from_table(table_name, limit=100):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
    documents = cursor.fetchall()
    cursor.close()
    connection.close()
    return [" ".join(str(value) for value in doc.values()) for doc in documents]

def get_all_documents():
    tables = [
        "actions", "components", "failures", "functions",
        "uscar_actions", "uscar_components", "uscar_failures",
        "uscar_functions", "uscar_requirements", "uscar_rpn"
    ]
    
    all_documents = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_documents_from_table, table) for table in tables]
        for future in futures:
            all_documents.extend(future.result())
    
    return all_documents