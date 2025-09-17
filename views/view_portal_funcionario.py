# Arquivo: views/view_portal_funcionario.py (Com meses em Português)

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
# A importação do 'calendar' não é mais necessária

try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    messagebox.showerror("Biblioteca Faltando", "Execute: pip install python-dateutil")
    relativedelta = None

class PortalFuncionarioApp(tk.Toplevel):
    # ... (todo o início da classe continua igual) ...
    def __init__(self, master, db_manager, funcionario_id):
        super().__init__(master)
        self.db_manager = db_manager
        self.funcionario_id = funcionario_id
        
        self.title("Portal do Funcionário")
        self.geometry("900x600")
        self.configure(bg="#34495e")
        self.transient(master)
        
        self.dados_funcionario = None
        self.carregar_dados_do_banco()
        
        if not self.dados_funcionario:
            messagebox.showerror("Erro de Dados", "Não foi possível carregar os dados do funcionário.", parent=self)
            self.destroy()
            return

        self.setup_styles()
        self.create_tabs()

    def carregar_dados_do_banco(self):
        sql = "SELECT nome, cpf, funcao, departamento, salario, admissao, dia_pagamento FROM funcionarios WHERE id = %s"
        resultado = self.db_manager.execute_query(sql, (self.funcionario_id,))
        if resultado:
            colunas = ["nome", "cpf", "funcao", "departamento", "salario", "admissao", "dia_pagamento"]
            self.dados_funcionario = dict(zip(colunas, resultado[0]))
    
    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('Portal.TFrame', background="#ecf0f1")
        style.configure('Header.TLabel', background="#ecf0f1", foreground="#34495e", font=('Arial', 22, 'bold'))
        style.configure('Info.TLabel', background="#ecf0f1", foreground="#2c3e50", font=('Arial', 12))
        style.configure('Value.TLabel', background="#ecf0f1", foreground="#2980b9", font=('Arial', 12, 'bold'))
        style.configure('TNotebook.Tab', font=('Arial', 11, 'bold'))

    def create_tabs(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        self.tab_resumo = ttk.Frame(notebook, style='Portal.TFrame', padding=30)
        self.tab_holerites = ttk.Frame(notebook, style='Portal.TFrame', padding=30)
        notebook.add(self.tab_resumo, text=" Meu Resumo ")
        notebook.add(self.tab_holerites, text=" Meus Holerites ")
        self.create_resumo_widgets(self.tab_resumo)
        self.create_holerites_widgets(self.tab_holerites)

    def create_resumo_widgets(self, parent_frame):
        # ... (esta função continua igual) ...
        nome_curto = self.dados_funcionario.get('nome', '').split(' ')[0]
        header_label = ttk.Label(parent_frame, text=f"Olá, {nome_curto}!", style='Header.TLabel')
        header_label.pack(anchor='w', pady=(0, 30))
        self.criar_info_section(parent_frame, "Suas Informações")
        self.criar_info_row(self.info_frame, "Nome Completo:", self.dados_funcionario.get('nome'))
        self.criar_info_row(self.info_frame, "CPF:", self.formatar_cpf(self.dados_funcionario.get('cpf')))
        self.criar_info_section(parent_frame, "Dados do Contrato")
        self.criar_info_row(self.contract_frame, "Função/Cargo:", self.dados_funcionario.get('funcao'))
        self.criar_info_row(self.contract_frame, "Departamento:", self.dados_funcionario.get('departamento'))
        self.criar_info_row(self.contract_frame, "Data de Admissão:", self.formatar_data(self.dados_funcionario.get('admissao')))
        self.criar_info_section(parent_frame, "Financeiro")
        self.criar_info_row(self.finance_frame, "Salário Bruto:", self.formatar_salario(self.dados_funcionario.get('salario')))
        self.criar_info_row(self.finance_frame, "Próximo Pagamento:", self.calcular_proximo_pagamento())

    def create_holerites_widgets(self, parent_frame):
        selecao_frame = ttk.Frame(parent_frame, style='Portal.TFrame')
        selecao_frame.pack(fill='x', pady=(0, 20))

        # ***** MUDANÇA APLICADA AQUI *****
        # Lista de meses fixa em português para garantir consistência
        meses_pt = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        self.meses_map = {nome: num + 1 for num, nome in enumerate(meses_pt)}
        
        ttk.Label(selecao_frame, text="Mês:", style='Info.TLabel').pack(side='left', padx=(0, 5))
        self.combo_mes = ttk.Combobox(selecao_frame, values=meses_pt, state='readonly', width=15)
        self.combo_mes.set(meses_pt[date.today().month - 1]) # Pré-seleciona o mês atual
        self.combo_mes.pack(side='left', padx=(0, 20))
        
        # ... (o resto da função continua igual) ...
        ttk.Label(selecao_frame, text="Ano:", style='Info.TLabel').pack(side='left', padx=(0, 5))
        anos = [str(y) for y in range(date.today().year, date.today().year - 5, -1)]
        self.combo_ano = ttk.Combobox(selecao_frame, values=anos, state='readonly', width=8)
        self.combo_ano.set(str(date.today().year))
        self.combo_ano.pack(side='left', padx=(0, 20))

        self.btn_buscar_holerite = ttk.Button(selecao_frame, text="Buscar", command=self.buscar_holerite)
        self.btn_buscar_holerite.pack(side='left')

        resultado_frame = ttk.Frame(parent_frame, style='Portal.TFrame')
        resultado_frame.pack(fill='both', expand=True)
        colunas = ('descricao', 'tipo', 'valor')
        self.tree_holerite = ttk.Treeview(resultado_frame, columns=colunas, show='headings', height=10)
        self.tree_holerite.heading('descricao', text='Descrição')
        self.tree_holerite.heading('tipo', text='Tipo')
        self.tree_holerite.heading('valor', text='Valor (R$)')
        self.tree_holerite.column('tipo', width=120, anchor='center')
        self.tree_holerite.column('valor', width=120, anchor='e')
        self.tree_holerite.pack(fill='both', expand=True)
        
        totais_frame = ttk.Frame(parent_frame, style='Portal.TFrame', padding=(0, 10))
        totais_frame.pack(fill='x')
        self.lbl_total_proventos = ttk.Label(totais_frame, text="Total Proventos: R$ 0,00", style='Value.TLabel', font=('Arial', 11, 'bold'))
        self.lbl_total_proventos.pack(side='right')
        self.lbl_total_descontos = ttk.Label(totais_frame, text="Total Descontos: R$ 0,00", style='Value.TLabel', font=('Arial', 11, 'bold'), foreground='#c0392b')
        self.lbl_total_descontos.pack(side='right', padx=20)
        self.lbl_salario_liquido = ttk.Label(totais_frame, text="Salário Líquido: R$ 0,00", style='Value.TLabel', font=('Arial', 13, 'bold'))
        self.lbl_salario_liquido.pack(side='right', padx=20)

    def buscar_holerite(self):
        # ... (esta função continua igual) ...
        self.tree_holerite.delete(*self.tree_holerite.get_children())
        self.lbl_total_proventos.config(text="Total Proventos: R$ 0,00")
        self.lbl_total_descontos.config(text="Total Descontos: R$ 0,00")
        self.lbl_salario_liquido.config(text="Salário Líquido: R$ 0,00")

        mes_nome = self.combo_mes.get()
        mes_num = self.meses_map.get(mes_nome)
        ano = int(self.combo_ano.get())

        sql_holerite = "SELECT id, total_proventos, total_descontos, salario_liquido FROM holerites WHERE funcionario_id = %s AND mes = %s AND ano = %s"
        holerite_data = self.db_manager.execute_query(sql_holerite, (self.funcionario_id, mes_num, ano))

        if not holerite_data:
            messagebox.showinfo("Busca", "Nenhum holerite encontrado para o período selecionado.", parent=self)
            return

        holerite_id, total_proventos, total_descontos, salario_liquido = holerite_data[0]
        sql_itens = "SELECT descricao, tipo, valor FROM holerite_itens WHERE holerite_id = %s ORDER BY tipo DESC, valor DESC"
        itens_data = self.db_manager.execute_query(sql_itens, (holerite_id,))

        if itens_data:
            for item in itens_data:
                descricao, tipo, valor = item
                valor_formatado = f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                self.tree_holerite.insert("", "end", values=(descricao, tipo, valor_formatado))

        self.lbl_total_proventos.config(text=f"Total Proventos: {self.formatar_salario(total_proventos)}")
        self.lbl_total_descontos.config(text=f"Total Descontos: {self.formatar_salario(total_descontos)}")
        self.lbl_salario_liquido.config(text=f"Salário Líquido: {self.formatar_salario(salario_liquido)}")

    def criar_info_section(self, parent, title):
        # ... (esta função continua igual) ...
        section_frame = ttk.Frame(parent, style='Portal.TFrame')
        section_frame.pack(fill='x', pady=(10, 20))
        title_label = ttk.Label(section_frame, text=title, font=('Arial', 16, 'bold'), background="#ecf0f1", foreground="#34495e")
        title_label.pack(anchor='w', pady=(0, 10))
        if title == "Suas Informações": self.info_frame = section_frame
        elif title == "Dados do Contrato": self.contract_frame = section_frame
        elif title == "Financeiro": self.finance_frame = section_frame

    def criar_info_row(self, parent, label_text, value_text):
        # ... (esta função continua igual) ...
        row_frame = ttk.Frame(parent, style='Portal.TFrame')
        row_frame.pack(fill='x', pady=4)
        label = ttk.Label(row_frame, text=label_text, style='Info.TLabel', width=20)
        label.pack(side='left')
        value = ttk.Label(row_frame, text=value_text or "N/A", style='Value.TLabel')
        value.pack(side='left')

    def formatar_cpf(self, cpf):
        # ... (esta função continua igual) ...
        if not cpf or len(cpf) != 11: return cpf
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        
    def formatar_data(self, data_obj):
        # ... (esta função continua igual) ...
        if not isinstance(data_obj, date): return "N/A"
        return data_obj.strftime("%d/%m/%Y")
        
    def formatar_salario(self, salario):
        # ... (esta função continua igual) ...
        if salario is None: return "N/A"
        return f"R$ {float(salario):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
    def calcular_proximo_pagamento(self):
        # ... (esta função continua igual) ...
        dia_pgto = self.dados_funcionario.get('dia_pagamento')
        if not dia_pgto or not relativedelta: return "N/A"
        hoje = date.today()
        ano, mes = hoje.year, hoje.month
        if hoje.day > dia_pgto:
            prox_mes = hoje + relativedelta(months=1)
            ano, mes = prox_mes.year, prox_mes.month
        try:
            prox_data = date(ano, mes, dia_pgto)
            return prox_data.strftime("%d/%m/%Y")
        except ValueError:
            return "Verificar com RH"