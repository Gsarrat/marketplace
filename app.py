from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Cadastro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        cpf = request.form['cpf']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Verifica se as senhas coincidem
        if password != confirm_password:
            flash('As senhas não coincidem!', 'danger')
            return redirect(url_for('register'))

        # Hash da senha
        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (email, cpf, password) VALUES (?, ?, ?)', 
                           (email, cpf, hashed_password))
            conn.commit()
            conn.close()
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash('Erro: Email ou CPF já cadastrados.', 'danger')

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cpf = request.form['cpf']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE cpf = ?', (cpf,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            flash('Login realizado com sucesso!', 'success')
            session['user'] = cpf  
            return redirect(url_for('index'))
        else:
            flash('CPF ou senha incorretos.', 'danger')

    return render_template('login.html')

if __name__ == '__main__':
    from models import init_db
    init_db()
    app.run(debug=True)
