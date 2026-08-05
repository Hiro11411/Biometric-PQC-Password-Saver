#Database connection, start after completely debugging original code.
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "vault.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_vault_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS vault_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            username TEXT NOT NULL,
            encrypted_password BLOB NOT NULL,
            nonce BLOB NOT NULL,
            tag BLOB NOT NULL,
            user_id INTEGER NOT NULL
        )
        """
    )
    conn.commit()


def insert_entry(conn, user_id, service, username, encrypted_password, nonce, tag):
    # TODO: implement
    pass


def get_all_entries(conn, user_id):
    # TODO: implement
    pass


def update_entry(conn, entry_id, encrypted_password, nonce, tag):
    # TODO: implement
    pass


def delete_entry(conn, entry_id):
    # TODO: implement
    pass
