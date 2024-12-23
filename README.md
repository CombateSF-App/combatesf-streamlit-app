# Combate SF - Streamlit App
Este repositório contém todos os arquivos necessários para a funcionalidade do app de dashboard pela plataforma Streamlit.

## Estrutura dos Arquivos
        .
    ├── logos						# Logos utilizados nas páginas do app
    ├── pages						# Arquivos .py responsáveis por cada uma das 3 páginas acessáveis através do menu do app
    ├── prediction					# Bases de dados utilizadas pelo app
    ├── my_database.db				# Base de dados utilizada pelo app
    ├── requirements.txt			# Dependências do app
    ├── GitHub.txt					# Tutorial de utilização das funcionalidades necessárias do GitHub
    ├── Streamlit.txt				# Tutorial de utilização das funcionalidades necessárias do Streamlit Community Cloud
    └── README.md

## Especificação da funcionalidade de cada página:

### Home:
	> Download de dois arquivos .csv contendo as porcentagens de desfolha por talhão e por fazenda.

### Informações gerais:
	Informações filtradas por data, empresa, fazenda e talhão:
	> Gráficos de rosca e barra com respeito a áreas de desfolha e monitoramento
	> Heatmap gradiente de porcentagem de cobertura do dossel
	(O heatmap binário foi implementado, porém foi removido e o código responsável por essa finalidade encontra-se comentado)

### Mapa da fazenda:
	> Download e visualização de mapas filtrados for data e fazenda

### Gráficos temporais:
	> Visualização de gráficos de porcentagens de cobertura do dossel e de desfolha por fazenda e talhão
