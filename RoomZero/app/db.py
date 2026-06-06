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
                email TEXT,
                role TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                invited_by TEXT,
                invite_code TEXT,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS invitations (
                id TEXT PRIMARY KEY,
                email TEXT,
                invite_code TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'created',
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
                possible_harm TEXT NOT NULL DEFAULT '',
                mitigation_notes TEXT NOT NULL DEFAULT '',
                human_oversight_required INTEGER NOT NULL DEFAULT 1,
                reviewer_id TEXT,
                reviewer_notes TEXT,
                suggested_conditions TEXT NOT NULL,
                priority INTEGER NOT NULL DEFAULT 5,
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
                expected_observations TEXT NOT NULL DEFAULT '',
                variables TEXT NOT NULL DEFAULT '[]',
                metrics TEXT NOT NULL DEFAULT '[]',
                ethical_constraints TEXT NOT NULL DEFAULT '[]',
                risk_level TEXT NOT NULL DEFAULT 'unknown',
                possible_harm TEXT NOT NULL DEFAULT '',
                mitigation_notes TEXT NOT NULL DEFAULT '',
                human_oversight_required INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'draft',
                result_summary TEXT,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(research_question_id) REFERENCES research_questions(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS simulation_runs (
                id TEXT PRIMARY KEY,
                scenario_id TEXT NOT NULL,
                run_status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                input_snapshot TEXT NOT NULL DEFAULT '{}',
                output_summary TEXT,
                metrics_json TEXT NOT NULL DEFAULT '{}',
                created_by TEXT NOT NULL,
                FOREIGN KEY(scenario_id) REFERENCES simulation_scenarios(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS observations (
                id TEXT PRIMARY KEY,
                scenario_id TEXT NOT NULL,
                run_id TEXT,
                observer_user_id TEXT NOT NULL,
                observation_type TEXT NOT NULL,
                content TEXT NOT NULL,
                confidence REAL NOT NULL DEFAULT 0.5,
                created_at TEXT NOT NULL,
                FOREIGN KEY(scenario_id) REFERENCES simulation_scenarios(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS knowledge_entries (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                entry_type TEXT NOT NULL DEFAULT 'insight',
                source_type TEXT NOT NULL,
                source_id TEXT NOT NULL,
                linked_question_id TEXT,
                linked_scenario_id TEXT,
                linked_run_id TEXT,
                linked_observation_id TEXT,
                tags TEXT NOT NULL DEFAULT '[]',
                source_ids TEXT NOT NULL DEFAULT '[]',
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS audit_logs (
                id TEXT PRIMARY KEY,
                actor_id TEXT NOT NULL,
                actor_user_id TEXT,
                action TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                entity_type TEXT,
                entity_id TEXT,
                before_json TEXT NOT NULL DEFAULT '{}',
                after_json TEXT NOT NULL DEFAULT '{}',
                details TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_invitations_code ON invitations(invite_code);
            CREATE INDEX IF NOT EXISTS idx_questions_status ON research_questions(status);
            CREATE INDEX IF NOT EXISTS idx_comments_question ON research_comments(question_id);
            CREATE INDEX IF NOT EXISTS idx_sim_runs_scenario ON simulation_runs(scenario_id);
            CREATE INDEX IF NOT EXISTS idx_observations_scenario ON observations(scenario_id);
            CREATE INDEX IF NOT EXISTS idx_audit_target ON audit_logs(target_type, target_id);

            CREATE TABLE IF NOT EXISTS simulation_event_review_notes (
                id TEXT PRIMARY KEY,
                event_id TEXT NOT NULL,
                note_text TEXT NOT NULL,
                reviewer_id TEXT NOT NULL,
                status TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_sim_event_review_notes_event_id
                ON simulation_event_review_notes(event_id);
            CREATE INDEX IF NOT EXISTS idx_sim_event_review_notes_created_at
                ON simulation_event_review_notes(created_at);

            """
        )

    with get_connection(db_path) as conn:
        migration_statements = [
            "ALTER TABLE users ADD COLUMN email TEXT",
            "ALTER TABLE users ADD COLUMN status TEXT NOT NULL DEFAULT 'active'",
            "ALTER TABLE invitations ADD COLUMN email TEXT",
            "ALTER TABLE invitations ADD COLUMN status TEXT NOT NULL DEFAULT 'created'",
            "ALTER TABLE research_questions ADD COLUMN possible_harm TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE research_questions ADD COLUMN mitigation_notes TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE research_questions ADD COLUMN human_oversight_required INTEGER NOT NULL DEFAULT 1",
            "ALTER TABLE research_questions ADD COLUMN reviewer_id TEXT",
            "ALTER TABLE research_questions ADD COLUMN reviewer_notes TEXT",
            "ALTER TABLE research_questions ADD COLUMN priority INTEGER NOT NULL DEFAULT 5",
            "ALTER TABLE simulation_scenarios ADD COLUMN expected_observations TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE simulation_scenarios ADD COLUMN risk_level TEXT NOT NULL DEFAULT 'unknown'",
            "ALTER TABLE simulation_scenarios ADD COLUMN possible_harm TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE simulation_scenarios ADD COLUMN mitigation_notes TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE simulation_scenarios ADD COLUMN human_oversight_required INTEGER NOT NULL DEFAULT 1",
            "ALTER TABLE simulation_scenarios ADD COLUMN status TEXT NOT NULL DEFAULT 'draft'",
            "ALTER TABLE simulation_scenarios ADD COLUMN result_summary TEXT",
            "ALTER TABLE knowledge_entries ADD COLUMN entry_type TEXT NOT NULL DEFAULT 'insight'",
            "ALTER TABLE knowledge_entries ADD COLUMN linked_run_id TEXT",
            "ALTER TABLE knowledge_entries ADD COLUMN tags TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE knowledge_entries ADD COLUMN source_ids TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE audit_logs ADD COLUMN actor_user_id TEXT",
            "ALTER TABLE audit_logs ADD COLUMN entity_type TEXT",
            "ALTER TABLE audit_logs ADD COLUMN entity_id TEXT",
            "ALTER TABLE audit_logs ADD COLUMN before_json TEXT NOT NULL DEFAULT '{}'",
            "ALTER TABLE audit_logs ADD COLUMN after_json TEXT NOT NULL DEFAULT '{}'",
            "ALTER TABLE simulation_event_review_notes ADD COLUMN status TEXT",
            "ALTER TABLE simulation_event_review_notes ADD COLUMN updated_at TEXT NOT NULL DEFAULT ''",
        ]
        for stmt in migration_statements:
            try:
                conn.execute(stmt)
            except sqlite3.OperationalError:
                pass


def json_dumps(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def json_loads(value: str) -> object:
    try:
        return json.loads(value)
    except Exception:
        return []
