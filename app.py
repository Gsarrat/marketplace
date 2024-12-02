from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Página inicial
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/index')
def index():
    if 'user' not in session:
        flash('Por favor, faça login primeiro.', 'danger')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id_produto, nome_produto, vlr_produto FROM produtos')
    produtos = cursor.fetchall()  
    conn.close()


    return render_template('index.html', produtos=produtos)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('landing'))

# Cadastro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        cpf = request.form['cpf']
        nome_usuario = request.form['nome_usuario']

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
            cursor.execute('INSERT INTO users (email, cpf, password, nome_usuario) VALUES (?, ?, ?, ?)', (email, cpf, hashed_password, nome_usuario))
            conn.commit()
            conn.close()
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('landing'))
        except sqlite3.IntegrityError:
            flash('Erro: Email ou CPF já cadastrados.', 'danger')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cpf = request.form['cpf']
        password = request.form['password']
        print(f"CPF recebido: {cpf}, Senha recebida: {password}")  # Depuração

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE cpf = ?', (cpf,))
        user = cursor.fetchone()
        conn.close()
        print(f"Usuário encontrado: {user}")  # Depuração

        if user:
            stored_hash = user[0]
            print("Senha armazenada no banco:", stored_hash)  # Depuração
            # Verifica se a senha recebida corresponde ao hash no banco
            if check_password_hash(stored_hash, password):
                session['user'] = cpf
                print("Login realizado com sucesso!")  # Depuração
                return redirect(url_for('index'))
            else:
                print("Senha incorreta!")  # Depuração
        else:
            print("Usuário não encontrado!")  # Depuração

        flash('CPF ou senha incorretos.', 'danger')

    return render_template('login.html')

if __name__ == '__main__':
    from models import init_db
    init_db()
    app.run(debug=True)
