import json
import os
import re
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

BASE_DIR = os.getenv("PHONEAPP_DATA_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "phoneapp.db")
LEGACY_BOT_DIR = os.getenv("LEGACY_BOT_DIR", r"C:\Users\Admin\Documents\saia_telegram_bot")


def detect_default_task_mode(title: str, description: str = "") -> str:
    combined = f"{title} {description}".lower()
    if any(k in combined for k in ["video", "expositiv", "exposición", "grabación", "youtube"]):
        return "video"
    if any(k in combined for k in ["manuscrito", "a mano", "escrito a mano", "hoja de examen", "escanead"]):
        return "manuscrito"
    return "digital"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS courses (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            teacher_name TEXT DEFAULT 'Docente de la Cátedra',
            total_grade TEXT DEFAULT 'Sin calificar',
            grades_json TEXT DEFAULT '[]',
            is_external INTEGER DEFAULT 0,
            updated_at TEXT NOT NULL
        )
        """
    )
    try:
        cur.execute("ALTER TABLE courses ADD COLUMN teacher_name TEXT DEFAULT 'Docente de la Cátedra'")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE assignments ADD COLUMN checkpoints_json TEXT DEFAULT '{}'")
    except Exception:
        pass

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS assignments (
            id TEXT PRIMARY KEY,
            course_id TEXT NOT NULL,
            title TEXT NOT NULL,
            type TEXT DEFAULT 'Tarea',
            link TEXT DEFAULT '',
            due_date TEXT DEFAULT '',
            time_remaining TEXT DEFAULT '-',
            status TEXT DEFAULT 'Pendiente',
            is_completed INTEGER DEFAULT 0,
            is_overdue INTEGER DEFAULT 0,
            description_text TEXT DEFAULT '',
            attachments_json TEXT DEFAULT '[]',
            local_files_json TEXT DEFAULT '[]',
            task_mode TEXT DEFAULT 'digital',
            allow_token_spend INTEGER DEFAULT 0,
            research_status TEXT DEFAULT 'idle',
            research_drive_folder_url TEXT DEFAULT '',
            research_files_json TEXT DEFAULT '[]',
            resolution_status TEXT DEFAULT 'idle',
            resolution_drive_url TEXT DEFAULT '',
            resolution_local_path TEXT DEFAULT '',
            consensus_report TEXT DEFAULT '',
            research_summary TEXT DEFAULT '',
            checkpoints_json TEXT DEFAULT '{}',
            tokens_used INTEGER DEFAULT 0,
            is_external INTEGER DEFAULT 0,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
        """
    )

    conn.commit()
    conn.close()
    _seed_defaults_and_legacy_data()


def get_setting(key: str, default: str = "") -> str:
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
    conn.commit()
    conn.close()


def _seed_defaults_and_legacy_data() -> None:
    # Seed default model names (Free-Tier verified: gemini-3-flash-preview)
    if not get_setting("gemini_model") or get_setting("gemini_model") in ("gemini-3.8-flash", "gemini-4-argon"):
        set_setting("gemini_model", "gemini-3-flash-preview")
    if not get_setting("gemini_arbiter_model") or get_setting("gemini_arbiter_model") in ("gemini-3.8-flash", "gemini-4-argon"):
        set_setting("gemini_arbiter_model", "gemini-3-flash-preview")
    if not get_setting("deepseek_model"):
        set_setting("deepseek_model", "deepseek-reasoner")

    # Import MoodleSession from legacy bot if not set yet
    if not get_setting("moodle_session"):
        cfg_path = os.path.join(LEGACY_BOT_DIR, "config.json")
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("moodle_session"):
                        set_setting("moodle_session", str(data["moodle_session"]).strip())
            except Exception:
                pass

    # Ensure virtual course for external topics exists
    now = datetime.now().isoformat()
    conn = get_connection()
    ext_course = conn.execute("SELECT id FROM courses WHERE id = 'EXTERNAL_FREE'").fetchone()
    if not ext_course:
        conn.execute(
            """
            INSERT INTO courses (id, name, total_grade, grades_json, is_external, updated_at)
            VALUES ('EXTERNAL_FREE', 'Proyectos Libres / Fuera de PSM', '-', '[]', 1, ?)
            """,
            (now,),
        )
        conn.commit()

    # Seed from legacy saia_state.json if no PSM courses exist yet
    psm_count = conn.execute("SELECT COUNT(*) as c FROM courses WHERE is_external = 0").fetchone()["c"]
    conn.close()

    if psm_count == 0:
        state_path = os.path.join(LEGACY_BOT_DIR, "saia_state.json")
        if os.path.exists(state_path):
            try:
                with open(state_path, "r", encoding="utf-8") as f:
                    state = json.load(f)
                upsert_scraped_courses(state.get("courses", []))
            except Exception:
                pass


