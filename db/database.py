import mysql.connector
import streamlit as st
from concurrent.futures import ThreadPoolExecutor

DB_CONFIG = {
    "host": st.secrets["mysql"]["host"],
    "user": st.secrets["mysql"]["user"],
    "password": st.secrets["mysql"]["password"],
    "database": st.secrets["mysql"]["name"]
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        return connection
    except Exception as e:
        print(f"Erro ao conectar ao banco: {str(e)}")
        return None

def fetch_documents_from_table(table_name, limit=100):
    connection = get_db_connection()
    if not connection:
        return []

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        documents = cursor.fetchall()
        
        if not documents:
            raise ValueError(f"Nenhum dado encontrado na tabela {table_name}.")
        
        return documents  
    except Exception as e:
        print(f"Erro ao buscar dados na tabela {table_name}: {str(e)}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_all_documents():
    tables = [
        "actions", "components", "dfmeas", "failures", "functions"
    ]
    
    all_documents = []
    with ThreadPoolExecutor() as executor:
        futures = {table: executor.submit(fetch_documents_from_table, table) for table in tables}
        for table, future in futures.items():
            try:
                documents = future.result()
                all_documents.extend(documents)
            except Exception as e:
                print(f"Erro ao buscar dados da tabela {table}: {str(e)}")

    return all_documents
