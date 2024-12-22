Para efetuarmos o deploy do app no Streamlit Community Cloud - para que seja possibilitado seu acesso via browser através de um link - é preciso criar um repositório no GitHub e sincronizá-lo com o app.
Entretanto, a base de dados utilizada pelo app excede o limite de tamanho permitido pelo GitHub. Portanto, utilizamos também a ferramenta Git LSF (Git Large File Storage), que viabiliza o upload de arquivos de até 2GB gratuitamente.

O repositório deve ser alterado sempre que for desejada qualquer alteração na base de dados "my_database.db". Sendo assim, há uma sequência de passos a serem seguidos sempre que uma alteração for efetuada:

Na primeira vez que for seguido o procedimento, é preciso criar um diretório local através do qual serão feitas as alterações por meio do comando
1)	git clone https://github.com/CombateSF-App/combatesf-streamlit-app

Em seguida, devemos acessar o novo diretório, por meio do comando (no Sistema Operacional Windows)
2)	cd combatesf-streamlit-app

Por fim, após a alteração da base de dados, a sequência de comandos a seguir determina o uso do Git LFS e atualiza o repositório no GitHub
3)	git lfs install
	git lfs track .\my_database.db
	git add .\.gitattributes
	git add .\my_database.db
	git commit -m "[Mensagem de Commit]"
	git push

Após este último comando, pode surgir na tela algumas opções de login com o GitHub. Neste passo a passo, elas não são utilizadas, então a janela que as apresenta pode ser fechada.
A seguir, devemos digitar “CombateSF-App” ao lado de
4)	Username for 'https://github.com':

No campo seguinte,
5)	Password for 'https://CombateSF-App@github.com':,

devemos digitar o GitHub Personal access token ao invés da senha da conta.
Este vídeo no YouTube serve como tutorial para a obtenção do token: https://www.youtube.com/watch?v=EaR4HRsYSPg


Nas proximas vezes que for seguido o procedimento, devemos acessar o diretório criado anteriormente e executar o comando a seguir:
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
		Username for 'https://github.com': CombateSF-App
		Password for 'https://CombateSF-App@github.com': [Token]
