import random

CARTAS_TAROT_MARSELA = [
    "O Louco", "O Mago", "A Suma Sacerdotisa", "A Imperatriz", "O Imperador", "O Papa",
    "Os Amantes", "O Carro", "A Força", "O Eremita", "A Roda da Fortuna", "A Justiça",
    "O Enforcado", "A Morte", "A Temperança", "O Diabo", "A Torre", "A Estrela",
    "A Lua", "O Sol", "O Julgamento", "O Mundo"
]

SIGNIFICADOS_TAROT = {
    "O Louco": "Novos começos, aventuras inesperadas, liberdade.",
    "O Mago": "Habilidade, poder, ação, transformação.",
    "A Suma Sacerdotisa": "Intuição, sabedoria, mistério, conhecimento oculto.",
    "A Imperatriz": "Fertilidade, abundância, natureza, criatividade.",
    "O Imperador": "Autoridade, estrutura, controle, estabilidade.",
    "O Papa": "Tradição, espiritualidade, conselho, aprendizado.",
    "Os Amantes": "Escolhas, união, harmonia, amor.",
    "O Carro": "Vontade, determinação, sucesso, superação.",
    "A Força": "Coragem, energia, dominação, compaixão.",
    "O Eremita": "Solidão, introspecção, sabedoria, guia interior.",
    "A Roda da Fortuna": "Mudança, destino, ciclos, sorte.",
    "A Justiça": "Equilíbrio, justiça, verdade, imparcialidade.",
    "O Enforcado": "Sacrifício, nova perspectiva, entrega, suspensão.",
    "A Morte": "Transformação, fim de um ciclo, mudança profunda.",
    "A Temperança": "Equilíbrio, paciência, moderação, harmonia.",
    "O Diabo": "Apego, materialismo, tentação, vícios.",
    "A Torre": "Destruição, revelações, mudança abrupta, choque.",
    "A Estrela": "Esperança, inspiração, serenidade, renovação.",
    "A Lua": "Ilusão, medo, sonhos, inconsciente.",
    "O Sol": "Sucesso, alegria, vitalidade, clareza.",
    "O Julgamento": "Ressurreição, renovação, julgamento, despertar.",
    "O Mundo": "Realização, completude, sucesso, viagem."
}

def sortear_cartas(cartas, qtd=3):
    return random.sample(cartas, qtd)

def criar_input_gpt(pergunta, cartas):
    significados = [SIGNIFICADOS_TAROT[carta] for carta in cartas]
    return (
        f"Você é um especialista em Tarot. Uma pessoa fez a seguinte pergunta: '{pergunta}'. "
        f"As cartas sorteadas foram: {', '.join(cartas)}. "
        f"Os significados básicos dessas cartas são: {', '.join(significados)}. "
        f"Baseado nisso, forneça uma interpretação detalhada e útil para essa pessoa."
    )

def consultar_gpt(prompt, client):
    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )
    return completion.choices[0].message.content

def jogar_tarot(pergunta, client):
    cartas_tiradas = sortear_cartas(CARTAS_TAROT_MARSELA)
    prompt = criar_input_gpt(pergunta, cartas_tiradas)
    interpretacao = consultar_gpt(prompt, client)

    resultado = {
        "cartas": [{"nome": carta, "descricao": SIGNIFICADOS_TAROT[carta]} for carta in cartas_tiradas],
        "interpretacao": interpretacao
    }
    return resultado
