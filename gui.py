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
    


