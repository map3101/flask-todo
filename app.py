from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
import os

from sqlalchemy import false

app = Flask(__name__)
# Secret Key para o flask-login
app.secret_key = 'thisisecret'
# Configuração do BD
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
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
# Inicialização do SQLAlchemy
db = SQLAlchemy(app)
# Inicialização do flask-mail
mail = Mail(app)
# Inicialização do flask-login
login_manager = LoginManager(app)
# Indicar página de redirecionamento caso usuário não tenha feito login
login_manager.login_view = 'loginuser'

# Models do banco de dados
# Model das tarefas
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    # Adiciona Foreign Key referente ao id do usuário
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        return '<Task %r>' % self.id

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

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/', methods=['POST', 'GET'])
@login_required
def index():
    if request.method == 'POST':
        # Pega valores do form de adicionar tarefa content e email
        task_content = request.form['content']
        task_email = request.form['email']
        # Cria uma nova tarefa baseado na Model Todo
        new_task = Todo(content=task_content, email=task_email, user_id=current_user.id)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'ERROR'
    else:
        # Busca as tarefas do usuário que está logado (current_user do flask-login)
        tasks = Todo.query.filter_by(user_id = current_user.id).all()
        return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'ERROR'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        task.email = request.form['email']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'ERROR'
    else:
        return render_template('update.html', task=task)

# Rota para mandar email com conteúdo da tarefa
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

# Rota para autenticar o usuário
@app.route('/loginuser', methods=['POST', 'GET'])
def loginuser():
    if current_user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email = email).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/')
    
    if request.method == 'GET':
        return render_template('login.html')

# Rota para registrar um novo usuário
@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
     
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
 
        if User.query.filter_by(email=email).first():
            return ('Email already Present')
             
        user = User(email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/loginuser')
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)