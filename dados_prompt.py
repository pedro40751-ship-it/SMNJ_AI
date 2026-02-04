from conexao import ConexaoBanco

def prompt():
  with ConexaoBanco() as conn:
    cursor = conn.cursor()
    cursor.execute("select prompt from prompt order by data_criacao desc limit 1")
    prompt_juri=cursor.fetchall()
    txt_prompt_juri= prompt_juri[0][0]

  return txt_prompt_juri


    
