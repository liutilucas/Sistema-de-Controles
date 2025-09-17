import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime, date
from PIL import Image, ImageTk

try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    messagebox.showerror("Biblioteca Faltando", "Execute: pip install python-dateutil")
    relativedelta = None

try:
    from tkcalendar import DateEntry
except ImportError:
    messagebox.showerror("Biblioteca Faltando", "Execute: pip install tkcalendar")
    DateEntry = None

class FuncionarioApp(tk.Toplevel):
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db
        self.title("Gestao de Funcionarios")
        self.state("zoomed")
        self.transient(master)
        self.grab_set()
        self.configure(bg="#34495e")
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TFrame', background="#34495e")
        self.style.configure('TLabel', background="#34495e", foreground="#ecf0f1", font=('Arial', 11))
        self.style.configure('TButton', font=('Arial', 11, 'bold'), background="#ecf0f1", foreground="#34495e")
        self.style.configure('TNotebook.Tab', font=('Arial', 12, 'bold'))
        self.style.configure('Dashboard.TFrame', background="#ecf0f1")
        self.style.configure('Dashboard.TLabel', background="#ecf0f1", foreground="#2c3e50", font=('Arial', 10))
        self.style.configure('Dashboard.Title.TLabel', background="#ecf0f1", foreground="#34495e", font=('Arial', 12, 'bold'))
        self.style.configure('Dashboard.Value.TLabel', background="#ecf0f1", foreground="#2980b9", font=('Arial', 11, 'bold'))
        self.funcionario_id_atual = None
        self.caminho_foto_atual = None
        self.foto_tk = None
        self.lista_ja_carregada = False
        self.create_widgets()

    def create_widgets(self):
        main_app_frame = ttk.Frame(self)
        main_app_frame.pack(fill="both", expand=True)
        self.notebook = ttk.Notebook(main_app_frame)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")
        self.barra_status = tk.Label(main_app_frame, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("Arial", 10))
        self.barra_status.pack(side=tk.BOTTOM, fill=tk.X)
        self.criar_aba_cadastro_consulta()
        self.criar_aba_listar()
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_selected)

    def on_tab_selected(self, event):
        tab_selecionada = self.notebook.tab(self.notebook.select(), "text")
        if tab_selecionada == "Listar Funcionarios" and not self.lista_ja_carregada:
            self.carregar_funcionarios()
            self.lista_ja_carregada = True

    def criar_aba_cadastro_consulta(self):
        self.frame_cadastro_consulta = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.frame_cadastro_consulta, text="Cadastrar/Consultar Funcionario")
        busca_frame = ttk.Frame(self.frame_cadastro_consulta)
        busca_frame.pack(fill="x", pady=10)
        ttk.Label(busca_frame, text="Buscar por ID ou Nome:", font=("Arial", 12)).pack(side="left", padx=(0, 10))
        self.entrada_busca = ttk.Entry(busca_frame, font=("Arial", 12), width=50)
        self.entrada_busca.pack(side="left", padx=(0,5))
        botao_buscar = ttk.Button(busca_frame, text="Buscar na Lista", command=self.buscar_funcionario)
        botao_buscar.pack(side="left")
        form_and_resumo_frame = ttk.Frame(self.frame_cadastro_consulta)
        form_and_resumo_frame.pack(fill="both", expand=True, pady=10)
        form_frame = ttk.Frame(form_and_resumo_frame, padding="10")
        form_frame.pack(side="left", fill="y", padx=(0, 20), anchor="n")
        form_frame.columnconfigure(1, weight=1)
        cargos = ["Repositor", "Almoxarifado", "Açougueiro", "Auxiliar", "Caixa", "Gerente", "Hortifrúti"]
        departamentos = ["GRU1", "GRU2", "SPO1", "SPO2", "Logística", "Administrativo", "TI Interno"]
        status_opcoes = ["Ativo", "Inativo"]
        row_num = 0
        self.criar_campo(form_frame, "Nome Completo (*):", "entrada_cadastro_nome", row=row_num); row_num += 1
        self.criar_campo(form_frame, "CPF (*):", "entrada_cadastro_cpf", row=row_num, formatar_cpf=True); row_num += 1
        self.criar_campo(form_frame, "Senha (*):", "entrada_cadastro_senha", row=row_num, show_char="*"); row_num += 1
        self.criar_campo(form_frame, "Data de Nasc.:", "entrada_cadastro_nascimento", row=row_num, tipo='calendario'); row_num += 1
        self.criar_campo(form_frame, "Data de Admissão (*):", "entrada_cadastro_admissao", row=row_num, tipo='calendario'); row_num += 1
        self.criar_campo(form_frame, "Função / Cargo (*):", "entrada_cadastro_funcao", row=row_num, opcoes=cargos); row_num += 1
        self.criar_campo(form_frame, "Departamento (*):", "entrada_cadastro_departamento", row=row_num, opcoes=departamentos); row_num += 1
        self.criar_campo(form_frame, "Salário (ex: 1500,50) (*):", "entrada_cadastro_salario", row=row_num, formatar_moeda=True); row_num += 1
        self.criar_campo_numerico(form_frame, "Dia do Pagamento (1-31) (*):", "entrada_cadastro_dia_pagamento", row=row_num); row_num += 1
        self.criar_campo(form_frame, "Status (*):", "entrada_cadastro_status", row=row_num, opcoes=status_opcoes); row_num += 1
        botoes_acao_frame = ttk.Frame(form_frame)
        botoes_acao_frame.grid(row=row_num, column=0, columnspan=2, pady=20)
        self.botao_cadastro_acao = ttk.Button(botoes_acao_frame, text="Salvar Alteracoes", command=self.cadastrar_ou_atualizar)
        self.botao_cadastro_acao.pack(side=tk.LEFT, padx=5)
        self.botao_excluir = ttk.Button(botoes_acao_frame, text="Excluir Funcionario", command=self.excluir_funcionario)
        self.botao_excluir.pack(side=tk.LEFT, padx=5)
        self.botao_limpar = ttk.Button(botoes_acao_frame, text="Limpar Formulario", command=self.limpar_campos_cadastro)
        self.botao_limpar.pack(side=tk.LEFT, padx=5)
        resumo_container = ttk.Frame(form_and_resumo_frame)
        resumo_container.pack(side="left", fill="y")
        ttk.Label(resumo_container, text="Resumo do Funcionario", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        botao_upload = ttk.Button(resumo_container, text="Carregar Foto", command=self.carregar_foto)
        botao_upload.pack(pady=(0, 10), fill='x')
        quadrado_branco = tk.Frame(resumo_container, bg="white", relief="solid", borderwidth=1)
        quadrado_branco.pack(fill="none", expand=False)
        self.foto_label = tk.Label(quadrado_branco, bg="white")
        self.foto_label.pack(side="right", anchor="ne", padx=10, pady=10)
        self.resumo_texto = tk.Text(quadrado_branco, height=12, width=40, wrap="word", font=("Arial", 11), bg="white", fg="#34495e", relief="flat", borderwidth=0)
        self.resumo_texto.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.resumo_texto.tag_configure("spacing", spacing1=5, spacing2=5)
        self.limpar_campos_cadastro()

    def criar_aba_listar(self):
        self.frame_listar = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.frame_listar, text="Listar Funcionarios")
        main_pane = tk.PanedWindow(self.frame_listar, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bg="#34495e")
        main_pane.pack(fill="both", expand=True)
        lista_container = ttk.Frame(main_pane, padding=5)
        filtro_frame = ttk.Frame(lista_container)
        filtro_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(filtro_frame, text="Filtrar por nome/ID/CPF:", font=("Arial", 12)).pack(side="left", padx=(0, 10))
        self.entrada_listar_busca = ttk.Entry(filtro_frame, width=30, font=("Arial", 12))
        self.entrada_listar_busca.pack(side="left", fill="x", expand=True)
        self.entrada_listar_busca.bind("<KeyRelease>", self.filtrar_funcionarios_ao_vivo)
        colunas = ("ID", "Nome", "CPF", "Funcao")
        self.tree = ttk.Treeview(lista_container, columns=colunas, show="headings")
        self.tree.pack(fill="both", expand=True)
        for col in colunas:
            self.tree.heading(col, text=col)
        self.tree.column("ID", width=60, stretch=tk.NO)
        self.tree.bind("<<TreeviewSelect>>", self.on_single_click_select)
        self.tree.bind("<Double-1>", self.on_double_click_select)
        main_pane.add(lista_container, width=800)
        self.criar_painel_dashboard(main_pane)

    def criar_painel_dashboard(self, parent):
        dashboard_frame = ttk.Frame(parent, style='Dashboard.TFrame', padding=20)
        ttk.Label(dashboard_frame, text="Dashboard do Funcionario", style='Dashboard.Title.TLabel').pack(pady=(0, 20), anchor="w")
        self.dash_nome = self.criar_kpi(dashboard_frame, "Nome:")
        self.dash_status = self.criar_kpi(dashboard_frame, "Status:")
        self.dash_departamento = self.criar_kpi(dashboard_frame, "Departamento:")
        self.dash_tempo_casa = self.criar_kpi(dashboard_frame, "Tempo de Casa:")
        self.dash_idade = self.criar_kpi(dashboard_frame, "Idade:")
        self.dash_aniversario = self.criar_kpi(dashboard_frame, "Aniversario:")
        self.dash_proximo_pgto = self.criar_kpi(dashboard_frame, "Proximo Pagamento:")
        self.dash_custo_anual = self.criar_kpi(dashboard_frame, "Custo Anual (Est.):")
        parent.add(dashboard_frame)

    def criar_kpi(self, parent, label_text):
        frame = ttk.Frame(parent, style='Dashboard.TFrame')
        frame.pack(fill="x", pady=5)
        ttk.Label(frame, text=label_text, style='Dashboard.TLabel', width=18, anchor="w").pack(side="left")
        value_label = ttk.Label(frame, text="-", style='Dashboard.Value.TLabel')
        value_label.pack(side="left", padx=5)
        return value_label

    def on_single_click_select(self, event):
        selected_items = self.tree.selection()
        if not selected_items: return
        id_funcionario = self.tree.item(selected_items[0])['values'][0]
        sql = "SELECT nome, admissao, salario, dia_pagamento, data_nascimento, departamento, status FROM funcionarios WHERE id = %s;"
        dados = self.db.execute_query(sql, (id_funcionario,))
        if dados: self.atualizar_dashboard_funcionario(dados[0])

    def on_double_click_select(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id: return
        id_funcionario = self.tree.item(item_id)['values'][0]
        sql = "SELECT id, nome, cpf, senha, admissao, funcao, salario, dia_pagamento, pagamento_realizado, foto_path, data_nascimento, departamento, status FROM funcionarios WHERE id = %s;"
        resultado = self.db.execute_query(sql, (id_funcionario,))
        if resultado:
            self.preencher_form_com_dados(resultado[0])
            self.notebook.select(self.frame_cadastro_consulta)

    def atualizar_dashboard_funcionario(self, dados):
        nome, admissao, salario, dia_pgto, data_nasc, depto, status = dados
        self.dash_nome.config(text=nome)
        self.dash_status.config(text=status or "N/A")
        if status == 'Ativo': self.dash_status.configure(foreground="#27ae60")
        elif status == 'Inativo': self.dash_status.configure(foreground="#c0392b")
        else: self.dash_status.configure(foreground="#2980b9")
        self.dash_departamento.config(text=depto or "N/A")
        admissao_date = None
        if isinstance(admissao, date): admissao_date = admissao
        elif isinstance(admissao, str):
            try: admissao_date = datetime.strptime(admissao, '%Y-%m-%d').date()
            except ValueError: admissao_date = None
        if isinstance(data_nasc, date) and relativedelta:
            hoje = date.today()
            idade = relativedelta(hoje, data_nasc)
            self.dash_idade.config(text=f"{idade.years} anos")
            niver_este_ano = date(hoje.year, data_nasc.month, data_nasc.day)
            prox_niver = niver_este_ano if niver_este_ano >= hoje else date(hoje.year + 1, data_nasc.month, data_nasc.day)
            self.dash_aniversario.config(text=prox_niver.strftime("%d/%m"))
        else:
            self.dash_idade.config(text="N/A"); self.dash_aniversario.config(text="N/A")
        if relativedelta and admissao_date:
            hoje = date.today()
            rd = relativedelta(hoje, admissao_date)
            self.dash_tempo_casa.config(text=f"{rd.years}a, {rd.months}m, {rd.days}d")
        else:
            self.dash_tempo_casa.config(text="N/A")
        if dia_pgto and 1 <= dia_pgto <= 31 and relativedelta:
            hoje = date.today()
            ano, mes = hoje.year, hoje.month
            if hoje.day > dia_pgto:
                prox_mes = hoje + relativedelta(months=1)
                ano, mes = prox_mes.year, prox_mes.month
            try:
                prox_data = date(ano, mes, dia_pgto)
                self.dash_proximo_pgto.config(text=prox_data.strftime("%d/%m/%Y"))
            except ValueError: self.dash_proximo_pgto.config(text="Dia Invalido")
        else:
            self.dash_proximo_pgto.config(text="N/A")
        if salario is not None:
            try:
                salario_float = float(salario)
                if salario_float > 0:
                    custo = salario_float * 13.33
                    self.dash_custo_anual.config(text=f"R$ {custo:,.2f}")
                else: self.dash_custo_anual.config(text="R$ 0,00")
            except (ValueError, TypeError): self.dash_custo_anual.config(text="N/A")
        else:
            self.dash_custo_anual.config(text="N/A")

    def criar_campo(self, parent_frame, label_text, entry_name, row, show_char=None, formatar_cpf=False, formatar_moeda=False, opcoes=None, tipo='texto'):
        ttk.Label(parent_frame, text=label_text).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        entry = None
        if tipo == 'calendario':
            if DateEntry:
                entry = DateEntry(parent_frame, width=38, font=("Arial", 9), date_pattern='dd/mm/yyyy', locale='pt_BR')
            else:
                entry = ttk.Entry(parent_frame, width=40, font=("Arial", 11))
        elif opcoes:
            entry = ttk.Combobox(parent_frame, values=opcoes, font=("Arial", 11), width=38, state="readonly")
        else:
            entry = ttk.Entry(parent_frame, width=40, font=("Arial", 11), show=show_char)
        entry.grid(row=row, column=1, sticky="ew", pady=5)
        setattr(self, entry_name, entry)
        if tipo != 'calendario':
             entry.bind("<FocusOut>", self.atualizar_resumo)
        if formatar_moeda: entry.bind("<KeyRelease>", lambda event: self.formatar_moeda(entry))
        if formatar_cpf: entry.bind("<KeyRelease>", lambda event: self.formatar_cpf(entry))

    def criar_campo_numerico(self, parent_frame, label_text, entry_name, row):
        ttk.Label(parent_frame, text=label_text).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        entry = ttk.Entry(parent_frame, width=40, font=("Arial", 11))
        entry.grid(row=row, column=1, sticky="ew", pady=5)
        setattr(self, entry_name, entry)
        entry.bind("<KeyRelease>", lambda event: self.formatar_numero(entry))
        entry.bind("<FocusOut>", self.atualizar_resumo)

    def mostrar_status(self, mensagem, tipo="info"):
        cores = {"sucesso": "#27ae60", "erro": "#c0392b", "info": "#2c3e50"}
        self.barra_status.config(text=f"  {mensagem}", fg="white", bg=cores.get(tipo, "black"))
        self.after(5000, self.limpar_status)

    def limpar_status(self):
        self.barra_status.config(text="", bg=self.cget('bg'))

    def carregar_foto(self):
        caminho_arquivo = filedialog.askopenfilename(filetypes=[("Arquivos de Imagem", "*.jpg *.jpeg *.png")])
        if caminho_arquivo:
            self.caminho_foto_atual = caminho_arquivo
            self.exibir_foto(caminho_arquivo)

    def exibir_foto(self, caminho):
        try:
            img = Image.open(caminho)
            img = img.resize((120, 160), Image.Resampling.LANCZOS)
            self.foto_tk = ImageTk.PhotoImage(img)
            self.foto_label.config(image=self.foto_tk)
        except Exception as e:
            self.mostrar_status(f"Erro ao carregar imagem: {e}", "erro")
            self.limpar_foto()

    def limpar_foto(self):
        self.foto_label.config(image="")
        self.foto_tk = None
        self.caminho_foto_atual = None

    def atualizar_resumo(self, event=None):
        resumo = f"Nome: {self.entrada_cadastro_nome.get()}\n"
        resumo += f"CPF: {self.entrada_cadastro_cpf.get()}\n"
        resumo += f"Status: {self.entrada_cadastro_status.get()}\n"
        resumo += f"Departamento: {self.entrada_cadastro_departamento.get()}\n"
        resumo += f"Funcao: {self.entrada_cadastro_funcao.get()}\n"
        resumo += f"Data de Nasc.: {self.entrada_cadastro_nascimento.get()}\n"
        resumo += f"Admissao: {self.entrada_cadastro_admissao.get()}\n"
        resumo += f"Salario: {self.entrada_cadastro_salario.get()}\n"
        resumo += f"Dia de Pagamento: {self.entrada_cadastro_dia_pagamento.get()}"
        self.resumo_texto.config(state=tk.NORMAL)
        self.resumo_texto.delete("1.0", tk.END)
        self.resumo_texto.insert("1.0", resumo, "spacing")
        self.resumo_texto.config(state=tk.DISABLED)

    def formatar_cpf(self, entry):
        entry.unbind("<KeyRelease>")
        pos = entry.index(tk.INSERT)
        len_antigo = len(entry.get())
        conteudo = ''.join(filter(str.isdigit, entry.get()))[:11]
        novo_cpf = ""
        if len(conteudo) > 9: novo_cpf = f"{conteudo[:3]}.{conteudo[3:6]}.{conteudo[6:9]}-{conteudo[9:]}"
        elif len(conteudo) > 6: novo_cpf = f"{conteudo[:3]}.{conteudo[3:6]}.{conteudo[6:]}"
        elif len(conteudo) > 3: novo_cpf = f"{conteudo[:3]}.{conteudo[3:]}"
        else: novo_cpf = conteudo
        len_novo = len(novo_cpf)
        entry.delete(0, tk.END); entry.insert(0, novo_cpf)
        pos += (len_novo - len_antigo)
        entry.icursor(pos)
        entry.bind("<KeyRelease>", lambda event: self.formatar_cpf(entry))
    
    def formatar_numero(self, entry):
        entry.unbind("<KeyRelease>")
        pos = entry.index(tk.INSERT)
        conteudo = ''.join(filter(str.isdigit, entry.get()))
        entry.delete(0, tk.END); entry.insert(0, conteudo); entry.icursor(pos)
        entry.bind("<KeyRelease>", lambda event: self.formatar_numero(entry))

    def formatar_moeda(self, entry):
        entry.unbind("<KeyRelease>")
        pos = entry.index(tk.INSERT)
        len_antigo = len(entry.get())
        conteudo = ''.join(filter(str.isdigit, entry.get()))
        valor_formatado = ""
        if conteudo:
            valor_decimal = float(conteudo) / 100
            valor_formatado = f"R$ {valor_decimal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        len_novo = len(valor_formatado)
        entry.delete(0, tk.END); entry.insert(0, valor_formatado)
        pos += (len_novo - len_antigo)
        entry.icursor(pos)
        entry.bind("<KeyRelease>", lambda event: self.formatar_moeda(entry))

    def carregar_funcionarios(self, query=None):
        for item in self.tree.get_children(): self.tree.delete(item)
        sql_base = "SELECT id, nome, cpf, funcao FROM funcionarios"
        if query:
            sql = f"{sql_base} WHERE lower(nome) LIKE %s OR CAST(id AS TEXT) LIKE %s OR cpf LIKE %s ORDER BY nome;"
            params = (f'%{query.lower()}%', f'%{query.lower()}%', f'%{query.lower()}%')
        else:
            sql = f"{sql_base} ORDER BY nome;"
            params = None
        funcionarios = self.db.execute_query(sql, params)
        if funcionarios:
            for func in funcionarios: self.tree.insert("", tk.END, values=func)
    
    def filtrar_funcionarios_ao_vivo(self, event):
        self.carregar_funcionarios(self.entrada_listar_busca.get().strip())

    def buscar_funcionario(self):
        query = self.entrada_busca.get().strip()
        if not query:
            messagebox.showwarning("Atencao", "Insira um ID ou nome para buscar.")
            return
        self.notebook.select(self.frame_listar)
        self.entrada_listar_busca.delete(0, tk.END)
        self.entrada_listar_busca.insert(0, query)
        self.carregar_funcionarios(query)
        self.mostrar_status(f"Resultados para '{query}' exibidos. De um duplo-clique para carregar e editar.", "info")

    def preencher_form_com_dados(self, dados):
        self.limpar_campos_cadastro()
        (self.funcionario_id_atual, nome, cpf, senha, admissao, funcao, 
         salario, dia_pagamento, pagamento_realizado, foto_path, 
         data_nascimento, departamento, status) = dados
        
        self.entrada_cadastro_nome.insert(0, nome or "")
        self.entrada_cadastro_cpf.insert(0, cpf or "")
        self.entrada_cadastro_senha.insert(0, senha or "")
        
        if data_nascimento and isinstance(data_nascimento, date):
            self.entrada_cadastro_nascimento.set_date(data_nascimento)
        if admissao and isinstance(admissao, date):
            self.entrada_cadastro_admissao.set_date(admissao)
            
        self.entrada_cadastro_funcao.set(funcao or "")
        self.entrada_cadastro_departamento.set(departamento or "")
        self.entrada_cadastro_status.set(status or "Ativo")
        if salario is not None: self.entrada_cadastro_salario.insert(0, f"R$ {salario:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        self.entrada_cadastro_dia_pagamento.insert(0, str(dia_pagamento or ""))
        if foto_path: 
            self.caminho_foto_atual = foto_path
            self.exibir_foto(foto_path)
        self.botao_cadastro_acao.config(text=f"Salvar (ID: {self.funcionario_id_atual})")
        self.atualizar_resumo()

    def cadastrar_ou_atualizar(self):
        nascimento_str = self.entrada_cadastro_nascimento.get()
        admissao_str = self.entrada_cadastro_admissao.get()

        campos = {
            "nome": self.entrada_cadastro_nome.get().strip(), "cpf": self.entrada_cadastro_cpf.get().strip(),
            "senha": self.entrada_cadastro_senha.get().strip(), 
            "admissao": self.entrada_cadastro_admissao.get_date() if admissao_str else None,
            "funcao": self.entrada_cadastro_funcao.get().strip(), "salario_str": self.entrada_cadastro_salario.get().strip().replace("R$", "").replace(".", "").replace(",", ".").strip(),
            "dia_pagamento_str": self.entrada_cadastro_dia_pagamento.get().strip(), 
            "nascimento": self.entrada_cadastro_nascimento.get_date() if nascimento_str else None,
            "departamento": self.entrada_cadastro_departamento.get().strip(), "status": self.entrada_cadastro_status.get().strip()
        }
        
        campos_obrigatorios = {k: v for k, v in campos.items() if k not in ["nascimento", "senha"]}
        if not all(campos_obrigatorios.values()):
            messagebox.showwarning("Dados Incompletos", "Erro: Todos os campos com (*) sao obrigatorios.")
            return

        cpf_numerico = ''.join(filter(str.isdigit, campos["cpf"]))
        if len(cpf_numerico) != 11:
            messagebox.showwarning("Dados Invalidos", "Erro: O CPF deve conter exatamente 11 digitos.")
            return
            
        try:
            admissao = campos["admissao"]
            data_nascimento = campos["nascimento"]
            if admissao > date.today():
                messagebox.showwarning("Dados Invalidos", "Erro: A data de admissao nao pode ser uma data futura.")
                return
            salario = float(campos["salario_str"])
            dia_pagamento = int(campos["dia_pagamento_str"])
            if not 1 <= dia_pagamento <= 31:
                messagebox.showwarning("Dados Invalidos", "Erro: O dia do pagamento deve ser um numero entre 1 e 31.")
                return
        except (ValueError, TypeError):
            messagebox.showwarning("Dados Invalidos", "Erro: Verifique o Salario ou Dia do Pagamento.")
            return

        foto_a_salvar = self.caminho_foto_atual
        if self.funcionario_id_atual:
            sql = "UPDATE funcionarios SET nome=%s, cpf=%s, senha=%s, admissao=%s, funcao=%s, salario=%s, dia_pagamento=%s, foto_path=%s, data_nascimento=%s, departamento=%s, status=%s WHERE id=%s;"
            params = (campos["nome"], cpf_numerico, campos["senha"], admissao, campos["funcao"], salario, dia_pagamento, foto_a_salvar, data_nascimento, campos["departamento"], campos["status"], self.funcionario_id_atual)
            msg = f"Funcionario '{campos['nome']}' atualizado com sucesso!"
            return_id_flag = False
        else:
            sql = "INSERT INTO funcionarios (nome, cpf, senha, admissao, funcao, salario, dia_pagamento, pagamento_realizado, foto_path, data_nascimento, departamento, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;"
            params = (campos["nome"], cpf_numerico, campos["senha"], admissao, campos["funcao"], salario, dia_pagamento, False, foto_a_salvar, data_nascimento, campos["departamento"], campos["status"])
            msg = f"Funcionario '{campos['nome']}' cadastrado com sucesso!"
            return_id_flag = True
            
        resultado = self.db.execute_modificacao(sql, params, return_id=return_id_flag)
        if resultado:
            self.mostrar_status(msg, "sucesso")
            self.limpar_campos_cadastro()
            self.carregar_funcionarios()
            if not self.funcionario_id_atual and isinstance(resultado, tuple):
                novo_id = resultado[0]
                self.notebook.select(self.frame_listar)
                self.after(100, lambda: self.selecionar_funcionario_na_lista(novo_id))
        else:
            self.mostrar_status("Erro ao salvar no banco de dados.", "erro")

    def selecionar_funcionario_na_lista(self, id_alvo):
        for item_id in self.tree.get_children():
            item = self.tree.item(item_id)
            if item['values'][0] == id_alvo:
                self.tree.selection_set(item_id)
                self.tree.focus(item_id)
                self.tree.see(item_id)
                return

    def excluir_funcionario(self):
        if not self.funcionario_id_atual:
            messagebox.showwarning("Atencao", "Busque e selecione um funcionario para excluir.")
            return
        if messagebox.askyesno("Confirmacao", f"Excluir o funcionario ID {self.funcionario_id_atual}?"):
            sql, params = "DELETE FROM funcionarios WHERE id=%s;", (self.funcionario_id_atual,)
            if self.db.execute_modificacao(sql, params):
                self.mostrar_status("Funcionario excluido com sucesso!", "sucesso")
                self.limpar_campos_cadastro(); self.carregar_funcionarios()
            else:
                self.mostrar_status("Nao foi possivel excluir o funcionario.", "erro")

    def limpar_campos_cadastro(self):
        self.funcionario_id_atual = None
        self.entrada_busca.delete(0, tk.END)
        entradas = [
            self.entrada_cadastro_nome, self.entrada_cadastro_cpf, self.entrada_cadastro_senha,
            self.entrada_cadastro_funcao, self.entrada_cadastro_salario,
            self.entrada_cadastro_dia_pagamento,
            self.entrada_cadastro_departamento, self.entrada_cadastro_status
        ]
        for widget in entradas:
            if isinstance(widget, ttk.Combobox): widget.set('')
            elif isinstance(widget, tk.Text): widget.delete("1.0", tk.END)
            else: widget.delete(0, tk.END)
        
        if DateEntry:
            self.entrada_cadastro_nascimento.delete(0, tk.END)
            self.entrada_cadastro_admissao.delete(0, tk.END)

        self.limpar_foto()
        self.botao_cadastro_acao.config(text="Cadastrar Novo Funcionario")
        self.atualizar_resumo()