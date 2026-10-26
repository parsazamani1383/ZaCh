
import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent / "docchat.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id)
                    REFERENCES conversations(id)
                    ON DELETE CASCADE
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS conversation_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (conversation_id)
                    REFERENCES conversations(id)
                    ON DELETE CASCADE,
                UNIQUE (conversation_id, file_path)
            )
        """)


def create_conversation(title="گفت‌وگوی جدید"):
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO conversations (title) VALUES (?)",
            (title,),
        )
        return cursor.lastrowid


def get_conversations():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, title, created_at, updated_at
            FROM conversations
            ORDER BY updated_at DESC, id DESC
            """
        ).fetchall()

        return [dict(row) for row in rows]

def rename_conversation(conversation_id, new_title):
    new_title = new_title.strip()

    if not new_title:
        return False

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE conversations
            SET title = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (new_title, conversation_id),
        )

        return cursor.rowcount > 0


def delete_conversation(conversation_id):
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM conversations WHERE id = ?",
            (conversation_id,),
        )

        return cursor.rowcount > 0

def save_message(conversation_id, role, content):
    if role not in ("user", "assistant"):
        raise ValueError("نقش پیام باید user یا assistant باشد.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO messages (conversation_id, role, content)
            VALUES (?, ?, ?)
            """,
            (conversation_id, role, content),
        )

        connection.execute(
            """
            UPDATE conversations
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (conversation_id,),
        )

        return cursor.lastrowid


def get_messages(conversation_id):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, conversation_id, role, content, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
            """,
            (conversation_id,),
        ).fetchall()

        return [dict(row) for row in rows]

def save_document(conversation_id, file_path, content):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO conversation_documents (
                conversation_id,
                file_path,
                content
            )
            VALUES (?, ?, ?)
            ON CONFLICT(conversation_id, file_path)
            DO UPDATE SET content = excluded.content
            """,
            (conversation_id, str(file_path), content),
        )


def get_documents(conversation_id):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT file_path, content
            FROM conversation_documents
            WHERE conversation_id = ?
            ORDER BY id ASC
            """,
            (conversation_id,),
        ).fetchall()

        return {
            row["file_path"]: row["content"]
            for row in rows
        }


def delete_document(conversation_id, file_path):
    delete_document_index(conversation_id, file_path)

    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM conversation_documents
            WHERE conversation_id = ? AND file_path = ?
            """,
            (conversation_id, str(file_path)),
        )

        return cursor.rowcount > 0


# ---------------------------------------------------------------------------
# RAG: تکه‌های سند، بردارها و خلاصه‌ها
# ---------------------------------------------------------------------------

_rag_tables_ready = False


def ensure_rag_tables():
    """جدول‌های RAG را (در صورت نبودن) می‌سازد. روی دیتابیس قبلی هم کار می‌کند."""
    global _rag_tables_ready

    if _rag_tables_ready:
        return

    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                embedding BLOB,
                FOREIGN KEY (conversation_id)
                    REFERENCES conversations(id)
                    ON DELETE CASCADE
            )
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_document_chunks_doc
            ON document_chunks (conversation_id, file_path)
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS document_summaries (
                conversation_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                summary TEXT NOT NULL,
                PRIMARY KEY (conversation_id, file_path),
                FOREIGN KEY (conversation_id)
                    REFERENCES conversations(id)
                    ON DELETE CASCADE
            )
        """)

    _rag_tables_ready = True


def replace_chunks(conversation_id, file_path, chunks):
    """chunks: فهرستی از (text, embedding_bytes_or_None)."""
    ensure_rag_tables()

    with get_connection() as connection:
        connection.execute(
            "DELETE FROM document_chunks "
            "WHERE conversation_id = ? AND file_path = ?",
            (conversation_id, str(file_path)),
        )
        connection.executemany(
            """
            INSERT INTO document_chunks (
                conversation_id, file_path, chunk_index, text, embedding
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (conversation_id, str(file_path), index, text, embedding)
                for index, (text, embedding) in enumerate(chunks)
            ],
        )


def has_chunks(conversation_id, file_path):
    ensure_rag_tables()

    with get_connection() as connection:
        row = connection.execute(
            "SELECT 1 FROM document_chunks "
            "WHERE conversation_id = ? AND file_path = ? LIMIT 1",
            (conversation_id, str(file_path)),
        ).fetchone()

        return row is not None


def get_chunks(conversation_id):
    ensure_rag_tables()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT file_path, chunk_index, text, embedding
            FROM document_chunks
            WHERE conversation_id = ?
            ORDER BY id ASC
            """,
            (conversation_id,),
        ).fetchall()

        return [dict(row) for row in rows]


def save_summary(conversation_id, file_path, summary):
    ensure_rag_tables()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO document_summaries (
                conversation_id, file_path, summary
            )
            VALUES (?, ?, ?)
            ON CONFLICT(conversation_id, file_path)
            DO UPDATE SET summary = excluded.summary
            """,
            (conversation_id, str(file_path), summary),
        )


def get_summaries(conversation_id):
    ensure_rag_tables()

    with get_connection() as connection:
        rows = connection.execute(
            "SELECT file_path, summary FROM document_summaries "
            "WHERE conversation_id = ?",
            (conversation_id,),
        ).fetchall()

        return {row["file_path"]: row["summary"] for row in rows}


def delete_document_index(conversation_id, file_path):
    ensure_rag_tables()

    with get_connection() as connection:
        connection.execute(
            "DELETE FROM document_chunks "
            "WHERE conversation_id = ? AND file_path = ?",
            (conversation_id, str(file_path)),
        )
        connection.execute(
            "DELETE FROM document_summaries "
            "WHERE conversation_id = ? AND file_path = ?",
            (conversation_id, str(file_path)),
        )


"""if __name__ == "__main__":
    initialize_database()

    conversation_id = create_conversation("آزمایش ذخیره‌سازی")

    print("شناسه گفت‌وگو:", conversation_id)
    print("فهرست گفت‌وگوها:")

    for conversation in get_conversations():
        print(conversation)"""


"""if __name__ == "__main__":
    initialize_database()
    print(f"دیتابیس با موفقیت ساخته شد: {DATABASE_PATH}")"""

"""if __name__ == "__main__":
    initialize_database()

    conversation_id = create_conversation("تست تغییر نام")

    print("ساخت گفت‌وگو:", conversation_id)

    renamed = rename_conversation(
        conversation_id,
        "عنوان جدید آزمایشی",
    )
    print("تغییر نام موفق:", renamed)

    print("فهرست گفت‌وگوها:")
    for conversation in get_conversations():
        print(conversation)

    deleted = delete_conversation(conversation_id)
    print("حذف گفت‌وگوی آزمایشی موفق:", deleted)"""
if __name__ == "__main__":
    initialize_database()

    conversation_id = create_conversation("تست ذخیره پیام")

    save_message(conversation_id, "user", "سلام")
    save_message(conversation_id, "assistant", "سلام! چطور می‌تونم کمک کنم؟")

    print("پیام‌های ذخیره‌شده:")
    for message in get_messages(conversation_id):
        print(message)

    delete_conversation(conversation_id)
    print("گفت‌وگوی آزمایشی حذف شد.")

