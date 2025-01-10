import sqlite3

DB_PATH = 'main.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  
    return conn


def criar_input_gpt(pergunta):

    return (
        f"Você é um terapeuta Holistico. Uma pessoa fez a seguinte pergunta: '{pergunta}'."
        f"baseado nessa pergunta voce deverá gerar uma sugestao de tarefa para cada dia da semana e uma descricao do porque a atividade ajudará a alvancar o objetivo final"
        f"e por fim elaborar uma conclusao sobre o que foi proposto"
        f"Por favor, formate a resposta no seguinte modelo: "
        f"**Tarefa do primeiro dia:**: ... "         
        f"**Descricao da primeira Tarefa**: ... "
        f"**Tarefa do segundo dia:**: ... "
        f"**Descricao da segunda Tarefa**: ... "
        f"**Tarefa do terceiro dia:**: ... "
        f"**Descricao da terceira Tarefa**: ... "
        f"**Tarefa do quarto dia:**: ... "
        f"**Descricao da quarta Tarefa**: ... "
        f"**Tarefa do quinto dia:**: ... "
        f"**Descricao da quinta Tarefa**: ... "
        f"**Tarefa do sexto dia:**: ... "
        f"**Descricao da sexta Tarefa**: ... "
        f"**Tarefa do setimo dia:**: ... "
        f"**Descricao da setima Tarefa**: ... "

        f"**Conclusão**: ... "

    )

def consultar_gpt(prompt, client):
    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )
    return completion.choices[0].message.content

def Gerar_Tarefa_semanal(pergunta, client):


    prompt = criar_input_gpt(pergunta)
    interpretacao = consultar_gpt(prompt, client)

    resultado = {
        "interpretacao": interpretacao
    }
    print(resultado)
    return resultado

def processar_tarefas(interpretacao):
    # Inicializa o dicionário com chaves vazias para tarefas e descrições
    partes = {f"tarefa_{i}": "" for i in range(1, 8)}
    partes.update({f"descricao_{i}": "" for i in range(1, 8)})
    partes["conclusao"] = ""

    dias = ["primeiro", "segundo", "terceiro", "quarto", "quinto", "sexto", "setimo"]
    dias_fem = ["primeira", "segunda", "terceira", "quarta", "quinta", "sexta", "setima"]

    for i, (dia, dia_fem) in enumerate(zip(dias, dias_fem), start=1):
        # Define os delimitadores para cada tarefa e descrição
        tarefa_key = f"**Tarefa do {dia} dia:**"
        descricao_key = f"**Descricao da {dia_fem} Tarefa**"

        # Processa a tarefa correspondente
        if tarefa_key in interpretacao:
            try:
                partes[f"tarefa_{i}"] = (
                    interpretacao.split(tarefa_key)[1].split("\n")[0].strip()
                )
            except IndexError:
                partes[f"tarefa_{i}"] = "Erro ao extrair a tarefa."

        # Processa a descrição correspondente
        if descricao_key in interpretacao:
            try:
                partes[f"descricao_{i}"] = (
                    interpretacao.split(descricao_key)[1].split("\n")[0].strip()
                )
            except IndexError:
                partes[f"descricao_{i}"] = "Erro ao extrair a descrição."

    # Processa a conclusão
    if "**Conclusão**" in interpretacao:
        try:
            partes["conclusao"] = interpretacao.split("**Conclusão**:")[1].strip()
        except IndexError:
            partes["conclusao"] = "Erro ao extrair a conclusão."

    return partes

