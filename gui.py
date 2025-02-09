import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
import os
import sys


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Controle de Caixa e Estoque")
        self.geometry('500x500')
        self.setup_ui()

    def get_db_path(self):
        # Obtém o caminho do diretório onde o script está sendo executado
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, 'data', 'estoque_caixa.db')

    def connect_to_database(self):
        db_path = self.get_db_path()
        print(f"Conectando ao banco de dados em: {db_path}")
        return sqlite3.connect(db_path)

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

            # Botão para registrar venda
            tk.Button(self, text="Registrar Venda", command=self.register_sale).grid(row=7, column=0, columnspan=2)

            # Botão para o relatório de vendas
            tk.Button(self, text="Relatório de Vendas", command=self.list_sales).grid(row=8, column=0, columnspan=2)

            # Botão para zerar o estoque
            tk.Button(self, text="Zerar Quantidades", command=self.reset_quantities).grid(row=9, column=0, columnspan=2)

            # Botão para editar produtos
            tk.Button(self, text="Editar Produto", command=self.edit_product).grid(row=10, column=0, columnspan=2)

    # Função para adicionar produtos
    def add_product(self):
        nome = self.nome_entry.get()
        quantidade = self.quantidade_entry.get()
        preco = self.preco_entry.get().replace(',', '.')  # Substituir vírgulas por pontos
        
        if nome and quantidade and preco:
            try:
                quantidade = int(quantidade)
                preco = float(preco)

                conn = self.connect_to_database()  # Alterado
                cursor = conn.cursor()
                cursor.execute("INSERT INTO produtos (nome, quantidade, preco) VALUES (?, ?, ?)", (nome, quantidade, preco))
                conn.commit()
                conn.close()
                
                self.nome_entry.delete(0, tk.END)
                self.quantidade_entry.delete(0, tk.END)
                self.preco_entry.delete(0, tk.END)
                messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")
                
                # Atualizar a lista de produtos no combobox
                self.load_products()

            except ValueError:
                messagebox.showerror("Erro", "Quantidade deve ser um número inteiro e preço deve ser um número válido.")
        else:
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")

    # Função para listar produtos
    def list_products(self):
        conn = self.connect_to_database()  # Alterado
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, quantidade, preco FROM produtos")
        rows = cursor.fetchall()
        conn.close()
        
        list_window = tk.Toplevel()
        list_window.title("Lista de Produtos")
        
        # Configuração da Treeview
        tree = ttk.Treeview(list_window, columns=("ID", "Nome", "Quantidade", "Preço"), show='headings')
        tree.heading("ID", text="ID", anchor="e")
        tree.heading("Nome", text="Nome", anchor="w")
        tree.heading("Quantidade", text="Quantidade")
        tree.heading("Preço", text="Preço", anchor="w")

        tree.column("ID", anchor="e")
        tree.column("Nome", anchor="w")
        tree.column("Quantidade", anchor="center")
        tree.column("Preço", anchor="w")

        tree.pack(fill=tk.BOTH, expand=True)
        
        # Inserir os dados na Treeview
        for row in rows:
            preco_formatado = f"R$ {float(row[3]):.2f}"  # Converter para float antes de formatar
            tree.insert("", tk.END, values=(row[0], row[1], row[2], preco_formatado))

        # Botão para deletar produto
        tk.Button(list_window, text="Deletar Produto", command=lambda: self.delete_product(tree)).pack()

    # Função para registrar venda
    def register_sale(self):
        produto_id = self.produto_combobox.get().split(' ')[0]  # Obtendo apenas o ID do texto
        quantidade_venda = self.quantidade_venda_entry.get()
        
        if produto_id and quantidade_venda:
            try:
                quantidade_venda = int(quantidade_venda)

                conn = self.connect_to_database()  # Alterado
                cursor = conn.cursor()
                
                cursor.execute("SELECT quantidade, preco FROM produtos WHERE id=?", (produto_id,))
                produto = cursor.fetchone()
                
                if produto:
                    nova_quantidade = produto[0] - quantidade_venda
                    if nova_quantidade >= 0:
                        total_venda = produto[1] * quantidade_venda
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

            except ValueError:
                messagebox.showerror("Erro", "A quantidade de venda deve ser um número inteiro.")
        else:
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
    
    # Função para selecionar produtos da minha lista
    def load_products(self):
        conn = self.connect_to_database()  # Alterado
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM produtos")
        produtos = cursor.fetchall()
        conn.close()

        self.produto_combobox['values'] = [f"{id} - {nome}" for id, nome in produtos]

    # Função para listar vendas
    def list_sales(self):
        conn = self.connect_to_database()  # Alterado
        cursor = conn.cursor()
        cursor.execute("SELECT produto_id, quantidade, total, data FROM vendas")
        sales = cursor.fetchall()
        conn.close()

        sales_window = tk.Toplevel()
        sales_window.title("Relatório de Vendas")

        tree = ttk.Treeview(sales_window, columns=("produto_id", "quantidade", "total", "data"), show="headings")
        tree.heading("produto_id", text="ID do Produto")
        tree.heading("quantidade", text="Quantidade Vendida")
        tree.heading("total", text="Total da Venda")
        tree.heading("data", text="Data da Venda")

        tree.column("produto_id", anchor="center")
        tree.column("quantidade", anchor="center")
        tree.column("total", anchor="center")
        tree.column("data", anchor="center")

        for sale in sales:
            tree.insert("", tk.END, values=sale)

        tree.pack()

    # Função para deletar um produto
    def delete_product(self, tree):
        # Obtém o item selecionado
        selected_item = tree.selection()

        if not selected_item:
            messagebox.showerror("Erro", "Nenhum produto selecionado.")
            return

        # Obtém os valores da linha selecionada
        item_values = tree.item(selected_item, "values")
        product_id = item_values[0]

        # Confirmação de deleção
        confirm = messagebox.askyesno("Confirmação", f"Tem certeza que deseja deletar o produto ID {product_id}?")

        if confirm:
            conn = self.connect_to_database()  # Alterado
            cursor = conn.cursor()
            cursor.execute("DELETE FROM produtos WHERE id=?", (product_id,))
            conn.commit()
            conn.close()

            # Remove o item da Treeview
            tree.delete(selected_item)
            
            # Atualiza a lista de produtos no combobox
            self.load_products()

            messagebox.showinfo("Sucesso", "Produto deletado com sucesso!")

    # Função para zerar estoque
    def reset_quantities(self):
        conn = self.connect_to_database()  # Alterado
        cursor = conn.cursor()
        cursor.execute("UPDATE produtos SET quantidade = 0")
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Quantidades de todos os produtos foram zeradas!")
        self.load_products()  # Atualiza o combobox de produtos

    # Função para editar produtos
    def edit_product(self):
        selected_product = self.produto_combobox.get()
        if not selected_product:
            messagebox.showerror("Erro", "Selecione um produto para editar.")
            return

        produto_id = selected_product.split(' ')[0]

        conn = self.connect_to_database()  # Alterado
        cursor = conn.cursor()
        cursor.execute("SELECT nome, quantidade, preco FROM produtos WHERE id=?", (produto_id,))
        produto = cursor.fetchone()
        conn.close()

        if not produto:
            messagebox.showerror("Erro", "Produto não encontrado.")
            return

        edit_window = tk.Toplevel()
        edit_window.title("Editar Produto")

        tk.Label(edit_window, text="Nome do Produto:").grid(row=0, column=0)
        nome_entry = tk.Entry(edit_window)
        nome_entry.insert(0, produto[0])
        nome_entry.grid(row=0, column=1)

        tk.Label(edit_window, text="Quantidade:").grid(row=1, column=0)
        quantidade_entry = tk.Entry(edit_window)
        quantidade_entry.insert(0, produto[1])
        quantidade_entry.grid(row=1, column=1)

        tk.Label(edit_window, text="Preço:").grid(row=2, column=0)
        preco_entry = tk.Entry(edit_window)
        preco_entry.insert(0, produto[2])
        preco_entry.grid(row=2, column=1)

        def save_changes():
            nome = nome_entry.get()
            quantidade = quantidade_entry.get()
            preco = preco_entry.get()

            if nome and quantidade and preco:
                try:
                    quantidade = int(quantidade)
                    preco = float(preco)

                    conn = self.connect_to_database()  # Alterado
                    cursor = conn.cursor()
                    cursor.execute("UPDATE produtos SET nome=?, quantidade=?, preco=? WHERE id=?", (nome, quantidade, preco, produto_id))
                    conn.commit()
                    conn.close()

                    messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
                    edit_window.destroy()
                    self.load_products()  # Atualiza o combobox de produtos
                    self.list_products()  # Atualiza a lista de produtos

                except ValueError:
                    messagebox.showerror("Erro", "Quantidade deve ser um número inteiro e preço deve ser um número válido.")
            else:
                messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")

        tk.Button(edit_window, text="Salvar", command=save_changes).grid(row=3, column=0, columnspan=2)