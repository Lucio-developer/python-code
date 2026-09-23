import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'conversations.db'

def get_connection():
    """Retorna uma conexão com o banco de dados."""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Cria as tabelas necessárias no SQLite se não existirem."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de Usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Tabela de Mensagens
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            recipient TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

# --- OPERAÇÕES DE MENSAGENS ---

def db_load_messages(user1, user2):
    """Busca o histórico de mensagens trocadas entre dois usuários."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT sender, content FROM messages 
        WHERE (sender = ? AND recipient = ?) OR (sender = ? AND recipient = ?)
        ORDER BY id ASC
    """
    cursor.execute(query, (user1, user2, user2, user1))
    rows = cursor.fetchall()
    conn.close()

    return [{'username': row[0], 'content': row[1]} for row in rows]

def db_save_message(sender, recipient, content):
    """Insere uma nova mensagem no banco de dados."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (sender, recipient, content) VALUES (?, ?, ?)",
        (sender, recipient, content)
    )
    conn.commit()
    conn.close()

# --- OPERAÇÕES DE USUÁRIOS ---

def db_create_user(username, password):
    """Cadastra um novo usuário no banco de dados."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def db_get_user_password(username):
    """Busca a senha salva de um determinado usuário."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def db_get_all_users():
    """Retorna uma lista com todos os nomes de usuários cadastrados."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]