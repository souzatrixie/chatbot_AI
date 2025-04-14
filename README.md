# IA Generativa com Streamlit e Banco de Dados

## Descrição do Projeto

Este projeto implementa um sistema de IA generativa utilizando **Streamlit** para interface, **Sentence Transformers** para geração de embeddings semânticos e **MySQL** para gerenciamento do banco de dados. A arquitetura segue o padrão **MVC (Model-View-Controller)** para melhor organização e manutenção do código.

## Estrutura do Projeto


```
# Estrutura do Projeto `chatbot_AI`

```plaintext
chatbot_AI/
│
├── app/                          # Lógica principal da aplicação
│   ├── controllers/              # Controladores que gerenciam a lógica de negócio
│   ├── models/                   # Modelos para manipulação de dados
│   ├── config/                   # Configurações do projeto
│   ├── db/                       # Gerenciamento do banco de dados
│   ├── interface/                # Arquivos de interface do usuário
│   ├── tests/                    # Testes unitários
│   ├── .streamlit/               # Configurações específicas do Streamlit
│
├── main.py                        # Arquivo principal da aplicação
├── Dockerfile                     # Configuração do Docker
├── docker-compose.yml             # Configuração do Docker Compose
├── requirements.txt               # Dependências do projeto
├── .gitignore                     # Arquivos a serem ignorados pelo Git
└── README.md                      # Documentação do projeto

```


## Tecnologias Utilizadas

- **Python 3.8+**: Linguagem de programação principal.
- **Streamlit**: Framework para criação de interfaces web interativas.
- **Sentence Transformers**: Biblioteca para geração de embeddings semânticos.
- **MySQL**: Banco de dados relacional para armazenamento de informações.
- **SQLAlchemy**: ORM (Object-Relational Mapping) para interação com o banco de dados.
- **Transformers (Hugging Face)**: Framework para modelos de linguagem avançados.
- **PyTorch**: Framework para cálculos numéricos e aprendizado profundo.
- **Docker**: Ferramenta para criar ambientes isolados e portáveis.
- **Streamlit Chat**: Componente para adicionar funcionalidades de chat na interface.
- **Tiktoken**: Biblioteca para tokenização eficiente.

## Configuração e Execução

### 1. Instalar dependências

Se estiver rodando localmente, execute:

```bash
pip install -r [requirements.txt](http://_vscodecontentref_/18)
```

### 2. Configurar o Banco de Dados

```bash
[mysql]
host = "localhost"
user = "root"
password = "sua_senha"
name = "dfmeas"
```

### Executar

Para rodar o projeto em um ambiente isolado, use o Docker:

```bash
docker-compose up --build
```

Isso iniciará a aplicação no endereço `http://localhost:8501`

Se preferir rodar localmente sem Docker, execute o seguinte comando

```bash
streamlit run main.py
```

## Fluxo de Processamento da Pergunta

1. O usuário digita a pergunta na interface do Streamlit.

2. O `QueryController` recebe a pergunta e chama o `RAGController`.

3. O `RAGController` é responsável por processar a pergunta e acionar o modelo de embeddings.

4. **Sentence Transformers** gera embeddings para a pergunta do usuário.

5. Os embeddings gerados são utilizados para realizar uma busca no banco de dados MySQL por documentos relevantes.

6. Os documentos retornados são reclassificados com base na **similaridade de cosseno** utilizando **PyTorch**.

7. O modelo **Groq - llama7b** (via API) é chamado para gerar uma resposta com base nos documentos encontrados.

8. A resposta gerada pelo modelo **Groq** é exibida na interface do usuário, completando o ciclo.

---

## Contribuição

Sinta-se à vontade para contribuir abrindo issues e pull requests.