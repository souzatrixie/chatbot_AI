from transformers import AutoTokenizer, AutoModel
import faiss
import numpy as np

class QueryModel:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.faiss_index = faiss.read_index("faiss_index_file")  # Supondo índice pré-carregado

    def get_response(self, question):
        inputs = self.tokenizer(question, return_tensors="pt", truncation=True, padding=True)
        outputs = self.model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()
        D, I = self.faiss_index.search(np.array([embedding]), k=5)
        return f"Documentos relevantes encontrados: {I}"
