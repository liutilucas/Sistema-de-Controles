import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta

try:
    from tkcalendar import DateEntry
except ImportError:
    messagebox.showerror("Biblioteca Faltando", "Execute: pip install tkcalendar")
    DateEntry = None

class JanelaProduto(tk.Toplevel):
    def __init__(self, master, db, produto_id=None, callback=None):
        super().__init__(master)
        self.db = db
        self.produto_id = produto_id
        self.callback = callback
        self.title("Adicionar/Editar Produto")
        self.geometry("400x400")
        self.transient(master)
        self.grab_set()
        self.configure(bg="#34495e")
        self.create_form_widgets()
        if self.produto_id:
            self.title("Editar Produto")
            self.carregar_dados_produto()
            
    def create_form_widgets(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        categorias = ["Bebidas", "Limpeza", "Higiene", "Alimentos", "Escritório", "Outros"]
        ttk.Label(main_frame, text="Nome do Produto (*):").pack(anchor="w")
        self.entrada_nome = ttk.Entry(main_frame, width=40)
        self.entrada_nome.pack(fill="x", pady=(0, 10))
        ttk.Label(main_frame, text="Categoria:").pack(anchor="w")
        self.combo_categoria = ttk.Combobox(main_frame, values=categorias)
        self.combo_categoria.pack(fill="x", pady=(0, 10))
        ttk.Label(main_frame, text="Descrição:").pack(anchor="w")
        self.texto_descricao = tk.Text(main_frame, height=5)
        self.texto_descricao.pack(fill="both", expand=True, pady=(0, 10))
        ttk.Label(main_frame, text="Ponto de Ressuprimento (Estoque Mínimo):").pack(anchor="w")
        self.entrada_ponto_ressuprimento = ttk.Entry(main_frame)
        self.entrada_ponto_ressuprimento.pack(fill="x", pady=(0, 10))
        botao_salvar = ttk.Button(main_frame, text="Salvar", command=self.salvar_produto)
        botao_salvar.pack(pady=10)

    def carregar_dados_produto(self):
        sql = "SELECT nome, categoria, descricao, ponto_ressuprimento FROM produtos WHERE id = %s"
        resultado = self.db.execute_query(sql, (self.produto_id,))
        if resultado:
            dados = resultado[0]
            self.entrada_nome.insert(0, dados[0])
            self.combo_categoria.set(dados[1] or "")
            self.texto_descricao.insert("1.0", dados[2] or "")
            self.entrada_ponto_ressuprimento.insert(0, str(dados[3] or "0"))

    def salvar_produto(self):
        nome = self.entrada_nome.get().strip()
        categoria = self.combo_categoria.get().strip()
        descricao = self.texto_descricao.get("1.0", "end-1c").strip()
        ponto_ressuprimento = self.entrada_ponto_ressuprimento.get().strip()
        if not nome:
            messagebox.showwarning("Validação", "O nome do produto é obrigatório.", parent=self)
            return
        try:
            ponto_ressuprimento = int(ponto_ressuprimento) if ponto_ressuprimento else 0
        except ValueError:
            messagebox.showwarning("Validação", "O ponto de ressuprimento deve ser um número.", parent=self)
            return
        dados = (nome, categoria, descricao, ponto_ressuprimento)
        if self.produto_id:
            sql = "UPDATE produtos SET nome=%s, categoria=%s, descricao=%s, ponto_ressuprimento=%s WHERE id=%s"
            params = dados + (self.produto_id,)
        else:
            sql = "INSERT INTO produtos (nome, categoria, descricao, ponto_ressuprimento) VALUES (%s, %s, %s, %s)"
            params = dados
        
        # --- AJUSTE AQUI ---
        if self.db.execute_modificacao(sql, params):
            if self.callback: self.callback()
            self.destroy()
        else:
            messagebox.showerror("Erro de Banco de Dados", "Não foi possível salvar o produto.", parent=self)

class EstoqueApp(tk.Toplevel):
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db
        self.title("Gestão de Estoque")
        self.geometry("1280x720")
        self.transient(master)
        self.grab_set()
        self.configure(bg="#34495e")
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TFrame', background="#34495e")
        self.style.configure('TLabel', background="#34495e", foreground="#ecf0f1", font=('Arial', 11))
        self.style.configure('TButton', font=('Arial', 11, 'bold'), background="#ecf0f1", foreground="#34495e")
        self.style.configure('TNotebook.Tab', font=('Arial', '12', 'bold'))
        self.style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        self.style.configure("Danger.TLabel", foreground="red", background="#34495e") 
        self.style.configure("Warning.TLabel", foreground="orange", background="#34495e")
        self.produtos_map = {}
        self.dashboard_ja_carregado = False
        self.create_widgets()

    def create_widgets(self):
        main_app_frame = ttk.Frame(self)
        main_app_frame.pack(fill="both", expand=True)
        self.notebook = ttk.Notebook(main_app_frame)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")
        self.frame_dashboard = ttk.Frame(self.notebook, padding="20")
        self.frame_produtos = ttk.Frame(self.notebook, padding="20")
        self.frame_movimentacao = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.frame_dashboard, text="Dashboard do Estoque")
        self.notebook.add(self.frame_produtos, text="Gerenciar Produtos")
        self.notebook.add(self.frame_movimentacao, text="Movimentar Estoque")
        self.criar_aba_dashboard()
        self.criar_aba_produtos()
        self.criar_aba_movimentacao()
        self.carregar_dados_iniciais()
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_selected)

    def on_tab_selected(self, event):
        tab_selecionada = self.notebook.tab(self.notebook.select(), "text")
        if tab_selecionada == "Dashboard do Estoque":
            self.atualizar_dashboard_completo()
        elif tab_selecionada == "Movimentar Estoque":
            self.carregar_lotes_estoque()

    def carregar_dados_iniciais(self):
        self.carregar_produtos()

    def criar_aba_dashboard(self):
        dash_pane = tk.PanedWindow(self.frame_dashboard, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bg="#34495e")
        dash_pane.pack(fill="both", expand=True)
        alertas_frame = ttk.Frame(dash_pane, padding=10)
        ttk.Label(alertas_frame, text="Alertas Importantes", font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 15))
        ttk.Label(alertas_frame, text="Produtos com Estoque Baixo", font=("Arial", 12, "bold"), style="Warning.TLabel").pack(anchor="w", pady=(10,5))
        cols_baixo = ("Produto", "Qtd Atual", "Qtd Mínima")
        self.tree_estoque_baixo = ttk.Treeview(alertas_frame, columns=cols_baixo, show="headings", height=5)
        self.tree_estoque_baixo.pack(fill="x", expand=True)
        for col in cols_baixo: self.tree_estoque_baixo.heading(col, text=col)
        self.tree_estoque_baixo.column("Produto", width=250); self.tree_estoque_baixo.column("Qtd Atual", width=100); self.tree_estoque_baixo.column("Qtd Mínima", width=100)
        ttk.Label(alertas_frame, text="Lotes Próximos da Validade (30 dias)", font=("Arial", 12, "bold"), style="Danger.TLabel").pack(anchor="w", pady=(20,5))
        cols_validade = ("Produto", "Qtd no Lote", "Data de Validade")
        self.tree_validade = ttk.Treeview(alertas_frame, columns=cols_validade, show="headings", height=5)
        self.tree_validade.pack(fill="x", expand=True)
        for col in cols_validade: self.tree_validade.heading(col, text=col)
        self.tree_validade.column("Produto", width=250); self.tree_validade.column("Qtd no Lote", width=100); self.tree_validade.column("Data de Validade", width=120)
        dash_pane.add(alertas_frame, width=500)
        resumo_frame = ttk.Frame(dash_pane, padding=10)
        ttk.Label(resumo_frame, text="Resumo Geral do Estoque", font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 15))
        cols_resumo = ("Produto", "Quantidade Total")
        self.tree_resumo_estoque = ttk.Treeview(resumo_frame, columns=cols_resumo, show="headings")
        self.tree_resumo_estoque.pack(fill="both", expand=True)
        for col in cols_resumo: self.tree_resumo_estoque.heading(col, text=col)
        self.tree_resumo_estoque.column("Produto", width=300); self.tree_resumo_estoque.column("Quantidade Total", width=150)
        dash_pane.add(resumo_frame)

    def criar_aba_produtos(self):
        botoes_produtos_frame = ttk.Frame(self.frame_produtos)
        botoes_produtos_frame.pack(fill="x", pady=(0, 10))
        ttk.Button(botoes_produtos_frame, text="Adicionar Novo Produto", command=self.adicionar_produto).pack(side="left")
        ttk.Button(botoes_produtos_frame, text="Editar Produto Selecionado", command=self.editar_produto).pack(side="left", padx=10)
        ttk.Button(botoes_produtos_frame, text="Excluir Produto Selecionado", command=self.excluir_produto).pack(side="left")
        colunas_produtos = ("ID", "Nome", "Categoria", "Estoque Mínimo", "Estoque Total")
        self.tree_produtos = ttk.Treeview(self.frame_produtos, columns=colunas_produtos, show="headings")
        self.tree_produtos.pack(fill="both", expand=True)
        for col in colunas_produtos: self.tree_produtos.heading(col, text=col)
        self.tree_produtos.column("ID", width=50, stretch=tk.NO); self.tree_produtos.column("Nome", width=400); self.tree_produtos.column("Categoria", width=200)

    def criar_aba_movimentacao(self):
        mov_pane = tk.PanedWindow(self.frame_movimentacao, orient=tk.VERTICAL, sashrelief=tk.RAISED, bg="#34495e")
        mov_pane.pack(fill="both", expand=True)
        form_entrada_frame = ttk.Frame(mov_pane, padding=10)
        ttk.Label(form_entrada_frame, text="Registrar Entrada de Lote", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,15))
        ttk.Label(form_entrada_frame, text="Selecione o Produto:").grid(row=1, column=0, sticky="w")
        self.combo_produtos_lote_entrada = ttk.Combobox(form_entrada_frame, width=40, state="readonly")
        self.combo_produtos_lote_entrada.grid(row=2, column=0, padx=(0, 20))
        ttk.Label(form_entrada_frame, text="Quantidade (*):").grid(row=1, column=1, sticky="w")
        self.entrada_quantidade_lote = ttk.Entry(form_entrada_frame)
        self.entrada_quantidade_lote.grid(row=2, column=1, padx=(0, 20))
        ttk.Label(form_entrada_frame, text="Data de Validade (Opcional):").grid(row=1, column=2, sticky="w")
        if DateEntry:
            self.entrada_validade_lote = DateEntry(form_entrada_frame, width=18, date_pattern='dd/mm/yyyy', locale='pt_BR')
            self.entrada_validade_lote.grid(row=2, column=2, padx=(0, 20))
            self.entrada_validade_lote.delete(0, 'end')
        else:
            self.entrada_validade_lote = ttk.Entry(form_entrada_frame)
            self.entrada_validade_lote.grid(row=2, column=2, padx=(0, 20))
        ttk.Button(form_entrada_frame, text="Registrar Entrada", command=self.registrar_entrada_lote).grid(row=2, column=3, padx=20)
        mov_pane.add(form_entrada_frame, height=120)
        form_saida_frame = ttk.Frame(mov_pane, padding=10)
        ttk.Label(form_saida_frame, text="Registrar Saída de Estoque", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", pady=(20,15))
        ttk.Label(form_saida_frame, text="Selecione o Produto:").grid(row=1, column=0, sticky="w")
        self.combo_produtos_lote_saida = ttk.Combobox(form_saida_frame, width=40, state="readonly")
        self.combo_produtos_lote_saida.grid(row=2, column=0, padx=(0, 20))
        ttk.Label(form_saida_frame, text="Quantidade a Retirar (*):").grid(row=1, column=1, sticky="w")
        self.entrada_quantidade_saida = ttk.Entry(form_saida_frame)
        self.entrada_quantidade_saida.grid(row=2, column=1, padx=(0, 20))
        ttk.Button(form_saida_frame, text="Registrar Saída", command=self.registrar_saida_estoque).grid(row=2, column=2, padx=20)
        ttk.Label(form_saida_frame, text="Lotes Atuais em Estoque (para referência)", font=("Arial", 11, "italic")).grid(row=3, column=0, columnspan=3, sticky="w", pady=(20,10))
        colunas_lotes = ("ID Lote", "Produto", "Quantidade", "Validade", "Data de Entrada")
        self.tree_lotes = ttk.Treeview(form_saida_frame, columns=colunas_lotes, show="headings", height=5)
        self.tree_lotes.grid(row=4, column=0, columnspan=4, sticky="ew", padx=0)
        for col in colunas_lotes: self.tree_lotes.heading(col, text=col)
        self.tree_lotes.column("ID Lote", width=80, stretch=tk.NO)
        mov_pane.add(form_saida_frame)

    def atualizar_dashboard_completo(self):
        self.carregar_resumo_estoque(); self.carregar_alerta_estoque_baixo(); self.carregar_alerta_validade()

    def carregar_resumo_estoque(self):
        for item in self.tree_resumo_estoque.get_children(): self.tree_resumo_estoque.delete(item)
        sql = "SELECT p.nome, SUM(l.quantidade_atual) as total FROM produtos p LEFT JOIN lotes_estoque l ON p.id = l.produto_id GROUP BY p.id, p.nome ORDER BY p.nome;"
        resumo = self.db.execute_query(sql)
        if resumo:
            for nome, total in resumo: self.tree_resumo_estoque.insert("", "end", values=(nome, int(total) if total else 0))

    def carregar_alerta_estoque_baixo(self):
        for item in self.tree_estoque_baixo.get_children(): self.tree_estoque_baixo.delete(item)
        sql = "SELECT p.nome, COALESCE(SUM(l.quantidade_atual), 0) as total, p.ponto_ressuprimento FROM produtos p LEFT JOIN lotes_estoque l ON p.id = l.produto_id GROUP BY p.id, p.nome, p.ponto_ressuprimento HAVING COALESCE(SUM(l.quantidade_atual), 0) <= p.ponto_ressuprimento AND p.ponto_ressuprimento > 0 ORDER BY total;"
        alertas = self.db.execute_query(sql)
        if alertas:
            for nome, total, minimo in alertas: self.tree_estoque_baixo.insert("", "end", values=(nome, int(total), minimo))

    def carregar_alerta_validade(self):
        for item in self.tree_validade.get_children(): self.tree_validade.delete(item)
        data_limite = date.today() + timedelta(days=30)
        sql = "SELECT p.nome, l.quantidade_atual, TO_CHAR(l.data_validade, 'DD/MM/YYYY') FROM lotes_estoque l JOIN produtos p ON l.produto_id = p.id WHERE l.data_validade IS NOT NULL AND l.data_validade <= %s ORDER BY l.data_validade;"
        alertas = self.db.execute_query(sql, (data_limite,))
        if alertas:
            for nome, qtd, validade in alertas: self.tree_validade.insert("", "end", values=(nome, qtd, validade))

    def carregar_produtos_no_combobox(self):
        sql = "SELECT id, nome FROM produtos ORDER BY nome"
        produtos = self.db.execute_query(sql)
        if produtos:
            self.produtos_map = {nome: id_prod for id_prod, nome in produtos}
            lista_nomes = list(self.produtos_map.keys())
            self.combo_produtos_lote_entrada['values'] = lista_nomes
            self.combo_produtos_lote_saida['values'] = lista_nomes
        else:
            self.produtos_map = {}; self.combo_produtos_lote_entrada['values'] = []; self.combo_produtos_lote_saida['values'] = []

    def carregar_lotes_estoque(self):
        for item in self.tree_lotes.get_children(): self.tree_lotes.delete(item)
        sql = "SELECT l.id, p.nome, l.quantidade_atual, TO_CHAR(l.data_validade, 'DD/MM/YYYY'), TO_CHAR(l.data_entrada, 'DD/MM/YYYY') FROM lotes_estoque l JOIN produtos p ON l.produto_id = p.id ORDER BY l.data_validade ASC NULLS LAST, l.data_entrada ASC"
        lotes = self.db.execute_query(sql)
        if lotes:
            for lote in lotes: self.tree_lotes.insert("", "end", values=lote)

    def registrar_entrada_lote(self):
        nome_produto = self.combo_produtos_lote_entrada.get()
        quantidade_str = self.entrada_quantidade_lote.get().strip()
        validade_str = self.entrada_validade_lote.get()
        if not nome_produto or not quantidade_str:
            messagebox.showwarning("Validação", "Produto e Quantidade são obrigatórios."); return
        try:
            quantidade = int(quantidade_str)
            if quantidade <= 0: raise ValueError
        except ValueError:
            messagebox.showwarning("Validação", "A quantidade deve ser um número inteiro positivo."); return
        produto_id = self.produtos_map.get(nome_produto)
        if not produto_id:
            messagebox.showerror("Erro", "Produto selecionado não encontrado."); return
        data_validade = None
        if validade_str:
            try: data_validade = datetime.strptime(validade_str, "%d/%m/%Y").date()
            except ValueError:
                messagebox.showwarning("Validação", "O formato da data de validade é inválido."); return
        sql = "INSERT INTO lotes_estoque (produto_id, quantidade_atual, data_validade) VALUES (%s, %s, %s)"
        params = (produto_id, quantidade, data_validade)
    
        if self.db.execute_modificacao(sql, params):
            messagebox.showinfo("Sucesso", "Entrada de lote registrada com sucesso.")
            self.carregar_lotes_estoque()
            self.carregar_produtos()
            self.combo_produtos_lote_entrada.set(''); self.entrada_quantidade_lote.delete(0, 'end'); self.entrada_validade_lote.delete(0, 'end')
        else:
            messagebox.showerror("Erro", "Não foi possível registrar a entrada do lote.")

    def registrar_saida_estoque(self):
        nome_produto = self.combo_produtos_lote_saida.get()
        quantidade_saida_str = self.entrada_quantidade_saida.get().strip()
        if not nome_produto or not quantidade_saida_str:
            messagebox.showwarning("Validação", "Produto e Quantidade são obrigatórios."); return
        try:
            quantidade_a_retirar = int(quantidade_saida_str)
            if quantidade_a_retirar <= 0: raise ValueError
        except ValueError:
            messagebox.showwarning("Validação", "A quantidade a retirar deve ser um número inteiro positivo."); return
        produto_id = self.produtos_map.get(nome_produto)
        if not produto_id:
            messagebox.showerror("Erro", "Produto selecionado não encontrado."); return

        sql_lotes = "SELECT id, quantidade_atual FROM lotes_estoque WHERE produto_id = %s ORDER BY data_validade ASC NULLS LAST, data_entrada ASC"
        lotes = self.db.execute_query(sql_lotes, (produto_id,))
        estoque_total = sum(lote[1] for lote in lotes) if lotes else 0
        if quantidade_a_retirar > estoque_total:
            messagebox.showerror("Estoque Insuficiente", f"Não há estoque suficiente. Quantidade disponível: {estoque_total}"); return

        quantidade_restante_a_retirar = quantidade_a_retirar
        for lote_id, quantidade_lote in lotes:
            if quantidade_restante_a_retirar <= 0: break
            retirar_deste_lote = min(quantidade_restante_a_retirar, quantidade_lote)
            nova_quantidade = quantidade_lote - retirar_deste_lote
            if nova_quantidade == 0:
                sql_update = "DELETE FROM lotes_estoque WHERE id = %s"
                self.db.execute_modificacao(sql_update, (lote_id,))
            else:
                sql_update = "UPDATE lotes_estoque SET quantidade_atual = %s WHERE id = %s"
                self.db.execute_modificacao(sql_update, (nova_quantidade, lote_id))
            quantidade_restante_a_retirar -= retirar_deste_lote

        messagebox.showinfo("Sucesso", f"Saída de {quantidade_a_retirar} unidade(s) de '{nome_produto}' registrada.")
        self.combo_produtos_lote_saida.set(''); self.entrada_quantidade_saida.delete(0, 'end')
        self.carregar_lotes_estoque()
        self.carregar_produtos()
        self.atualizar_dashboard_completo()

    def carregar_produtos(self):
        for item in self.tree_produtos.get_children(): self.tree_produtos.delete(item)
        sql = "SELECT p.id, p.nome, p.categoria, p.ponto_ressuprimento, COALESCE(SUM(l.quantidade_atual), 0) as total FROM produtos p LEFT JOIN lotes_estoque l ON p.id = l.produto_id GROUP BY p.id, p.nome, p.categoria, p.ponto_ressuprimento ORDER BY p.nome"
        produtos = self.db.execute_query(sql)
        if produtos:
            for p in produtos: self.tree_produtos.insert("", "end", values=p)
        self.carregar_produtos_no_combobox()

    def adicionar_produto(self):
        JanelaProduto(self, self.db, callback=self.carregar_produtos)

    def editar_produto(self):
        selecionado = self.tree_produtos.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um produto na lista para editar."); return
        produto_id = self.tree_produtos.item(selecionado[0])['values'][0]
        JanelaProduto(self, self.db, produto_id=produto_id, callback=self.carregar_produtos)

    def excluir_produto(self):
        selecionado = self.tree_produtos.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um produto na lista para excluir."); return
        item = self.tree_produtos.item(selecionado[0])
        produto_id = item['values'][0]; produto_nome = item['values'][1]
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o produto '{produto_nome}'?\n\nAVISO: Todos os lotes de estoque associados a este produto também serão excluídos."):
            sql = "DELETE FROM produtos WHERE id = %s"
            # --- AJUSTE AQUI ---
            if self.db.execute_modificacao(sql, (produto_id,)):
                messagebox.showinfo("Sucesso", "Produto excluído com sucesso.")
                self.carregar_produtos()
                self.carregar_lotes_estoque()
                self.atualizar_dashboard_completo()
            else:
                messagebox.showerror("Erro", "Não foi possível excluir o produto.")