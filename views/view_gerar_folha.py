# Arquivo: views/view_gerar_folha.py (Com lógica de geração em massa)

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import calendar
import random # Para gerar bônus de exemplo

class GerarFolhaApp(tk.Toplevel):
    def __init__(self, master, db_manager):
        super().__init__(master)
        self.db_manager = db_manager

        self.title("Gerar Folha de Pagamento")
        self.geometry("600x400")
        self.configure(bg="#34495e")
        self.transient(master)

        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background="#34495e")
        style.configure('TLabel', background="#34495e", foreground="#ecf0f1", font=('Arial', 11))
        style.configure('TButton', font=('Arial', 12, 'bold'), padding=10)
        style.configure('Header.TLabel', font=('Arial', 18, 'bold'))

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="Gerar Folha de Pagamento Mensal", style='Header.TLabel').pack(pady=(0, 30))
        
        selecao_frame = ttk.Frame(main_frame)
        selecao_frame.pack(pady=10)

        meses_pt = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        self.meses_map = {nome: num + 1 for num, nome in enumerate(meses_pt)}
        
        ttk.Label(selecao_frame, text="Mês de Referência:").pack(side='left', padx=(0, 5))
        self.combo_mes = ttk.Combobox(selecao_frame, values=meses_pt, state='readonly', width=15)
        self.combo_mes.set(meses_pt[date.today().month - 1])
        self.combo_mes.pack(side='left', padx=(0, 20))

        anos = [str(y) for y in range(date.today().year, date.today().year - 3, -1)]
        ttk.Label(selecao_frame, text="Ano:").pack(side='left', padx=(0, 5))
        self.combo_ano = ttk.Combobox(selecao_frame, values=anos, state='readonly', width=8)
        self.combo_ano.set(str(date.today().year))
        self.combo_ano.pack(side='left')

        self.btn_gerar = ttk.Button(main_frame, text="Gerar Holerites para Funcionários Ativos", command=self.iniciar_geracao)
        self.btn_gerar.pack(pady=30)

        ttk.Label(main_frame, text="Status da Geração:").pack(anchor='w')
        self.log_text = tk.Text(main_frame, height=8, state='disabled', font=('Courier New', 10), bg='#ecf0f1')
        self.log_text.pack(fill='both', expand=True)
    
    def adicionar_log(self, mensagem):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{mensagem}\n")
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)
        self.update_idletasks()

    # ***** ESTA É A FUNÇÃO PRINCIPAL QUE IMPLEMENTAMOS AGORA *****
    def iniciar_geracao(self):
        mes_nome = self.combo_mes.get()
        mes_num = self.meses_map.get(mes_nome)
        ano = int(self.combo_ano.get())
        
        if not messagebox.askyesno("Confirmar Ação", 
            f"Gerar folha de pagamento para {mes_nome}/{ano} para TODOS os funcionários ativos?\n\n"
            "O sistema irá ignorar funcionários que já possuam holerite para este período.", parent=self):
            return

        # Desabilita o botão para evitar cliques duplos
        self.btn_gerar.config(state='disabled')
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state='disabled')

        self.adicionar_log(f"Iniciando geração para {mes_nome}/{ano}...")
        
        # 1. Buscar todos os funcionários ativos
        sql_funcionarios = "SELECT id, salario FROM funcionarios WHERE status = 'Ativo' ORDER BY id"
        funcionarios = self.db_manager.execute_query(sql_funcionarios)

        if not funcionarios:
            self.adicionar_log("Nenhum funcionário ativo encontrado.")
            self.btn_gerar.config(state='normal')
            return

        self.adicionar_log(f"Encontrados {len(funcionarios)} funcionários ativos.")
        holerites_gerados = 0
        funcionarios_ignorados = 0

        # 2. Loop para processar cada funcionário
        for func_id, salario_base in funcionarios:
            if salario_base is None or salario_base <= 0:
                self.adicionar_log(f"-> ID {func_id}: Salário não definido. Pulando.")
                funcionarios_ignorados += 1
                continue

            self.adicionar_log(f"-> Processando funcionário ID: {func_id}...")

            # 3. Verificar se o holerite já existe
            sql_check = "SELECT id FROM holerites WHERE funcionario_id = %s AND mes = %s AND ano = %s"
            if self.db_manager.execute_query(sql_check, (func_id, mes_num, ano)):
                self.adicionar_log("   Holerite já existe. Pulando.")
                funcionarios_ignorados += 1
                continue
            
            # 4. Calcular valores (lógica de exemplo)
            bonus = round(random.uniform(50, 250), 2)
            desconto_inss = round(float(salario_base) * 0.08, 2)
            desconto_vt = 60.00
            
            total_proventos = float(salario_base) + bonus
            total_descontos = desconto_inss + desconto_vt
            salario_liquido = total_proventos - total_descontos

            # 5. Inserir no banco de dados
            sql_holerite = "INSERT INTO holerites (funcionario_id, mes, ano, total_proventos, total_descontos, salario_liquido) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id"
            params_holerite = (func_id, mes_num, ano, total_proventos, total_descontos, salario_liquido)
            resultado = self.db_manager.execute_modificacao(sql_holerite, params_holerite, return_id=True)
            
            if resultado and isinstance(resultado, tuple):
                novo_holerite_id = resultado[0]
                
                # Inserir itens
                sql_itens = "INSERT INTO holerite_itens (holerite_id, descricao, tipo, valor) VALUES (%s, %s, %s, %s)"
                self.db_manager.execute_modificacao(sql_itens, (novo_holerite_id, 'Salário Base', 'Provento', salario_base))
                self.db_manager.execute_modificacao(sql_itens, (novo_holerite_id, 'Bônus', 'Provento', bonus))
                self.db_manager.execute_modificacao(sql_itens, (novo_holerite_id, 'INSS', 'Desconto', desconto_inss))
                self.db_manager.execute_modificacao(sql_itens, (novo_holerite_id, 'Vale Transporte', 'Desconto', desconto_vt))
                
                self.adicionar_log("   Holerite gerado com sucesso!")
                holerites_gerados += 1
            else:
                self.adicionar_log("   ERRO ao gerar holerite.")

        # Finalização
        self.adicionar_log("\n----- PROCESSO CONCLUÍDO -----")
        self.adicionar_log(f"Holerites gerados: {holerites_gerados}")
        self.adicionar_log(f"Funcionários ignorados: {funcionarios_ignorados}")
        self.btn_gerar.config(state='normal')
        messagebox.showinfo("Geração Concluída", "O processo de geração da folha de pagamento foi finalizado.", parent=self)