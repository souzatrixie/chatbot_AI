from app.models.query_model import QueryModel
from app.views.response_view import display_response

class QueryController:
    def __init__(self):
        self.model = QueryModel()

    def process_query(self, question):
        response = self.model.get_response(question)
        return display_response(response)
