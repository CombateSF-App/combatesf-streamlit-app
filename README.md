# Combate SF - Streamlit App
Este repositório contém todos os arquivos necessários para a funcionalidade do app de dashboard pela plataforma Streamlit.

## Estrutura dos Arquivos
    .
    ├── logos                         # Logos utilizados nas páginas do app
    ├── pages                         # Arquivos .py responsáveis por cada uma das 3 páginas acessáveis através do menu do app
    ├── prediction                    # Bases de dados utilizadas pelo app
    ├── my_database.db                # Base de dados utilizada pelo app
    ├── requirements.txt              # Dependências do app
    └── README.md

## Tutorial de Utilização Local do App
> Nota
    Todos os comandos apresentados a seguir devem ser reproduzidos em uma Command-Line Interface (CLI), ou Interface de Linha de Comando, como o Windows PowerShell ou o Prompt de Comando, e assumem que o ambiente sendo utilizado já possui instalados os programas\n
	    python\n
        pip\n
	    git

#### O repositório no GitHub contém todos os arquivos referentes ao projeto. Entretanto, a base de dados utilizada pelo app excede o limite de tamanho permitido pelo GitHub. Portanto, utilizamos também a ferramenta Git LSF (Git Large File Storage), que viabiliza o upload de arquivos de até 2GB gratuitamente.

#### O repositório deve ser alterado sempre que for desejada qualquer alteração na base de dados "my_database.db". Sendo assim, há uma sequência de passos a serem seguidos sempre que uma alteração for efetuada:

#### Na primeira vez que for seguido o procedimento, é preciso criar um diretório local através do qual serão feitas as alterações por meio do comando
1)
git clone https://github.com/CombateSF-App/combatesf-streamlit-app

#### Em seguida, devemos acessar o novo diretório, por meio do comando (no Sistema Operacional Windows)
2)
cd combatesf-streamlit-app

#### Por fim, após a alteração da base de dados, a sequência de comandos a seguir determina o uso do Git LFS e atualiza o repositório no GitHub
3)	git lfs install
	git lfs track .\my_database.db
	git add .\.gitattributes
	git add .\my_database.db
	git commit -m "[Mensagem de Commit]"
	git push

#### Após este último comando, pode surgir na tela algumas opções de login com o GitHub. Neste passo a passo, elas não são utilizadas, então a janela que as apresenta pode ser fechada.
#### A seguir, devemos digitar “CombateSF-App” ao lado de
4)	Username for 'https://github.com':

#### No campo seguinte,
5)	Password for 'https://CombateSF-App@github.com':,

#### devemos digitar o GitHub Personal access token ao invés da senha da conta.
#### Este vídeo no YouTube serve como tutorial para a obtenção do token: https://www.youtube.com/watch?v=EaR4HRsYSPg


#### Nas proximas vezes que for seguido o procedimento, devemos acessar o diretório criado anteriormente e executar o comando a seguir:
	git pull https://github.com/CombateSF-App/combatesf-streamlit-app

Por fim, após a alteração da base de dados, o procedimento consiste em repetir os passos 3), 4) e 5) mencionados acima.


Resumidamente:
	- Primeira vez:
		git clone https://github.com/CombateSF-App/combatesf-streamlit-app
		cd combatesf-streamlit-app
		git lfs install
		git lfs track .\my_database.db
		git add .\.gitattributes
		git add .\my_database.db
		git commit -m "[Mensagem de Commit]"
		git push
		Username for 'https://github.com': CombateSF-App
		Password for 'https://CombateSF-App@github.com': [Token]
	
	- Próximas vezes:
		git pull https://github.com/CombateSF-App/combatesf-streamlit-app
		git lfs install
		git lfs track .\my_database.db
		git add .\.gitattributes
		git add .\my_database.db
		git commit -m "[Mensagem de Commit]"
		git push
		Caso necessário:
			Username for 'https://github.com': CombateSF-App
			Password for 'https://CombateSF-App@github.com': [Token]


Após a criação do repositório no GitHub, cujo nome é "combatesf-streamlit-app", devemos acessar a plataforma do Streamlit Community Cloud e clicar em "Create App", onde são selecionadas todas as configurações do app. Este procedimento não precisa ser repetido, e já foi feito uma vez. Entretanto, pode ser necessário efetuá-lo novamente caso seja necessário, por conta de alguma necessidade futura, repetir o processo de deploy.
Caso ocorra algum erro durante a execução da aplicação, ele será visível por meio do console presente junto ao app, quando acessado através desta plataforma. É necessário, neste casso, fazer "Reboot" do app, através dos botões disponíveis, e buscar corrigir o erro indicado no console.

O deploy do app é feito pelo Streamlit Community Cloud. Para acessar o app como administrador e obter controle sobre a atividade dos usuários e sobre qualquer erro que possa ocorrer, é preciso fazer login no site.
Recomenda-se efetuar o login no Streamlit Community Cloud através do GitHub.

O arquivo "requirements.txt" contém todas as dependências do app para que ele possa ser executado. A plataforma do Streamlit faz as instalações necessárias por conta própria através do arquivo. Entretanto, caso seja desejado efetuar um teste local do app, o comando
	pip install -r requirements.txt
instala as dependências necessárias na máquina onde se deseja efetuar o teste.

Para efetuar um teste local do app, devemos seguir os passos 1) e 2) e executar o comando
	streamlit run .\Home.py
Este comando abre uma guia em um browser por meio da qual é possível interagir com o app.


## Especificação da Funcionalidade de Cada Página

### Home:
	- Download de dois arquivos .csv contendo as porcentagens de desfolha por talhão e por fazenda.

### Informações gerais:
	Informações filtradas por data, empresa, fazenda e talhão:
	- Gráficos de rosca e barra com respeito a áreas de desfolha e monitoramento
	- Heatmap gradiente de porcentagem de cobertura do dossel
	(O heatmap binário foi implementado, porém foi removido e o código responsável por essa finalidade encontra-se comentado)

### Mapa da fazenda:
	- Download e visualização de mapas filtrados for data e fazenda

### Gráficos temporais:
	- Visualização de gráficos de porcentagens de cobertura do dossel e de desfolha por fazenda e talhão
