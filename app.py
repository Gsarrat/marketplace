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

    cpf = session['user']
    cursor.execute('SELECT nome_usuario, Qt_coins FROM users WHERE cpf = ?', (cpf,))
    user = cursor.fetchone()
    nome_usuario = user[0] if user else 'Usuário'
    qt_coins = user[1] if user else 0  # Valor padrão caso não exista

    conn.close()
    return render_template('index.html', produtos=produtos, nome_usuario=nome_usuario, qt_coins=qt_coins)

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

# Carrinho

@app.route('/carrinho', methods=['GET', 'POST'])
def carrinho():
    if 'user' not in session:
        flash('Por favor, faça login primeiro.', 'danger')
        return redirect(url_for('login'))
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Seleciona os itens do carrinho do usuário
    cpf = session['user']
    cursor.execute("""
        SELECT c.id_produto, p.nome_produto, p.vlr_produto, c.quantidade, (p.vlr_produto * c.quantidade) AS subtotal 
        FROM carrinho c
        JOIN produtos p ON c.id_produto = p.id_produto
        WHERE c.cpf_usuario = ?
    """, (cpf,))
    itens_carrinho = cursor.fetchall()

    # Calcula o total do carrinho
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

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cpf = session['user']

    # Busca os itens do carrinho do usuário
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

    # Verifica saldo de créditos do usuário
    cursor.execute("SELECT Qt_coins FROM users WHERE cpf = ?", (cpf,))
    qt_coins = cursor.fetchone()[0]
    if creditos_utilizados > qt_coins:
        flash('Créditos insuficientes.', 'danger')
        return redirect(url_for('carrinho'))

    valor_a_pagar_externo = max(0.00, valor_total - creditos_utilizados)

    # Cria o pedido
    cursor.execute("""
        INSERT INTO pedidos (id_usuario, data_criacao, status_pedido, valor_total, metodo_pagamento, 
                             status_pagamento, creditos_utilizados, valor_a_pagar_externo, data_atualizacao)
        VALUES ((SELECT id_user FROM users WHERE cpf = ?), datetime('now'), 'Pendente', ?, ?, 'Pendente', ?, ?, datetime('now'))
    """, (cpf, valor_total, metodo_pagamento, creditos_utilizados, valor_a_pagar_externo))
    id_pedido = cursor.lastrowid

    # Adiciona os itens do pedido
    for item in itens_carrinho:
        id_produto, preco_unitario, quantidade, subtotal = item
        cursor.execute("""
            INSERT INTO itens_pedido (id_pedido, id_produto, quantidade, preco_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """, (id_pedido, id_produto, quantidade, preco_unitario, subtotal))

    # Atualiza créditos do usuário
    cursor.execute("""
        UPDATE users SET Qt_coins = Qt_coins - ? WHERE cpf = ?
    """, (creditos_utilizados, cpf))

    # Limpa o carrinho do usuário
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

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Verifica se o produto já está no carrinho do usuário
    cursor.execute("""
        SELECT quantidade FROM carrinho WHERE cpf_usuario = ? AND id_produto = ?
    """, (cpf, id_produto))
    item_existente = cursor.fetchone()

    if item_existente:
        # Atualiza a quantidade do produto no carrinho
        nova_quantidade = item_existente[0] + quantidade
        cursor.execute("""
            UPDATE carrinho SET quantidade = ? WHERE cpf_usuario = ? AND id_produto = ?
        """, (nova_quantidade, cpf, id_produto))
    else:
        # Adiciona o produto ao carrinho
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

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Busca os dados do produto
    cursor.execute("""
        SELECT id_produto, vlr_produto FROM produtos WHERE id_produto = ?
    """, (id_produto,))
    produto = cursor.fetchone()

    if not produto:
        flash('Produto não encontrado.', 'danger')
        return redirect(url_for('index'))

    id_produto, preco_unitario = produto
    subtotal = preco_unitario * quantidade

    # Redireciona para a lógica de finalizar pedido com apenas este produto
    session['compra_direta'] = {'id_produto': id_produto, 'quantidade': quantidade, 'subtotal': subtotal}

    conn.close()
    return redirect(url_for('finalizar_pedido'))





if __name__ == '__main__':
    from models import init_db
    init_db()
    app.run(debug=True)
