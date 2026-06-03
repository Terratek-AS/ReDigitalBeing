from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def get_connection(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Path) -> None:
    with get_connection(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                role TEXT NOT NULL,
                invited_by TEXT,
                invite_code TEXT,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS invitations (
                id TEXT PRIMARY KEY,
                invite_code TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL,
                invited_by TEXT,
                expires_at TEXT,
                accepted_by TEXT,
                accepted_at TEXT,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS research_questions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                hypothesis TEXT NOT NULL,
                simulation_relevance TEXT NOT NULL,
                ethical_risk TEXT NOT NULL,
                suggested_conditions TEXT NOT NULL,
                status TEXT NOT NULL,
                author TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                tags TEXT NOT NULL DEFAULT '[]'
            );

            CREATE TABLE IF NOT EXISTS research_comments (
                id TEXT PRIMARY KEY,
                question_id TEXT NOT NULL,
                author TEXT NOT NULL,
                comment TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(question_id) REFERENCES research_questions(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS simulation_scenarios (
                id TEXT PRIMARY KEY,
                research_question_id TEXT NOT NULL,
                purpose TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                environment TEXT NOT NULL,
                variables TEXT NOT NULL DEFAULT '[]',
                metrics TEXT NOT NULL DEFAULT '[]',
                ethical_constraints TEXT NOT NULL DEFAULT '[]',
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(research_question_id) REFERENCES research_questions(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS knowledge_entries (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source_type TEXT NOT NULL,
                source_id TEXT NOT NULL,
                linked_question_id TEXT,
                linked_scenario_id TEXT,
                linked_observation_id TEXT,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS audit_logs (
                id TEXT PRIMARY KEY,
                actor_id TEXT NOT NULL,
                action TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                details TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_invitations_code ON invitations(invite_code);
            CREATE INDEX IF NOT EXISTS idx_questions_status ON research_questions(status);
            CREATE INDEX IF NOT EXISTS idx_comments_question ON research_comments(question_id);
            CREATE INDEX IF NOT EXISTS idx_audit_target ON audit_logs(target_type, target_id);
            """
        )


def json_dumps(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def json_loads(value: str) -> object:
    try:
        return json.loads(value)
    except Exception:
        return []
