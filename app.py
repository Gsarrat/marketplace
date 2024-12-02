from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Página inicial
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        flash('Por favor, faça login primeiro.', 'danger')
        return redirect(url_for('login'))

    search_query = request.form.get('search', '')  # Captura o termo de busca

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Busca produtos com ou sem filtro de pesquisa
    if search_query:
        cursor.execute('SELECT id_produto, nome_produto, vlr_produto, descricao_produto, imagem_produto FROM produtos WHERE nome_produto LIKE ?', ('%' + search_query + '%',))
    else:
        cursor.execute('SELECT id_produto, nome_produto, vlr_produto, descricao_produto, imagem_produto FROM produtos')
    
    produtos = cursor.fetchall()

    # Pega o nome do usuário logado
    cpf = session['user']
    cursor.execute('SELECT nome_usuario FROM users WHERE cpf = ?', (cpf,))
    user = cursor.fetchone()
    nome_usuario = user[0] if user else 'Usuário'
    
    conn.close()

    return render_template('index.html', produtos=produtos, nome_usuario=nome_usuario)

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


        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE cpf = ?', (cpf,))
        user = cursor.fetchone()
        conn.close()


        if user:
            stored_hash = user[0]

            # Verifica se a senha recebida corresponde ao hash no banco
            if check_password_hash(stored_hash, password):
                session['user'] = cpf

                return redirect(url_for('index'))

        flash('CPF ou senha incorretos.', 'danger')

    return render_template('login.html')

if __name__ == '__main__':
    from models import init_db
    init_db()
    app.run(debug=True)
