import tkinter as tk
from tkinter import messagebox
import sqlite3

# Função para adicionar um produto
def add_product():
    nome = nome_entry.get()
    quantidade = quantidade_entry.get()
    preco = preco_entry.get()
    
    if nome and quantidade and preco:
        conn = sqlite3.connect('data/estoque_caixa.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO produtos (nome, quantidade, preco) VALUES (?, ?, ?)", (nome, quantidade, preco))
        conn.commit()
        conn.close()
        
        nome_entry.delete(0, tk.END)
        quantidade_entry.delete(0, tk.END)
        preco_entry.delete(0, tk.END)
        messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")
    else:
        messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")

# Função para listar os produtos
def list_products():
    conn = sqlite3.connect('data/estoque_caixa.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    rows = cursor.fetchall()
    conn.close()
    
    list_window = tk.Toplevel()
    list_window.title("Lista de Produtos")
    
    for row in rows:
        tk.Label(list_window, text=row).pack()

# Função para registrar vendas
def register_sale():
    produto_id = produto_id_entry.get()
    quantidade_venda = quantidade_venda_entry.get()
    
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
                
                produto_id_entry.delete(0, tk.END)
                quantidade_venda_entry.delete(0, tk.END)
                messagebox.showinfo("Sucesso", "Venda registrada com sucesso!")
            else:
                messagebox.showerror("Erro", "Quantidade insuficiente em estoque.")
        else:
            messagebox.showerror("Erro", "Produto não encontrado.")
    else:
        messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")

# Criar a janela principal (Cria e define o titulo)
root = tk.Tk()
root.title("Sistema de Controle de Caixa e Estoque")

# Adicionar os produtos (Interface)
tk.Label(root, text="Nome do Produto:").grid(row=0, column=0)
nome_entry = tk.Entry(root)
nome_entry.grid(row=0, column=1)

tk.Label(root, text="Quantidade:").grid(row=1, column=0)
quantidade_entry = tk.Entry(root)
quantidade_entry.grid(row=1, column=1)

tk.Label(root, text="Preço:").grid(row=2, column=0)
preco_entry = tk.Entry(root)
preco_entry.grid(row=2, column=1)

tk.Button(root, text="Adicionar Produto", command=add_product).grid(row=3, column=0, columnspan=2)

