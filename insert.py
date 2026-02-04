from conexao import ConexaoBanco

def insert_texto(t):
     with ConexaoBanco() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO texto (texto) VALUES (%s)", (t,))
        conn.commit()


def insert_perguntas(pergunta,resposta,numero_processo):
    with ConexaoBanco() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO perguntas_respostas02 (pergunta,resposta,numero_processo) VALUES (%s,%s,%s)",(pergunta,resposta,numero_processo))
        conn.commit()
        