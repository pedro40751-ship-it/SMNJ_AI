from conexao import ConexaoBanco
from openai import OpenAI
from dados_prompt import prompt
from insert import insert_perguntas
import os



def extrair_linhas_tabela(resposta_modelo):
    """
    Extrai as linhas da tabela markdown e retorna uma lista de dicionários.
    
    Args:
        tabela_markdown: String contendo a tabela em formato markdown
        
    Returns:
        list: Lista de dicionários com número, pergunta e resposta
    """
    linhas_dados = []
    
    # Divide a tabela em linhas
    linhas = resposta_modelo.strip().split('\n')
    
    # Processa cada linha (pulando cabeçalho e separador)
    for linha in linhas:
        # Ignora linhas vazias e separadores
        if not linha.strip() or '----' in linha:
            continue
            
        # Ignora o cabeçalho
        if 'Pergunta' in linha and 'Resposta' in linha:
            continue
        
        # Divide a linha em colunas pelo separador |
        colunas = linha.split('|')
        
        # Remove espaços e elementos vazios
        colunas = [col.strip() for col in colunas if col.strip()]
        
        # Verifica se tem pelo menos 3 colunas (número, pergunta, resposta)
        if len(colunas) >= 3:
            numero = colunas[0]
            pergunta = colunas[1]
            resposta = colunas[2]
            
            linhas_dados.append({
                'numero': numero,
                'pergunta': pergunta,
                'resposta': resposta
            })
    
    return linhas_dados


def texto_extraido(numero_processo):
    with ConexaoBanco() as conn:
        #Criação do cursor para executar comando SQL
        cursor = conn.cursor()
        cursor.execute('select texto from texto order by data_criacao desc limit 1 ')
        texto_extraido_pdf = cursor.fetchall()
        txt_texto_extraido_pdf = texto_extraido_pdf[0][0]
        txt_prompt_juri = prompt()
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        temperatura = 0.0
        response = client.chat.completions.create(
            model= 'gpt-4.1',
            messages=[
                {"role": "system", "content": txt_prompt_juri},
                {"role": "user", "content": txt_texto_extraido_pdf}
            ],
            temperature= temperatura
        )
        resposta_modelo=response.choices[0].message.content
    linhas = extrair_linhas_tabela(resposta_modelo)
    
    # 4. Insere cada linha no banco de dados
    contador_inserido = 0
    for linha in linhas:
        try:
            insert_perguntas(
                pergunta=linha['pergunta'],
                resposta=linha['resposta'],
                numero_processo=numero_processo
            )
            contador_inserido += 1
            print(f"✓ Linha {linha['numero']} inserida com sucesso")
        except Exception as e:
            print(f"✗ Erro ao inserir linha {linha['numero']}: {e}")
    
    print(f"\n{'='*50}")
    print(f"Total de linhas inseridas: {contador_inserido}/{len(linhas)}")
    print(f"{'='*50}")
    
    return resposta_modelo

       

