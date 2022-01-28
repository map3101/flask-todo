from flask_mail import Mail, Message
from unittest import expectedFailure
from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

from sqlalchemy import false

app = Flask(__name__)
# Configuração do BD
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# Configurações para o envio de emails
# Conta que enviará os emails é do gmail, logo utilizarei o mail server deles
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
# Para o username e senha, são utilizadas variáveis de ambiente
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get("MAIL_DEFAULT_SENDER")
db = SQLAlchemy(app)
mail = Mail()

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return '<Task %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        # Pega valores do form de adicionar tarefa content e email
        task_content = request.form['content']
        task_email = request.form['email']
        # Cria uma nova tarefa baseado na Model Todo
        new_task = Todo(content=task_content, email=task_email)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'ERROR'
    else:
        # Salva as tarefas na ordem das mais recentes primeiro
        tasks = Todo.query.order_by(Todo.date_created.desc()).all()
        return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'ERROR'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
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
def mail(id):
    # Query no banco de dados para pegar as infos do todo
    task = Todo.query.get_or_404(id)
    # Monta a mensagem que será enviada
    msg = Message(
        body=task.content,
        subject="Task Manager - Task " + task.date_created,
        recipients=[task.email]
        )
    return 

if __name__ == "__main__":
    app.run(debug=True)