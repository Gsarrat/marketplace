from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from groq import Groq

# Importa Produtos
from produtos.tres_cartas import *
from produtos.caminho_semana import *





app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

#api groq
API_KEY = "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"
client = Groq(api_key=API_KEY)

def get_db_connection():
    return sqlite3.connect('main.db')


@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        flash('Por favor, faça login primeiro.', 'danger')
        return redirect(url_for('login'))

    search_query = request.form.get('search', '')  

    conn = get_db_connection()
    cursor = conn.cursor()

 
    if search_query:
        cursor.execute('SELECT id_produto, nome_produto, vlr_produto, descricao_produto, imagem_produto FROM produtos WHERE nome_produto LIKE ?', ('%' + search_query + '%',))
    else:
        cursor.execute('SELECT id_produto, nome_produto, vlr_produto, descricao_produto, imagem_produto FROM produtos')
    
    produtos = cursor.fetchall()

    cpf = session['user']
    cursor.execute('SELECT nome_usuario, Qt_coins FROM users WHERE cpf = ?', (cpf,))
    user = cursor.fetchone()
    nome_usuario = user[0] if user else 'Usuário'
    qt_coins = user[1] if user else 0  
    conn.close()
    return render_template('index.html', produtos=produtos, nome_usuario=nome_usuario, qt_coins=qt_coins)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('landing'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        cpf = request.form['cpf']
        nome_usuario = request.form['nome_usuario']

        password = request.form['password']
        confirm_password = request.form['confirm_password']


        if password != confirm_password:
            flash('As senhas não coincidem!', 'danger')
            return redirect(url_for('register'))


        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect('main.db')
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


        conn = sqlite3.connect('main.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE cpf = ?', (cpf,))
        user = cursor.fetchone()
        conn.close()


        if user:
            stored_hash = user[0]


            if check_password_hash(stored_hash, password):
                session['user'] = cpf

                return redirect(url_for('index'))

        flash('CPF ou senha incorretos.', 'danger')

    return render_template('login.html')

@app.route('/produtos')
def produtos():
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id_produto, nome_produto, vlr_produto, descricao_produto, imagem_produto, link 
        FROM produtos
        WHERE ativo = 1
    ''')
    produtos = cursor.fetchall()
    conn.close()
    return render_template('produtos.html', produtos=produtos)

from flask import request, render_template, redirect, url_for, flash
from math import ceil



@app.route('/gestao_usuarios', methods=['GET'])
def gestao_usuarios():
    cpf = request.args.get('cpf', '').strip()
    nome = request.args.get('nome', '').strip()
    email = request.args.get('email', '').strip()

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()

    page = request.args.get('page', 1, type=int)

    users_per_page = 10

    query_count = "SELECT COUNT(*) FROM users WHERE 1=1"
    params_count = []

    if cpf:
        query_count += " AND cpf LIKE ?"
        params_count.append(f"%{cpf}%")
    if nome:
        query_count += " AND nome_usuario LIKE ?"
        params_count.append(f"%{nome}%")
    if email:
        query_count += " AND email LIKE ?"
        params_count.append(f"%{email}%")

    cursor.execute(query_count, params_count)
    total_users = cursor.fetchone()[0]

    total_pages = (total_users + users_per_page - 1) // users_per_page

    query = "SELECT id_user, cpf, nome_usuario, email FROM users WHERE 1=1"
    params = []

    if cpf:
        query += " AND cpf LIKE ?"
        params.append(f"%{cpf}%")
    if nome:
        query += " AND nome_usuario LIKE ?"
        params.append(f"%{nome}%")
    if email:
        query += " AND email LIKE ?"
        params.append(f"%{email}%")

    query += " LIMIT ? OFFSET ?"
    params.append(users_per_page)
    params.append((page - 1) * users_per_page)

    cursor.execute(query, params)
    usuarios = cursor.fetchall()

    print("Usuários encontrados:", usuarios)

    conn.close()

    return render_template('gestao_usuarios.html', usuarios=usuarios, page=page, total_pages=total_pages, cpf=cpf, nome=nome, email=email)



@app.route('/editar_usuario', methods=['POST'])
def editar_usuario():
    user_id = request.form.get('id')
    cpf = request.form.get('cpf').strip()
    nome = request.form.get('nome').strip()
    email = request.form.get('email').strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id_user FROM users WHERE id_user = ?", (user_id,))
    usuario = cursor.fetchone()

    if not usuario:
        flash('Usuário não encontrado!', 'danger')
        return jsonify({'status': 'error', 'message': 'Usuário não encontrado!'}), 400

    try:
        cursor.execute("UPDATE users SET cpf = ?, nome_usuario = ?, email = ? WHERE id_user = ?",
                       (cpf, nome, email, user_id))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Usuário atualizado com sucesso!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erro ao atualizar o usuário: {str(e)}'}), 400
    finally:
        conn.close()


@app.route('/gestao_produtos')
def gestao_produtos():
    return
@app.route('/gestao_vendedores')
def gestao_vendedores():
    return
@app.route('/gestao_valores')
def gestao_valores():
    return










@app.route('/carrinho', methods=['GET', 'POST'])
def carrinho():
    if 'user' not in session:
        flash('Por favor, faça login primeiro.', 'danger')
        return redirect(url_for('login'))
    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()


    cpf = session['user']
    cursor.execute("""
        SELECT c.id_produto, p.nome_produto, p.vlr_produto, c.quantidade, (p.vlr_produto * c.quantidade) AS subtotal 
        FROM carrinho c
        JOIN produtos p ON c.id_produto = p.id_produto
        WHERE c.cpf_usuario = ?
    """, (cpf,))
    itens_carrinho = cursor.fetchall()

    total = sum(item[4] for item in itens_carrinho)

    conn.close()
    return render_template('carrinho.html', itens_carrinho=itens_carrinho, total=total)

@app.route('/finalizar_pedido', methods=['POST'])
def finalizar_pedido():
    if 'user' not in session:
        flash('Por favor, faça login primeiro.', 'danger')
        return redirect(url_for('login'))

    metodo_pagamento = request.form.get('metodo_pagamento')
    creditos_utilizados = float(request.form.get('creditos_utilizados', 0.00))

    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()

    cpf = session['user']


    cursor.execute("""
        SELECT c.id_produto, p.vlr_produto, c.quantidade, (p.vlr_produto * c.quantidade) AS subtotal 
        FROM carrinho c
        JOIN produtos p ON c.id_produto = p.id_produto
        WHERE c.cpf_usuario = ?
    """, (cpf,))
    itens_carrinho = cursor.fetchall()

    if not itens_carrinho:
        flash('Carrinho vazio. Adicione itens antes de finalizar a compra.', 'danger')
        return redirect(url_for('carrinho'))

    valor_total = sum(item[3] for item in itens_carrinho)


    cursor.execute("SELECT Qt_coins FROM users WHERE cpf = ?", (cpf,))
    qt_coins = cursor.fetchone()[0]
    if creditos_utilizados > qt_coins:
        flash('Créditos insuficientes.', 'danger')
        return redirect(url_for('carrinho'))

    valor_a_pagar_externo = max(0.00, valor_total - creditos_utilizados)


    cursor.execute("""
        INSERT INTO pedidos (id_usuario, data_criacao, status_pedido, valor_total, metodo_pagamento, 
                             status_pagamento, creditos_utilizados, valor_a_pagar_externo, data_atualizacao)
        VALUES ((SELECT id_user FROM users WHERE cpf = ?), datetime('now'), 'Pendente', ?, ?, 'Pendente', ?, ?, datetime('now'))
    """, (cpf, valor_total, metodo_pagamento, creditos_utilizados, valor_a_pagar_externo))
    id_pedido = cursor.lastrowid

    for item in itens_carrinho:
        id_produto, preco_unitario, quantidade, subtotal = item
        cursor.execute("""
            INSERT INTO itens_pedido (id_pedido, id_produto, quantidade, preco_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """, (id_pedido, id_produto, quantidade, preco_unitario, subtotal))

    cursor.execute("""
        UPDATE users SET Qt_coins = Qt_coins - ? WHERE cpf = ?
    """, (creditos_utilizados, cpf))

    cursor.execute("DELETE FROM carrinho WHERE cpf_usuario = ?", (cpf,))

    conn.commit()
    conn.close()

    flash('Pedido finalizado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/add_carrinho', methods=['POST'])
def add_carrinho():
    if 'user' not in session:
        flash('Por favor, faça login primeiro.', 'danger')
        return redirect(url_for('login'))

    id_produto = request.form.get('id_produto')
    quantidade = int(request.form.get('quantidade', 1))
    cpf = session['user']

    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT quantidade FROM carrinho WHERE cpf_usuario = ? AND id_produto = ?
    """, (cpf, id_produto))
    item_existente = cursor.fetchone()

    if item_existente:
        nova_quantidade = item_existente[0] + quantidade
        cursor.execute("""
            UPDATE carrinho SET quantidade = ? WHERE cpf_usuario = ? AND id_produto = ?
        """, (nova_quantidade, cpf, id_produto))
    else:
        cursor.execute("""
            INSERT INTO carrinho (cpf_usuario, id_produto, quantidade)
            VALUES (?, ?, ?)
        """, (cpf, id_produto, quantidade))

    conn.commit()
    conn.close()

    flash('Produto adicionado ao carrinho com sucesso!', 'success')
    return redirect(url_for('index'))


@app.route('/comprar_direto', methods=['POST'])
def comprar_direto():
    if 'user' not in session:
        flash('Por favor, faça login primeiro.', 'danger')
        return redirect(url_for('login'))

    id_produto = request.form.get('id_produto')
    quantidade = int(request.form.get('quantidade', 1))

    conn = sqlite3.connect('main.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_produto, vlr_produto FROM produtos WHERE id_produto = ?
    """, (id_produto,))
    produto = cursor.fetchone()

    if not produto:
        flash('Produto não encontrado.', 'danger')
        return redirect(url_for('index'))

    id_produto, preco_unitario = produto
    subtotal = preco_unitario * quantidade

    session['compra_direta'] = {'id_produto': id_produto, 'quantidade': quantidade, 'subtotal': subtotal}

    conn.close()
    return redirect(url_for('finalizar_pedido'))


@app.route('/nav_bar')
def nav_bar():
    return render_template('nav_bar.html')





# rotas dos produtos
@app.route('/tarot_tres_cartas', methods=['GET', 'POST'])
def tarot_tres_cartas():
    resultado = None
    if request.method == 'POST':
        pergunta = request.form.get('pergunta')  
        if pergunta:
            bruto = jogar_tarot(pergunta, client)  
            bruto["interpretacao"] = processar_interpretacao(bruto["interpretacao"])  
            resultado = bruto
    return render_template('produtos/tarot_tres_cartas.html', resultado=resultado)

@app.route('/caminho_semana', methods=['GET', 'POST'])
def caminho_semana():
    partes = None
    if request.method == 'POST':
        pergunta = request.form.get('pergunta')  
        if pergunta:
            bruto = Gerar_Tarefa_semanal(pergunta, client)  
            partes = processar_tarefas(bruto["interpretacao"])  
            print("Partes processadas:", partes)  # Verifique o log

    return render_template('produtos/caminho_semana.html', partes=partes)


if __name__ == '__main__':
    from models import init_db
    init_db()
    app.run(debug=True)
