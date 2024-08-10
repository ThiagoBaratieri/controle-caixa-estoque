import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Controle de Caixa e Estoque")
        self.setup_ui()

    def setup_ui(self):
        # Adicionar os produtos (Interface)
        tk.Label(self, text="Nome do Produto:").grid(row=0, column=0)
        self.nome_entry = tk.Entry(self)
        self.nome_entry.grid(row=0, column=1)

        tk.Label(self, text="Quantidade:").grid(row=1, column=0)
        self.quantidade_entry = tk.Entry(self)
        self.quantidade_entry.grid(row=1, column=1)

        tk.Label(self, text="Preço:").grid(row=2, column=0)
        self.preco_entry = tk.Entry(self)
        self.preco_entry.grid(row=2, column=1)

        tk.Button(self, text="Adicionar Produto", command=self.add_product).grid(row=3, column=0, columnspan=2)

        # Listar os produtos (Interface)
        tk.Button(self, text="Listar Produtos", command=self.list_products).grid(row=4, column=0, columnspan=2)

        # Registrar vendas
        tk.Label(self, text="Produto:").grid(row=5, column=0)
        self.produto_combobox = ttk.Combobox(self)
        self.produto_combobox.grid(row=5, column=1)
        self.load_products()

        tk.Label(self, text="Quantidade:").grid(row=6, column=0)
        self.quantidade_venda_entry = tk.Entry(self)
        self.quantidade_venda_entry.grid(row=6, column=1)

        tk.Button(self, text="Registrar Venda", command=self.register_sale).grid(row=7, column=0, columnspan=2)

    # Função para adicionar produtos
    def add_product(self):
        nome = self.nome_entry.get()
        quantidade = self.quantidade_entry.get()
        preco = self.preco_entry.get()
        
        if nome and quantidade and preco:
            conn = sqlite3.connect('data/estoque_caixa.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO produtos (nome, quantidade, preco) VALUES (?, ?, ?)", (nome, quantidade, preco))
            conn.commit()
            conn.close()
            
            self.nome_entry.delete(0, tk.END)
            self.quantidade_entry.delete(0, tk.END)
            self.preco_entry.delete(0, tk.END)
            messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")
        else:
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")

    # Função para listar produtos
    def list_products(self):
        conn = sqlite3.connect('data/estoque_caixa.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, quantidade, preco FROM produtos")
        rows = cursor.fetchall()
        conn.close()
        
        list_window = tk.Toplevel()
        list_window.title("Lista de Produtos")
        
        # Configuração da Treeview
        tree = ttk.Treeview(list_window, columns=("ID", "Nome", "Quantidade", "Preço"), show='headings')
        tree.heading("ID", text="ID")
        tree.heading("Nome", text="Nome")
        tree.heading("Quantidade", text="Quantidade")
        tree.heading("Preço", text="Preço")
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Inserir os dados na Treeview
        for row in rows:
            tree.insert("", tk.END, values=row)

    # Função para registrar produtos
    def register_sale(self):
        produto_id = self.produto_combobox.get().split(' ')[0]  # Obtendo apenas o ID do texto
        quantidade_venda = self.quantidade_venda_entry.get()
        
        if produto_id and quantidade_venda:
            conn = sqlite3.connect('data/estoque_caixa.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT quantidade, preco FROM produtos WHERE id=?", (produto_id,))
            produto = cursor.fetchone()
            
            if produto:
                nova_quantidade = produto[0] - int(quantidade_venda)
                if nova_quantidade >= 0:
                    total_venda = produto[1] * int(quantidade_venda)
                    cursor.execute("UPDATE produtos SET quantidade=? WHERE id=?", (nova_quantidade, produto_id))
                    cursor.execute("INSERT INTO vendas (produto_id, quantidade, total, data) VALUES (?, ?, ?, datetime('now'))", (produto_id, quantidade_venda, total_venda))
                    conn.commit()
                    conn.close()
                    
                    self.quantidade_venda_entry.delete(0, tk.END)
                    messagebox.showinfo("Sucesso", "Venda registrada com sucesso!")
                else:
                    messagebox.showerror("Erro", "Quantidade insuficiente em estoque.")
            else:
                messagebox.showerror("Erro", "Produto não encontrado.")
        else:
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
    
    # Função para selecionar produtos da minha lista
    def load_products(self):
        conn = sqlite3.connect('data/estoque_caixa.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM produtos")
        produtos = cursor.fetchall()
        conn.close()

        self.produto_combobox['values'] = [f"{id} - {nome}" for id, nome in produtos]

# Criar e iniciar o aplicativo
if __name__ == "__main__":
    app = Application()
    app.mainloop()
