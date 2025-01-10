import random
import sqlite3

DB_PATH = 'main.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  
    return conn

def fetch_cartas_do_banco():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT nome_arcano, significado, img_ref FROM info_arcanos")
    cartas = cursor.fetchall()

    conn.close()

    return {carta['nome_arcano']: {'significado': carta['significado'], 'img_ref': carta['img_ref']} for carta in cartas}

def sortear_cartas(cartas, qtd=3):
    if qtd > len(cartas):
        raise ValueError(f"Não há cartas suficientes para sortear {qtd}. Total disponível: {len(cartas)}")
    return random.sample(list(cartas.keys()), qtd)

def criar_input_gpt(pergunta, cartas, cartas_info):
    significados = [cartas_info[carta]['significado'] for carta in cartas]
    return (
        f"Você é um especialista em Tarot. Uma pessoa fez a seguinte pergunta: '{pergunta}'. "
        f"As cartas sorteadas foram: {', '.join(cartas)}. "
        f"Os significados básicos dessas cartas são: {', '.join(significados)}. "
        f"Baseado nisso, forneça uma interpretação detalhada e útil para essa pessoa. "
        f"A resposta deve ser estruturada em seis seções claras e separadas: "
        f"- Interpretação da primeira carta (inter_cart_um). "
        f"- Interpretação da segunda carta (inter_cart_dois). "
        f"- Interpretação da terceira carta (inter_cart_tres). "
        f"- Interpretação geral das cartas (inter_geral). "
        f"- Conclusão (conclusao). "
        f"- Dicas práticas (dicas). "
        f"Por favor, formate a resposta no seguinte modelo: "
        f"**Interpretação da primeira carta**: ... "
        f"**Interpretação da segunda carta**: ... "
        f"**Interpretação da terceira carta**: ... "
        f"**Interpretação geral**: ... "
        f"**Conclusão**: ... "
        f"**Dicas práticas**: ... "
    )

def consultar_gpt(prompt, client):
    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )
    return completion.choices[0].message.content

def jogar_tarot(pergunta, client):
    cartas_info = fetch_cartas_do_banco()
    cartas_tiradas = sortear_cartas(cartas_info)
    prompt = criar_input_gpt(pergunta, cartas_tiradas, cartas_info)
    interpretacao = consultar_gpt(prompt, client)

    resultado = {
        "cartas": [
            {
                "nome": carta,
                "descricao": cartas_info[carta]['significado'],
                "img_ref": cartas_info[carta]['img_ref']
            } 
            for carta in cartas_tiradas
        ],
        "interpretacao": interpretacao
    }
    return resultado


def processar_interpretacao(interpretacao):
    partes = {
        "inter_cart_um": "",
        "inter_cart_dois": "",
        "inter_cart_tres": "",
        "inter_geral": "",
        "conclusao": "",
        "dicas": ""
    }

    # Dividir a interpretação em seções com base no padrão do prompt
    if "**Interpretação da primeira carta**" in interpretacao:
        partes["inter_cart_um"] = interpretacao.split("**Interpretação da primeira carta**:")[1].split("**Interpretação da segunda carta**")[0].strip()
    if "**Interpretação da segunda carta**" in interpretacao:
        partes["inter_cart_dois"] = interpretacao.split("**Interpretação da segunda carta**:")[1].split("**Interpretação da terceira carta**")[0].strip()
    if "**Interpretação da terceira carta**" in interpretacao:
        partes["inter_cart_tres"] = interpretacao.split("**Interpretação da terceira carta**:")[1].split("**Interpretação geral**")[0].strip()
    if "**Interpretação geral**" in interpretacao:
        partes["inter_geral"] = interpretacao.split("**Interpretação geral**:")[1].split("**Conclusão**")[0].strip()
    if "**Conclusão**" in interpretacao:
        partes["conclusao"] = interpretacao.split("**Conclusão**:")[1].split("**Dicas práticas**")[0].strip()
    if "**Dicas práticas**" in interpretacao:
        partes["dicas"] = interpretacao.split("**Dicas práticas**:")[1].strip()

    return partes