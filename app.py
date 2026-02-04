# importar biblioteca para front end
import streamlit as st
# importa biblioteca para conecatar com a API de extração de texto
import requests
import time
# importar a conexao com o Banco
from conexao import ConexaoBanco
from texto_processado import texto_extraido
from insert import insert_texto

st.set_page_config(page_title="Análise Jurídica de PDF", layout="centered")
st.title("⚖️ Análise Jurídica Automatizada")

st.header("Envie um PDF para análise jurídica")
arquivo_pdf = st.file_uploader("Escolha um arquivo PDF de processo", type=["pdf"])

API_URL = "http://192.168.30.10:5000/extract-async"
STATUS_URL = "http://192.168.30.10:5000/status"

if arquivo_pdf is not None:
    st.success(f"Arquivo carregado: {arquivo_pdf.name}")
    
    if st.button("🔍 Analisar PDF"):
        with st.spinner("Processando PDF e analisando com IA jurídica..."):
            try:
                # Envia o arquivo para extração de texto
                files = {"file": (arquivo_pdf.name, arquivo_pdf.getvalue(), "application/pdf")}
                response = requests.post(API_URL, files=files)
                
                if response.status_code == 202:
                    job_id = response.json()["job_id"]
                    
                    # Verificar status da extração
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    while True:
                        status_response = requests.get(f"{STATUS_URL}/{job_id}")
                        
                        if status_response.status_code == 200:
                            job_data = status_response.json()
                            status = job_data.get("status")
                            progress = job_data.get("progress", 0)
                            
                            progress_bar.progress(progress)
                            status_text.text(f"Status: {status} ({progress}%)")
                            
                            if status == "done":
                                progress_bar.empty()
                                status_text.empty()
                                
                                # Extrair os dados
                                result = job_data.get("result", {})
                                files_data = result.get("files", [])
                                
                                # Processar o primeiro arquivo
                                if files_data:
                                    file_result = files_data[0]
                                    combined_text = file_result.get("combined_text", "")
                                    
                                    if combined_text:
                                        # Inserir o texto bruto no banco
                                        t=combined_text
                                        insert_texto(t)
                                        #pega o nome do arquivo e salva na variavel
                                        numero_processo = arquivo_pdf.name.replace('.pdf', '')
                                       
                                     
                                        
                                        # Processar com o modelo GPT
                                        st.success("✅ Texto extraído! Analisando com modelo jurídico...")
                                        
                                        try:
                                            # Chama a função que processa com o modelo GPT e envia o numero do processo junto
                                            resposta_modelo = texto_extraido(numero_processo)
                                            
                                            st.divider()
                                            st.subheader("📋 Análise Jurídica Completa")
                                            
                                            # Exibe informações do arquivo
                                            col1, col2, col3 = st.columns(3)
                                            with col1:
                                                st.metric("Arquivo", arquivo_pdf.name)
                                            with col2:
                                                st.metric("Páginas", file_result.get("meta", {}).get("pages", 0))
                                            with col3:
                                                st.metric("Status", "Analisado")
                                            
                                            st.divider()
                                            
                                            # Exibe a resposta do modelo
                                            st.markdown("### Resultado da Análise")
                                            
                                            # Verifica se a resposta está em formato Markdown (tabela)
                                            if "|" in resposta_modelo and "---" in resposta_modelo:
                                                # Renderiza como Markdown
                                                st.markdown(resposta_modelo)
                                            else:
                                                # Exibe como texto formatado
                                                st.markdown(resposta_modelo)
                                            
                                            # Botão para baixar a análise
                                            st.download_button(
                                                label="📥 Baixar Análise Completa",
                                                data=resposta_modelo,
                                                file_name=f"{arquivo_pdf.name.replace('.pdf', '')}_analise_juridica.md",
                                                mime="text/markdown"
                                            )
                                            
                                            # Estatísticas da análise
                                            st.divider()
                                            st.caption(f"Análise gerada em: {time.strftime('%d/%m/%Y %H:%M:%S')}")
                                            
                                        except Exception as e:
                                            st.error(f"❌ Erro ao processar com modelo jurídico: {str(e)}")
                                    else:
                                        st.warning("⚠️ Nenhum texto foi extraído do PDF.")
                                else:
                                    st.error("❌ Nenhum dado extraído do PDF.")
                                
                                break
                                
                            elif status == "error":
                                progress_bar.empty()
                                status_text.empty()
                                st.error(f"❌ Erro na extração: {job_data.get('error')}")
                                break
                        else:
                            st.error(f"❌ Erro ao verificar status: {status_response.status_code}")
                            break
                        
                        time.sleep(1)
                else:
                    st.error(f"❌ Erro ao enviar PDF: {response.status_code} - {response.text}")
                    
            except Exception as e:
                st.error(f"❌ Erro no processamento: {str(e)}")