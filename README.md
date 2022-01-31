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
**Implementação da view de enviar emails**
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
#### Autenticação de usuário
