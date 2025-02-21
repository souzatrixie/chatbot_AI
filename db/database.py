from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://user:password@localhost:3306/database_name")

def insert_document(title, content):
    with engine.connect() as conn:
        conn.execute(f"INSERT INTO documents (title, content) VALUES ('{title}', '{content}')")

def get_document_by_id(doc_id):
    with engine.connect() as conn:
        result = conn.execute(f"SELECT * FROM documents WHERE id = {doc_id}")
        return result.fetchone()
