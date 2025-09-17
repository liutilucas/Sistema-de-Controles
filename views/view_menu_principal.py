import tkinter as tk
from tkinter import ttk, messagebox


from views.view_funcionarios import FuncionarioApp
from views.view_estoque import EstoqueApp
from views.view_gerar_folha import GerarFolhaApp 

class MainMenuApp(tk.Toplevel):
    def __init__(self, master, db_manager):
        super().__init__(master)
        self.db_manager = db_manager
        self.title("Sistema de Gestão - Painel de Controle (Admin)")
        self.geometry("800x550")
        self.configure(bg="#34495e")
        self.transient(master)
        self.setup_styles()
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def setup_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('Main.TFrame', background=self.cget('bg'))
        self.style.configure('Menu.TButton', 
                             font=('Arial', 14, 'bold'), 
                             padding=(20, 20),
                             background="#ecf0f1",
                             foreground="#34495e")
        self.style.map('Menu.TButton', background=[('active', '#bdc3c7')])

    def create_widgets(self):
        main_frame = ttk.Frame(self, style='Main.TFrame', padding=40)
        main_frame.pack(fill="both", expand=True)
        title_label = tk.Label(main_frame, text="Painel de Controle", 
                               font=("Arial", 28, "bold"), 
                               bg=self.cget('bg'), 
                               fg="#ecf0f1")
        title_label.pack(pady=(20, 50))

        btn_funcionarios = ttk.Button(main_frame, text="Gerenciar Funcionários", 
                                      style='Menu.TButton', 
                                      command=self.abrir_gestao_funcionarios)
        btn_funcionarios.pack(fill="x", pady=10)

        btn_estoque = ttk.Button(main_frame, text="Gerenciar Estoque", 
                                 style='Menu.TButton', 
                                 command=self.abrir_gestao_estoque)
        btn_estoque.pack(fill="x", pady=10)
        
        btn_gerar_folha = ttk.Button(main_frame, text="Gerar Folha de Pagamento", 
                                     style='Menu.TButton', 
                                     command=self.abrir_gerador_folha)
        btn_gerar_folha.pack(fill="x", pady=10)


    def abrir_gestao_funcionarios(self):
        win_funcionarios = FuncionarioApp(self, self.db_manager)
        win_funcionarios.grab_set()

    def abrir_gestao_estoque(self):
        win_estoque = EstoqueApp(self, self.db_manager)
        win_estoque.grab_set()
        
    def abrir_gerador_folha(self):
        win_gerar_folha = GerarFolhaApp(self, self.db_manager)
        win_gerar_folha.grab_set()