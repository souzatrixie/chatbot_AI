from app.models import embedding_model
from db import database
from app.models.llama_model import GroqModel
import tiktoken

class RAGController:
    def __init__(self):
        self.embedding_model = embedding_model.EmbeddingModel()
        self.documents = database.get_all_documents()
        self.groq_model = GroqModel()
        self.max_tokens = 4096
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text):
        """Conta o número de tokens em um texto."""
        return len(self.tokenizer.encode(text))

    def get_relevant_context(self, query):
        """Seleciona apenas os documentos mais relevantes para a consulta."""
        relevant_docs = []
        for doc in self.documents:
            if any(word in doc.lower() for word in query.lower().split()):
                relevant_docs.append(doc)
        
        return "\n".join(relevant_docs[:5])  # Usa apenas os 5 documentos mais relevantes

    def get_response(self, query, temperature=0.7):
        """Gera uma resposta baseada no contexto relevante e valida antes de exibir."""
        try:
            context = self.get_relevant_context(query)

            prompt = f"""
            Você é MAITE, o assistente pessoal de consulta da TE Connectivity, uma empresa global líder em tecnologia industrial especializada no design e fabricação de componentes eletrônicos e elétricos. Nossa missão é conectar e proteger o mundo, fornecendo soluções inovadoras que atendem a diversos setores, incluindo automotivo, industrial, comunicações, energia, aeroespacial e defesa.

            Diretrizes para interação:

            1. **Aprendizado Controlado**: Nossa IA permitirá um momento de aprendizado, mas será restrita a aprender somente assuntos pré-programados, garantindo um aprendizado restrito e limitado.
            2. **Resolução de Conflitos**: Em caso de conflito, nossa IA deve: Perguntar e Aprender, assegurando respostas precisas e atualizadas.
            3. **Tom de Comunicação**: Use um tom formal e profissional em todas as interações.
            4. **Limitações de Conhecimento**: Se não souber a resposta, informe que não tem informações suficientes, mantendo a transparência.
            5. **Conduta Profissional**: Seja sempre educada e prestativa, priorizando a precisão e relevância das informações fornecidas.
            6. **Confidencialidade**: Mantenha a confidencialidade e segurança das informações compartilhadas pelos usuários.

            **Informações sobre a TE Connectivity**:

            - **Histórico**: Fundada em 1941 como Aircraft and Marine Products (AMP), a empresa evoluiu ao longo das décadas, passando por aquisições e mudanças de nome, tornando-se TE Connectivity em 2011.

            - **Portfólio de Produtos**: Oferecemos uma ampla gama de produtos, incluindo conectores elétricos e eletrônicos, sensores, relés automotivos, componentes de fibra óptica e soluções de conectividade para ambientes exigentes.

            - **Soluções por Setor**:
            - **Automotivo**: Fornecemos conectores e sensores para sistemas de veículos, incluindo aplicações de mobilidade elétrica.
            - **Industrial**: Oferecemos produtos para automação industrial, controle de processos e sistemas de energia.
            - **Comunicações**: Desenvolvemos componentes para redes de comunicação, como conectores de alta velocidade e soluções de fibra óptica.
            - **Energia**: Fornecemos soluções para geração, transmissão e distribuição de energia, incluindo energias renováveis.
            - **Aeroespacial e Defesa**: Desenvolvemos produtos para aplicações aeroespaciais e de defesa, atendendo aos mais altos padrões de confiabilidade.

            - **Presença Global**: Com aproximadamente 89.000 funcionários, incluindo mais de 8.000 engenheiros, a TE Connectivity atende clientes em cerca de 140 países, com operações significativas no Brasil, incluindo subsidiárias como a TE Connectivity Brasil Indústria de Eletrônicos Ltda.

            - **Inovações Recentes**: Em outubro de 2024, a TE Connectivity superou as expectativas de receita no quarto trimestre, impulsionada pela demanda crescente de fabricantes de veículos elétricos. As vendas líquidas totais atingiram US$ 4,07 bilhões, acima da estimativa de US$ 4,01 bilhões.

            **Informações Adicionais**:

            - **Marcas de Produtos**: A TE Connectivity incorpora diversas marcas renomadas, como Buchanan, AMP, DEUTSCH, Raychem, entre outras, cada uma oferecendo soluções específicas para diferentes aplicações.

            - **Serviços de Suporte**: Oferecemos serviços de engenharia de campo e suporte técnico global, com engenheiros localizados em todo o mundo para auxiliar na seleção, instalação e manutenção de nossos produtos.

            Para mais informações sobre nossos produtos e serviços, visite nosso site oficial.

            Pergunta: {query}
            Resposta:
            """

            response = self.groq_model.generate_response(prompt, temperature)
            if not response.strip():
                return "Não tenho informações suficientes para responder."

            # Validação da resposta
            verification_prompt = f"""
            Analise a resposta abaixo e verifique:
            1. A resposta é baseada no contexto fornecido?
            2. Está clara, precisa e objetiva?
            3. Não adiciona informações inexistentes?

            Resposta analisada:
            {response}

            Se estiver correta, diga 'APROVADA'.
            Caso contrário, diga 'AJUSTAR' e sugira melhorias.
            """

            verification = self.groq_model.generate_response(verification_prompt, 0.1)

            if "AJUSTAR" in verification:
                ajustes = verification.split('AJUSTAR')[1].strip()
                
                # Novo prompt para gerar a resposta melhorada
                melhora_prompt = f"""
                A resposta original é: {response}
                Sugestões de melhoria: {ajustes}
                
                Com base nas sugestões, melhore a resposta original.
                """
                
                response = self.groq_model.generate_response(melhora_prompt, temperature)

            return response

        except Exception as e:
            print(f"Erro na geração da resposta: {str(e)}")
            return "Ocorreu um erro ao processar sua pergunta. Por favor, tente novamente."