def upsert_scraped_courses(courses_data: List[Dict[str, Any]]) -> None:
    now = datetime.now().isoformat()
    conn = get_connection()
    for c in courses_data:
        cid = str(c["id"])
        cname = c.get("name", f"Curso {cid}")
        tname = c.get("teacher_name", "Docente de la Cátedra")
        total = str(c.get("total", "Sin calificar"))
        grades_json = json.dumps(c.get("grades", []), ensure_ascii=False)

        conn.execute(
            """
            INSERT INTO courses (id, name, teacher_name, total_grade, grades_json, is_external, updated_at)
            VALUES (?, ?, ?, ?, ?, 0, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                teacher_name = CASE WHEN excluded.teacher_name != 'Docente de la Cátedra' THEN excluded.teacher_name ELSE courses.teacher_name END,
                total_grade = excluded.total_grade,
                grades_json = excluded.grades_json,
                updated_at = excluded.updated_at
            """,
            (cid, cname, tname, total, grades_json, now),
        )

        for act in c.get("activities", []):
            link = act.get("link", "")
            m = re.search(r"[?&]id=(\d+)", link)
            act_id = f"saia_{m.group(1)}" if m else f"saia_{cid}_{ abs(hash(act.get('title', ''))) % 1000000 }"
            title = act.get("title", "Actividad")
            act_type = act.get("type", "Tarea")
            due_date = act.get("fecha_calendario") or act.get("fecha_entrega") or ""
            time_rem = act.get("tiempo", "-")
            status = act.get("estado", "Pendiente")
            is_completed = 1 if act.get("es_realizada") else 0
            is_overdue = 1 if act.get("es_atrasada") else 0
            desc = act.get("description_text", "")
            attachments = json.dumps(act.get("attachments", []), ensure_ascii=False)

            existing = conn.execute("SELECT task_mode, description_text, attachments_json FROM assignments WHERE id = ?", (act_id,)).fetchone()
            if existing:
                task_mode = existing["task_mode"]
                final_desc = desc if desc else existing["description_text"]
                final_att = attachments if act.get("attachments") else existing["attachments_json"]
            else:
                task_mode = detect_default_task_mode(title, desc)
                final_desc = desc
                final_att = attachments

            conn.execute(
                """
                INSERT INTO assignments (
                    id, course_id, title, type, link, due_date, time_remaining,
                    status, is_completed, is_overdue, description_text, attachments_json,
                    task_mode, is_external, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    type = excluded.type,
                    link = excluded.link,
                    due_date = excluded.due_date,
                    time_remaining = excluded.time_remaining,
                    status = excluded.status,
                    is_completed = excluded.is_completed,
                    is_overdue = excluded.is_overdue,
                    description_text = CASE WHEN excluded.description_text != '' THEN excluded.description_text ELSE assignments.description_text END,
                    attachments_json = CASE WHEN excluded.attachments_json != '[]' THEN excluded.attachments_json ELSE assignments.attachments_json END,
                    updated_at = excluded.updated_at
                """,
                (
                    act_id,
                    cid,
                    title,
                    act_type,
                    link,
                    due_date,
                    time_rem,
                    status,
                    is_completed,
                    is_overdue,
                    final_desc,
                    final_att,
                    task_mode,
                    now,
                ),
            )
    conn.commit()
    conn.close()


