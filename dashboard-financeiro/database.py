import sqlite3
import hashlib
import secrets
import os
from datetime import datetime, timedelta
from pathlib import Path


def get_database_path() -> str:
    db_path = os.environ.get("DASHBOARD_DB_PATH")
    if db_path:
        path = Path(db_path).expanduser()
    else:
        data_dir = os.environ.get("DASHBOARD_DATA_DIR")
        base_dir = Path(data_dir).expanduser() if data_dir else Path(__file__).resolve().parent
        path = base_dir / "database.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    return str(path)


DATABASE = get_database_path()

# =========================
# HASH DE SENHA
# =========================
def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        260000,
    ).hex()
    return f"pbkdf2_sha256$260000${salt}${digest}"


def verify_password(password, stored_hash):
    if not stored_hash:
        return False
    partes = stored_hash.split("$")
    if len(partes) == 4 and partes[0] == "pbkdf2_sha256":
        _, iteracoes, salt, digest = partes
        tentativa = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iteracoes),
        ).hex()
        return secrets.compare_digest(tentativa, digest)

    # Compatibilidade com senhas gravadas antes da troca para PBKDF2.
    legado = hashlib.sha256(password.encode()).hexdigest()
    return secrets.compare_digest(legado, stored_hash)


# =========================
# CRIAR TABELAS
# =========================
def criar_tabelas():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Tabela de usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabela de contas bancárias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            nome TEXT,
            banco TEXT,
            saldo_inicial REAL,
            saldo_final REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shared_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            payload TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            revoked_at TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            code_hash TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# =========================
# USUÁRIOS
# =========================
def create_user(username, password, is_admin=False):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        password_hash = hash_password(password)

        cursor.execute("""
            INSERT INTO users (username, password, is_admin)
            VALUES (?, ?, ?)
        """, (username, password_hash, int(is_admin)))  # ✅ corrigido

        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def create_or_update_admin(username, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (username, password, is_admin)
        VALUES (?, ?, 1)
        ON CONFLICT(username) DO UPDATE SET
            password = excluded.password,
            is_admin = 1
        """,
        (username, hash_password(password)),
    )
    conn.commit()
    conn.close()
    return True


def bootstrap_admin_from_env():
    username = os.environ.get("DASHBOARD_ADMIN_USER", "").strip()
    password = os.environ.get("DASHBOARD_ADMIN_PASSWORD", "")
    if not username or not password:
        return False
    if len(username) < 3 or len(password) < 8:
        return False
    create_or_update_admin(username, password)
    return True


def login_user(username, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username, password, is_admin
        FROM users
        WHERE username = ?
    """, (username,))

    result = cursor.fetchone()
    conn.close()

    if result:
        user_id, user_name, password_db, is_admin = result

        if verify_password(password, password_db):
            if not str(password_db).startswith("pbkdf2_sha256$"):
                conn = sqlite3.connect(DATABASE)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET password = ? WHERE id = ?",
                    (hash_password(password), user_id),
                )
                conn.commit()
                conn.close()
            return (user_id, user_name, is_admin)

    return None


def verify_admin_password(user_id, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT password, is_admin
        FROM users
        WHERE id = ?
    """, (user_id,))
    result = cursor.fetchone()
    conn.close()
    return bool(
        result
        and result[1]
        and verify_password(password, result[0])
    )


def create_password_reset_code(username, valid_minutes=15):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return None

    user_id = result[0]
    code = secrets.token_hex(6).upper()
    code_hash = hashlib.sha256(code.encode("utf-8")).hexdigest()
    expires_at = (
        datetime.utcnow() + timedelta(minutes=valid_minutes)
    ).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        UPDATE password_reset_codes
        SET used_at = CURRENT_TIMESTAMP
        WHERE user_id = ? AND used_at IS NULL
    """, (user_id,))
    cursor.execute("""
        INSERT INTO password_reset_codes (user_id, code_hash, expires_at)
        VALUES (?, ?, ?)
    """, (user_id, code_hash, expires_at))
    conn.commit()
    conn.close()
    return code


def reset_password_with_code(username, code, new_password):
    code_hash = hashlib.sha256(code.strip().upper().encode("utf-8")).hexdigest()
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT password_reset_codes.id, users.id
        FROM password_reset_codes
        JOIN users ON users.id = password_reset_codes.user_id
        WHERE users.username = ?
          AND password_reset_codes.code_hash = ?
          AND password_reset_codes.used_at IS NULL
          AND datetime(password_reset_codes.expires_at) > datetime('now')
        ORDER BY password_reset_codes.created_at DESC
        LIMIT 1
    """, (username, code_hash))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return False

    reset_id, user_id = result
    cursor.execute(
        "UPDATE users SET password = ? WHERE id = ?",
        (hash_password(new_password), user_id),
    )
    cursor.execute("""
        UPDATE password_reset_codes
        SET used_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (reset_id,))
    conn.commit()
    conn.close()
    return True


def get_all_users():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, is_admin FROM users")
    users = cursor.fetchall()

    conn.close()
    return users


def delete_user_by_admin(username):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username = ? AND is_admin = 0",
        (username,),
    )
    result = cursor.fetchone()
    if not result:
        conn.close()
        return False
    user_id = result[0]
    cursor.execute("DELETE FROM password_reset_codes WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM shared_reports WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM contas WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))

    conn.commit()
    conn.close()
    return True


# =========================
# CONTAS BANCÁRIAS
# =========================
def add_conta(user_id, nome, banco, saldo_inicial, saldo_final):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO contas (user_id, nome, banco, saldo_inicial, saldo_final)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, nome, banco, saldo_inicial, saldo_final))

    conn.commit()
    conn.close()


def get_contas(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, banco, saldo_inicial, saldo_final
        FROM contas
        WHERE user_id = ?
    """, (user_id,))

    contas = cursor.fetchall()
    conn.close()
    return contas


def delete_conta(conta_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM contas WHERE id = ?", (conta_id,))

    conn.commit()
    conn.close()


# =========================
# RELATÓRIOS COMPARTILHADOS
# =========================
def create_shared_report(user_id, title, payload, expires_at=None):
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO shared_reports (
            user_id, token_hash, title, payload, expires_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, token_hash, title, payload, expires_at))
    conn.commit()
    conn.close()
    return token


def get_shared_report(token):
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, user_id, title, payload, created_at, expires_at
        FROM shared_reports
        WHERE token_hash = ?
          AND revoked_at IS NULL
          AND (expires_at IS NULL OR datetime(expires_at) > datetime('now'))
    """, (token_hash,))
    report = cursor.fetchone()
    conn.close()
    return report


def list_shared_reports(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, created_at, expires_at, revoked_at
        FROM shared_reports
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))
    reports = cursor.fetchall()
    conn.close()
    return reports


def revoke_shared_report(report_id, user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE shared_reports
        SET revoked_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ? AND revoked_at IS NULL
    """, (report_id, user_id))
    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return changed
