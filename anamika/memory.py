"""Local Persistent Memory & Conversation Context Store for Artificial Anamika."""

import os
import json
import sqlite3
import time
from typing import List, Dict, Any, Optional

DEFAULT_MEMORY_DIR = os.path.expanduser("~/.anamika")
DEFAULT_DB_PATH = os.path.join(DEFAULT_MEMORY_DIR, "memory.db")


class MemoryManager:
    """Manages multi-turn conversation history and persistent device memory using SQLite."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = os.path.abspath(os.path.expanduser(db_path))
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT,
                    tool_calls TEXT,
                    tool_call_id TEXT,
                    name TEXT,
                    timestamp REAL NOT NULL
                )
            """)
            # Key-Value durable facts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS durable_facts (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    category TEXT,
                    updated_at REAL NOT NULL
                )
            """)
            conn.commit()

    def add_message(
        self,
        session_id: str,
        role: str,
        content: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        tool_call_id: Optional[str] = None,
        name: Optional[str] = None
    ) -> None:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (session_id, role, content, tool_calls, tool_call_id, name, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                role,
                content,
                json.dumps(tool_calls) if tool_calls else None,
                tool_call_id,
                name,
                time.time()
            ))
            conn.commit()

    def get_history(self, session_id: str, limit: int = 30) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, content, tool_calls, tool_call_id, name
                FROM messages
                WHERE session_id = ?
                ORDER BY id ASC
            """, (session_id,))
            rows = cursor.fetchall()
            
            # Slice last N turns if limit exceeded
            if limit and len(rows) > limit:
                rows = rows[-limit:]

            history = []
            for r in rows:
                msg = {"role": r["role"]}
                if r["content"] is not None:
                    msg["content"] = r["content"]
                if r["tool_calls"]:
                    try:
                        msg["tool_calls"] = json.loads(r["tool_calls"])
                    except Exception:
                        pass
                if r["tool_call_id"]:
                    msg["tool_call_id"] = r["tool_call_id"]
                if r["name"]:
                    msg["name"] = r["name"]
                history.append(msg)
            return history

    def clear_history(self, session_id: str) -> None:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            conn.commit()

    def set_fact(self, key: str, value: Any, category: str = "general") -> None:
        val_str = json.dumps(value) if not isinstance(value, str) else value
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO durable_facts (key, value, category, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    category=excluded.category,
                    updated_at=excluded.updated_at
            """, (key, val_str, category, time.time()))
            conn.commit()

    def get_fact(self, key: str) -> Optional[Any]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM durable_facts WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row["value"])
                except Exception:
                    return row["value"]
            return None

    def get_all_facts(self) -> Dict[str, Any]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM durable_facts")
            facts = {}
            for row in cursor.fetchall():
                try:
                    facts[row["key"]] = json.loads(row["value"])
                except Exception:
                    facts[row["key"]] = row["value"]
            return facts
