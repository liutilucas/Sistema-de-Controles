import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

# --- Funções de formatação ---
def formatar_cpf_cnpj(entry):
    text = entry.get().replace(".", "").replace("/", "").replace("-", "")
    text = "".join(filter(str.isdigit, text))
    
    if len(text) > 14: text = text[:14]

    if len(text) <= 11:
        entry.delete(0, tk.END)
        if len(text) > 9: text = f"{text[:3]}.{text[3:6]}.{text[6:9]}-{text[9:]}"
        elif len(text) > 6: text = f"{text[:3]}.{text[3:6]}.{text[6:]}"
        elif len(text) > 3: text = f"{text[:3]}.{text[3:]}"
        entry.insert(0, text)
    else:
        entry.delete(0, tk.END)
        if len(text) > 12: text = f"{text[:2]}.{text[2:5]}.{text[5:8]}/{text[8:12]}-{text[12:]}"
        elif len(text) > 8: text = f"{text[:2]}.{text[2:5]}.{text[5:8]}/{text[8:]}"
        elif len(text) > 5: text = f"{text[:2]}.{text[2:5]}.{text[5:]}"
        elif len(text) > 2: text = f"{text[:2]}.{text[2:]}"
        entry.insert(0, text)

class LoginApp(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.configure(bg="#34495e")
        style = ttk.Style(self)
        style.configure('Main.TFrame', background="#2c3e50")
        style.configure('Title.TLabel', background="#2c3e50", foreground="#ecf0f1", font=('Arial', 20, 'bold'))
        style.configure('Light.TLabel', background="#2c3e50", foreground="#ecf0f1", font=('Arial', 11))
        style.configure('Login.TButton', font=('Arial', 12, 'bold'), padding=10)
        form_frame = ttk.Frame(self, style='Main.TFrame', padding=(40, 60))
        form_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        title_label = ttk.Label(form_frame, text="Acesso ao Sistema", style='Title.TLabel')
        title_label.pack(pady=(0, 30))
        ttk.Label(form_frame, text="CNPJ ou CPF:", style='Light.TLabel').pack(anchor='w')
        self.entry_login = ttk.Entry(form_frame, width=30, font=('Arial', 12))
        self.entry_login.pack(pady=(5, 15))
        self.entry_login.bind("<KeyRelease>", lambda event: formatar_cpf_cnpj(self.entry_login))
        ttk.Label(form_frame, text="Senha:", style='Light.TLabel').pack(anchor='w')
        self.entry_senha = ttk.Entry(form_frame, width=30, show="*", font=('Arial', 12))
        self.entry_senha.pack(pady=(5, 20))
        btn_entrar = ttk.Button(form_frame, text="Entrar", style='Login.TButton', command=self.realizar_login)
        btn_entrar.pack(fill='x')
        self.entry_senha.bind("<Return>", self.realizar_login)

    def realizar_login(self, event=None):
        login = self.entry_login.get()
        senha = self.entry_senha.get()
        if not login or not senha:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos.", parent=self)
            return
        
        tipo_usuario, user_id = self.controller.verificar_login(login, senha)
        
        if tipo_usuario:
            self.controller.login_bem_sucedido(tipo_usuario, user_id)
        else:
            messagebox.showerror("Falha no Login", "CPF/CNPJ ou senha incorretos.", parent=self)

class AppController(tk.Tk):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        
        self.title("Sistema de Gestão")
        self.geometry("800x600")
        self.configure(bg="#34495e")
        self.eval('tk::PlaceWindow . center')
        container = tk.Frame(self, bg="#34495e")
        container.pack(fill="both", expand=True)
        self.login_frame = LoginApp(container, self)
        self.login_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.login_frame.tkraise()

    def verificar_login(self, login, senha):
        login_limpo = "".join(filter(str.isdigit, login))
        
        ADMIN_CNPJ = "123"
        ADMIN_PASS = "123"
        
        if login_limpo == ADMIN_CNPJ and senha == ADMIN_PASS:
            print("Login de Administrador bem-sucedido.")
            return 'admin', None

        elif len(login_limpo) == 11:
            sql = "SELECT id FROM funcionarios WHERE cpf = %s AND senha = %s AND status = 'Ativo'"
            params = (login_limpo, senha)
            resultado = self.db_manager.execute_query(sql, params)
            
            if resultado:
                funcionario_id = resultado[0][0]
                print(f"Login de Funcionário bem-sucedido. ID: {funcionario_id}")
                return 'funcionario', funcionario_id
        
        print("Falha na autenticação.")
        return None, None

    def login_bem_sucedido(self, tipo_usuario, funcionario_id=None):
        self.login_frame.destroy()
        if tipo_usuario == 'admin':
            from views.view_menu_principal import MainMenuApp
            main_menu = MainMenuApp(self, self.db_manager)
            main_menu.grab_set()
        
        elif tipo_usuario == 'funcionario':
                    # A linha da messagebox foi REMOVIDA
                    from views.view_portal_funcionario import PortalFuncionarioApp
                    portal = PortalFuncionarioApp(self, self.db_manager, funcionario_id)
                    portal.grab_set()

if __name__ == "__main__":
    db_manager = Database() 
    if db_manager.conn is None:
        messagebox.showerror("Erro Fatal de Conexão", "Não foi possível conectar ao banco de dados PostgreSQL.")
    else:
        app = AppController(db_manager)
        app.mainloop()
        db_manager.close_connection()

        #90909090909