def list_courses_with_assignments(
    include_external: bool = True, include_overdue: bool = False
) -> List[Dict[str, Any]]:
    conn = get_connection()
    query = "SELECT * FROM courses" if include_external else "SELECT * FROM courses WHERE is_external = 0"
    courses = [dict(r) for r in conn.execute(query + " ORDER BY is_external ASC, name ASC").fetchall()]
    for c in courses:
        c["grades"] = json.loads(c.get("grades_json") or "[]")
        c["is_external"] = bool(c["is_external"])
        if include_overdue:
            rows = conn.execute(
                "SELECT * FROM assignments WHERE course_id = ? ORDER BY is_completed ASC, title ASC",
                (c["id"],),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM assignments WHERE course_id = ? AND is_overdue = 0 ORDER BY is_completed ASC, title ASC",
                (c["id"],),
            ).fetchall()
        c["assignments"] = [_format_assignment_row(dict(r)) for r in rows]
    conn.close()
    return courses


def get_assignment(assignment_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM assignments WHERE id = ?", (assignment_id,)).fetchone()
    if not row:
        conn.close()
        return None
    data = _format_assignment_row(dict(row))
    course = conn.execute("SELECT name, teacher_name FROM courses WHERE id = ?", (data["course_id"],)).fetchone()
    data["course_name"] = course["name"] if course else "General"
    data["teacher_name"] = (course["teacher_name"] if course and course["teacher_name"] else "Docente de la Cátedra")
    conn.close()
    return data


def update_assignment_fields(assignment_id: str, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not fields:
        return get_assignment(assignment_id)
    fields["updated_at"] = datetime.now().isoformat()
    cols = ", ".join(f"{k} = ?" for k in fields.keys())
    vals = list(fields.values()) + [assignment_id]
    conn = get_connection()
    conn.execute(f"UPDATE assignments SET {cols} WHERE id = ?", vals)
    conn.commit()
    conn.close()
    return get_assignment(assignment_id)


def create_external_assignment(
    title: str,
    description_text: str,
    category_name: str = "Proyectos Libres / Fuera de PSM",
    task_mode: str = "digital",
    local_files: Optional[List[str]] = None,
) -> Dict[str, Any]:
    now = datetime.now().isoformat()
    conn = get_connection()
    course_id = "EXTERNAL_FREE"
    if category_name and category_name.strip() and category_name.strip() != "Proyectos Libres / Fuera de PSM":
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", category_name.strip().upper()).strip("_")
        course_id = f"EXT_{slug[:24]}"
        conn.execute(
            """
            INSERT INTO courses (id, name, total_grade, grades_json, is_external, updated_at)
            VALUES (?, ?, '-', '[]', 1, ?)
            ON CONFLICT(id) DO UPDATE SET name = excluded.name, updated_at = excluded.updated_at
            """,
            (course_id, category_name.strip(), now),
        )

    act_id = f"ext_{int(datetime.now().timestamp() * 1000)}"
    mode = task_mode if task_mode in ("digital", "manuscrito", "video") else detect_default_task_mode(title, description_text)
    local_json = json.dumps(local_files or [], ensure_ascii=False)

    conn.execute(
        """
        INSERT INTO assignments (
            id, course_id, title, type, link, due_date, time_remaining,
            status, is_completed, is_overdue, description_text, attachments_json,
            local_files_json, task_mode, allow_token_spend, is_external, updated_at
        )
        VALUES (?, ?, ?, 'Tema Libre / Evaluación', '', 'Sin fecha límite', 'Activo',
                'Pendiente', 0, 0, ?, '[]', ?, ?, 0, 1, ?)
        """,
        (act_id, course_id, title.strip(), description_text.strip(), local_json, mode, now),
    )
    conn.commit()
    conn.close()
    return get_assignment(act_id)  # type: ignore


def _format_assignment_row(r: Dict[str, Any]) -> Dict[str, Any]:
    r["is_completed"] = bool(r.get("is_completed"))
    r["is_overdue"] = bool(r.get("is_overdue"))
    r["allow_token_spend"] = bool(r.get("allow_token_spend"))
    r["is_external"] = bool(r.get("is_external"))
    r["attachments"] = json.loads(r.get("attachments_json") or "[]")
    r["local_files"] = json.loads(r.get("local_files_json") or "[]")
    r["research_files"] = json.loads(r.get("research_files_json") or "[]")
    r["checkpoints"] = json.loads(r.get("checkpoints_json") or "{}")
    return r
