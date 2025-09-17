import psycopg2
from psycopg2 import sql
from tkinter import messagebox

DB_NAME = "gestao_interna"
DB_USER = "postgres"
DB_PASS = "A12345" 
DB_HOST = "localhost"
DB_PORT = "5432"

class Database:

    def __init__(self):
        self.conn = None
        try:
            self.conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASS,
                host=DB_HOST,
                port=DB_PORT
            )
        except psycopg2.OperationalError as e:
            print(f"[ERRO DE CONEXÃO] Verifique as credenciais e se o serviço do PostgreSQL está ativo. Erro: {e}")
            self.conn = None
        except Exception as e:
            print(f"[ERRO DESCONHECIDO NA CONEXÃO] {e}")
            self.conn = None

    def close_connection(self):
        if self.conn:
            self.conn.close()
            print("[OK] Conexão com o banco de dados fechada.")

    def execute_query(self, query, params=None):
        if not self.conn:
            return None
        
        with self.conn.cursor() as cur:
            try:
                cur.execute(query, params)
                return cur.fetchall()
            except Exception as e:
                print(f"[ERRO DE CONSULTA] Query: {query} | Erro: {e}")
                messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro ao consultar os dados.\n\nDetalhe: {e}")
                return None

    def execute_modificacao(self, query, params=None, return_id=False):
        if not self.conn:
            return False
        
        with self.conn.cursor() as cur:
            try:
                cur.execute(query, params)
                
                if return_id:
                    returned_id = cur.fetchone()
                    self.conn.commit()
                    return returned_id if returned_id else True
                
                self.conn.commit()
                return True
            except Exception as e:
                print(f"[ERRO DE MODIFICAÇÃO] Query: {query} | Erro: {e}")

                self.conn.rollback()
                messagebox.showerror("Erro de Banco de Dados", f"Não foi possível salvar os dados.\n\nDetalhe: {e}")
                return False