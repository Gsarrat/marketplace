import sqlite3

def init_db():
    with sqlite3.connect('main.db') as conn:
        cursor = conn.cursor()
        

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS perfil_Usuario (
                id_acesso INTEGER NOT NULL UNIQUE,
                nome TEXT NOT NULL UNIQUE,
                PRIMARY KEY (id_acesso)
            );
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id_user INTEGER NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                cpf TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                nome_usuario TEXT NOT NULL,
                Qt_coins REAL NOT NULL DEFAULT 0,
                access_lvl INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (id_user AUTOINCREMENT),
                FOREIGN KEY (perfil_Usuario_Id) REFERENCES perfil_Usuario (id_acesso)
            );
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id_produto INTEGER NOT NULL UNIQUE,
                nome_produto TEXT,
                vlr_produto REAL,
                descricao_produto TEXT,
                imagem_produto TEXT,
                PRIMARY KEY (id_produto AUTOINCREMENT)
            );
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carrinho (
                id_carrinho INTEGER,
                cpf_usuario TEXT NOT NULL,
                id_produto INTEGER NOT NULL,
                quantidade INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (id_carrinho),
                FOREIGN KEY (cpf_usuario) REFERENCES users (cpf),
                FOREIGN KEY (id_produto) REFERENCES produtos (id_produto)
            );
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id_pedido INTEGER NOT NULL UNIQUE,
                id_usuario INTEGER NOT NULL,
                data_criacao BLOB NOT NULL,
                status_pedido TEXT NOT NULL,
                valor_total REAL NOT NULL,
                metodo_pagamento TEXT NOT NULL,
                status_pagamento TEXT NOT NULL,
                gateway_id TEXT,
                creditos_utilizados REAL NOT NULL DEFAULT 0.00,
                valor_a_pagar_externo REAL,
                endereco_entrega TEXT,
                data_atualizacao BLOB NOT NULL,
                PRIMARY KEY (id_pedido),
                FOREIGN KEY (id_usuario) REFERENCES users (id_user)
            );
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS itens_pedido (
                id_item INTEGER NOT NULL,
                id_pedido INTEGER NOT NULL UNIQUE,
                id_produto INTEGER NOT NULL UNIQUE,
                quantidade INTEGER NOT NULL,
                preco_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                PRIMARY KEY (id_item AUTOINCREMENT),
                FOREIGN KEY (id_pedido) REFERENCES pedidos (id_pedido),
                FOREIGN KEY (id_produto) REFERENCES produtos (id_produto)
            );
        ''')
        
        conn.commit()
