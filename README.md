# flask-todo
Atividade Prática do processo seletivo de estágio da BlueBridge

### Como rodar o projeto
Requisitos: Python3.+ e pip3
1. Instalar o `virtualenv`:
```
$ pip3 install virtualenv
```

2. Abra a pasta do projeto e execute o comando:
```
$ virtualenv env
```

3. Execute o comando para ativar o ambiente virtual:
```
$ .\env\Scripts\activate
```

4. Instale as dependências do projeto:
```
$ (env) pip install -r requirements.txt
```

5. Inicie o servidor:
```
$ (env) python app.py
```
### Funcionalidade de enviar email (Segunda etapa)
Para atingir esse objetivo, primeiramente editei a classe **Todo** e adicionei uma nova coluna:
```
email = db.Column(db.String(100), nullable=False)
```
Com isso posso registrar um email para cada tarefa. O próximo passo foi editar o formulário do arquivo **index.html** para adicionar um campo de email.
```
<form action="/" method="POST">
        <!-- Input de email, type="email" para validação -->
        <input placeholder="Email" type="email" name="email" id="email">
        <input placeholder="Task" type="text" name="content" id="content">
        <br>
        <input type="submit" value="Add Task" id="addButton">
    </form>
```
Agora temos um form completo para a segunda etapa. 
#### Implementação da view de enviar emails 
Para essa funcionalidade foi utilizado o Flask-Mail. Seguindo a documentação configurei as seguintes variáveis do app:
```
# Configurações para o envio de emails
# Conta que enviará os emails é do gmail, logo utilizarei o mail server deles
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# Usar SSL e porta 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_PORT'] = 465
# Para o username e senha, são utilizadas variáveis de ambiente
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get("MAIL_USERNAME")

# Inicialização do flask-mail
mail = Mail(app)
```
**Para o deploy do heroku a conta configurada é taskmanagerprocesso@gmail.com**
**Para configurar as variáveis de ambiente utilize o comando export com os nomes indicados.**
```
export MAIL_USERNAME="username@gmail.com" # Caso for outro serviço de email, alterar variável MAIL_SERVER
export MAIL_PASSWORD="password"
export MAIL_DEFAULT_USER=$MAIL_USERNAME
```

A rota declarada recebe a id de uma tarefa como parâmetro. Utilizando o Flask-Mail posso montar a mensagem e enviá-la:
```
@app.route('/mail/<int:id>', methods=['GET'])
@login_required
def send_mail(id):
    # Query no banco de dados para pegar as infos do todo
    task = Todo.query.get_or_404(id)
    # Monta a mensagem que será enviada
    msg = Message(
        body=task.content,
        subject="Task Manager - Task " + str(task.date_created.date()),
        recipients=[task.email]
    )
    try:
        # Tenta enviar a mensagem
        mail.send(msg)
        return 'EMAIL SENT!'
    except:
        return 'ERROR'
```

### Funcionalidades da terceira etapa
Foram implementadas 3 funcionalidades.
#### Autenticação e registro de usuário
##### Porque essa funcionalidade foi implementada?
Principalmente para proteger os dados dos usuários e melhorar a usabilidade. Além disso, em aplicações reais normalmente temos essas funcionalidades. 
##### O que foi feito
Utilizando algumas funções do Flask-Login e configurando segundo a documentação pude implementar essas funcionalidades com facilidade.
```
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user

# Secret Key para o flask-login
app.secret_key = os.environ.get("SECRET_KEY")

# Inicialização do flask-login
login_manager = LoginManager(app)
# Indicar página de redirecionamento caso usuário não tenha feito login, será ativado nas rotas com @login_required
login_manager.login_view = 'loginuser'
```
O Flask-Login utiliza cookies para amrazenar as informações da _session_ e assim autenticar e deslogar usuários.

###### Criar a model de usuário
```
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String())
    # Adiciona relação one-to-many com a model Todo
    tasks = db.relationship('Todo', backref='user', lazy=True)

    # Função para gerar o hash da senha
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    # Função para checar se a senha corresponde ao hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```
Devido a relação criada para as tasks, foi necessário adicionar uma coluna a table de Todos
```
    # Adiciona Foreign Key referente ao id do usuário
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
```
###### Criar forms de login e registro
Foram criadas duas templates, uma para login e outra para registro. Cada template tem seus campos e suas funcionalidades foram implementadas nas rotas `/loginuser` e `/register`, respectivamente.

###### Rota /loginuser
O email preenchido no formulário de login e utilizado para fazer uma query no banco de dados. Caso um usuário for encontrado e a função `check_password` retornar verdadeiro, a função `login_user` será chamada. Caso contrário o usuário não será logado.

###### Rota /register
Primeiramente ocorre a validação dos campos preenchidos no formulário. Caso tudo estiver preenchido o código realizará uma nova verificação, mas agora para conferir se o email digitado já está registrado em alguma conta. Caso tudo estiver correto e validado o usuário é registrado e o programa redireciona para a tela de login.

###### Rota /logout
Apenas desloga o usu
