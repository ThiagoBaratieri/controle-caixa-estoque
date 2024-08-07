import sqlite3

def create_connection():
    conn = sqlite3.connect('data/estoque_caixa.db')
    return conn