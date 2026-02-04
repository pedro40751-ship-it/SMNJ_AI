import psycopg2
from psycopg2 import OperationalError
from typing import Optional


class ConexaoBanco:
    
    def __init__(self):
        self.conexao: Optional[psycopg2.extensions.connection] = None
        
    def __enter__(self):
        try:
            self.conexao = psycopg2.connect(host='192.168.30.10',
                            port=6543,
                            database='postgres', 
                            user='postgres.local', 
                            password='your-super-secret-and-long-postgres-password'
                            )

        
            return self.conexao
        except OperationalError as e:
            raise RuntimeError(f"falha ao conectar no PostgresSQL: {e}") from e
        
    def __exit__(self,exc_type,exc_val,exc_tb):
        if self.conexao:
            self.conexao.close()