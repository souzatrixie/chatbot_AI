from rank_bm25 import BM25Okapi

class RerankModel:
    def __init__(self, corpus):
        self.corpus = corpus
        self.bm25 = BM25Okapi([text.split() for text in corpus])

    def rerank(self, query, top_n=5):
        query_tokens = query.split()
        doc_scores = self.bm25.get_scores(query_tokens)
        top_docs = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:top_n]
        return [self.corpus[i] for i in top_docs]