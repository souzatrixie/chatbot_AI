# IA Generativa com Streamlit, FAISS e Banco de Dados

## Descrição do Projeto

Este projeto implementa um sistema de IA generativa utilizando **Streamlit** para interface, **FAISS** para busca eficiente de documentos relevantes e **SQLAlchemy** para gerenciamento do banco de dados. A arquitetura segue o padrão **MVC (Model-View-Controller)** para melhor organização e manutenção do código.

## Estrutura do Projeto

```
chatbot_AI/
│-- app/
│   ├── controllers/  # Controladores que gerenciam a lógica de negócio
│   │   ├── __init__.py
│   │   ├── query_controller.py
│   ├── models/  # Modelos para manipulação de dados
│   │   ├── __init__.py
│   │   ├── query_model.py
│-- config/  # Configurações do projeto
│   ├── settings.py
│-- db/  # Gerenciamento do banco de dados
│   ├── database.py
│-- interface/  # Arquivos de interface
│   ├── style.css
│   ├── TE_logo.png
│-- tests/  # Testes unitários
│   ├── test_app.py
│-- .streamlit/  # Configurações do Streamlit
│   ├── config.toml
│-- main.py  # Arquivo principal da aplicação
│-- Dockerfile  # Configuração do Docker
│-- requirements.txt  # Dependências do projeto
│-- .gitignore  # Arquivos a serem ignorados pelo Git
│-- README.md  # Documentação do projeto
```

## Tecnologias Utilizadas

- **Python 3.9**
- **Streamlit** (Interface gráfica)
- **FAISS** (Pesquisa de similaridade)
- **Transformers (Hugging Face)** (Modelo de embeddings)
- **SQLAlchemy** (Gerenciamento do banco de dados)
- **Docker** (Ambiente isolado)

## Configuração e Execução

### 1. Instalar dependências

Se estiver rodando localmente, execute:

```bash
pip install -r requirements.txt
```

### 2. Criar e rodar o container Docker

```bash
docker build -t ai-generative-app .
docker run -p 8501:8501 ai-generative-app
```

Isso iniciará a aplicação no endereço `http://localhost:8501`

## Fluxo de Funcionamento

1. O usuário insere uma pergunta na interface Streamlit.
2. A pergunta é processada pelo [`QueryController`](app/controllers/query_controller.py), que chama o [`QueryModel`](app/models/query_model.py).
3. O modelo gera embeddings da pergunta e busca documentos relevantes no FAISS.
4. Os documentos são reclassificados e uma resposta é gerada.
5. A resposta é exibida na interface do usuário.

## Contribuição

Sinta-se à vontade para contribuir abrindo issues e pull requests. 🚀
