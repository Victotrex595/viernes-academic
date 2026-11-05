import json
import os
import shutil
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from pydantic import BaseModel

from .ai_consortium import (
    AIConsortiumEngine,
    add_extra_gemini_key_to_env,
    extract_local_files_text,
    get_api_keys_status,
)
from .mobile_web_ui import MOBILE_WEB_HTML
from .database import (
    BASE_DIR,
    create_external_assignment,
    get_assignment,
    get_setting,
    init_db,
    list_courses_with_assignments,
    set_setting,
    update_assignment_fields,
    upsert_scraped_courses,
)
from .docx_generator import create_four_pillars_docx_bundle, create_resolution_docx
from .drive_service import GoogleDriveManager
from .saia_service import DOWNLOADS_DIR, DynamicSaiaEngine

init_db()

app = FastAPI(
    title="PhoneApp Academic Consortium API",
    description="Backend para App Móvil: Moodle SAIA PSM + Consorcio IA (Gemini 3.8/4 + DeepSeek-R1) + 4 Pilares NotebookLM",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

drive_manager = GoogleDriveManager()
_LIVE_PROGRESS: Dict[str, Dict[str, Any]] = {}


def _set_progress(
    assignment_id: str,
    percent: int,
    stage: str,
    active: bool = True,
    op_type: str = "research",
) -> None:
    _LIVE_PROGRESS[assignment_id] = {
        "assignment_id": assignment_id,
        "percent": percent,
        "stage": stage,
        "active": active,
        "op_type": op_type,
    }


@app.get("/api/assignments/{assignment_id}/progress")
def get_assignment_progress(assignment_id: str) -> Dict[str, Any]:
    return _LIVE_PROGRESS.get(
        assignment_id,
        {
            "assignment_id": assignment_id,
            "percent": 0,
            "stage": "En espera...",
            "active": False,
            "op_type": "idle",
        },
    )


class CookieUpdatePayload(BaseModel):
    moodle_session: str


class DriveBridgePayload(BaseModel):
    bridge_url: str


class AssignmentControlsPayload(BaseModel):
    allow_token_spend: Optional[bool] = None
    task_mode: Optional[str] = None


class ModelSettingsPayload(BaseModel):
    gemini_model: Optional[str] = None
    gemini_arbiter_model: Optional[str] = None
    deepseek_model: Optional[str] = None


class ExtraGeminiKeyPayload(BaseModel):
    api_key: str


def _get_saia_engine() -> DynamicSaiaEngine:
    cookie = get_setting("moodle_session", "")
    return DynamicSaiaEngine(cookie)


def _get_ai_engine() -> AIConsortiumEngine:
    return AIConsortiumEngine(
        gemini_model=get_setting("gemini_model", "gemini-3-flash-preview"),
        gemini_arbiter_model=get_setting("gemini_arbiter_model", "gemini-3-flash-preview"),
        deepseek_model=get_setting("deepseek_model", "deepseek-reasoner"),
    )


@app.get("/", response_class=HTMLResponse)
def serve_mobile_app_home() -> str:
    return MOBILE_WEB_HTML


@app.get("/icon.svg")
def serve_app_icon() -> Response:
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
      <defs>
        <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#18181c"/>
          <stop offset="100%" stop-color="#0d0d0f"/>
        </linearGradient>
        <linearGradient id="capTop" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#ffffff"/>
          <stop offset="100%" stop-color="#d4d4d8"/>
        </linearGradient>
      </defs>
      <!-- Outer Squircle -->
      <rect width="512" height="512" rx="116" fill="#0d0d0f"/>
      <rect x="20" y="20" width="472" height="472" rx="98" fill="url(#bgGrad)" stroke="#2e2e36" stroke-width="6"/>
      
      <!-- Classic Mortarboard (Birrete Clásico) -->
      <!-- Diamond Top Board -->
      <polygon points="256,120 436,204 256,288 76,204" fill="url(#capTop)"/>
      <!-- Subtle inner bevel on top board -->
      <polygon points="256,134 410,204 256,274 102,204" fill="none" stroke="#18181c" stroke-width="3" stroke-opacity="0.25"/>
      
      <!-- Center Button -->
      <ellipse cx="256" cy="204" rx="14" ry="8" fill="#18181c"/>
      
      <!-- Skullcap / Base under the board -->
      <path d="M148,252 L148,334 C148,368 196,396 256,396 C316,396 364,368 364,334 L364,252 L256,303 L148,252 Z" fill="#a1a1aa"/>
      <path d="M148,252 L148,334 C148,368 196,396 256,396 L256,303 L148,252 Z" fill="#d4d4d8"/>
      
      <!-- Tassel (Borla Clásica) -->
      <path d="M256,204 L392,242 L392,338" fill="none" stroke="#f4f4f6" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="392" cy="336" r="11" fill="#e4e4e7"/>
      <path d="M381,346 L403,346 L408,384 L376,384 Z" fill="#f4f4f6"/>
    </svg>"""
    return Response(content=svg, media_type="image/svg+xml")


@app.get("/manifest.json")
def serve_pwa_manifest() -> JSONResponse:
    return JSONResponse(
        {
            "name": "V.I.E.R.N.E.S.",
            "short_name": "V.I.E.R.N.E.S.",
            "description": "V.I.E.R.N.E.S. — Sistema Académico SAIA PSM + Consorcio IA + NotebookLM",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#0d0d0f",
            "theme_color": "#0d0d0f",
            "orientation": "portrait",
            "icons": [
                {
                    "src": "/icon.svg",
                    "sizes": "any",
                    "type": "image/svg+xml",
                    "purpose": "any maskable",
                }
            ],
        }
    )


@app.get("/sw.js")
def serve_service_worker() -> Response:
    js = """
    self.addEventListener('install', (e) => self.skipWaiting());
    self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));
    self.addEventListener('fetch', (e) => {});
    """
    return Response(content=js, media_type="application/javascript")


@app.get("/api/health")
def get_health(verify_saia: bool = Query(False)) -> Dict[str, Any]:
    cookie = get_setting("moodle_session", "")
    saia_status: Dict[str, Any] = {"configured": bool(cookie), "active": None, "user": "Estudiante PSM"}
    if verify_saia and cookie:
        v = _get_saia_engine().verify_session()
        saia_status["active"] = v.get("active", False)
        saia_status["user"] = v.get("user", "Estudiante PSM")
        saia_status["reason"] = v.get("reason", "")

    courses = list_courses_with_assignments(include_external=True)
    total_tokens = sum(
        a.get("tokens_used", 0) for c in courses for a in c.get("assignments", [])
    )

    return {
        "status": "ok",
        "saia": saia_status,
        "ai_keys": get_api_keys_status(),
        "drive": drive_manager.get_status(),
        "models": {
            "gemini_model": get_setting("gemini_model", "gemini-3-flash-preview"),
            "gemini_arbiter_model": get_setting("gemini_arbiter_model", "gemini-3-flash-preview"),
            "deepseek_model": get_setting("deepseek_model", "deepseek-reasoner"),
        },
        "total_tokens_used": total_tokens,
    }


@app.get("/api/courses")
def get_courses(include_external: bool = Query(True)) -> Dict[str, Any]:
    courses = list_courses_with_assignments(include_external=include_external)
    return {"courses": courses}


@app.get("/api/assignments/{assignment_id}")
def get_single_assignment(assignment_id: str) -> Dict[str, Any]:
    item = get_assignment(assignment_id)
    if not item:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return item


@app.get("/api/assignments/{assignment_id}/inspect")
def inspect_assignment_documents(
    assignment_id: str, fetch_remote: bool = Query(False)
) -> Dict[str, Any]:
    """Returns teacher guidelines, teacher attachments text, and full text of all AI-generated .docx files."""
    item = get_assignment(assignment_id)
    if not item:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")

    desc_text = item.get("description_text", "")
    local_files: List[str] = item.get("local_files", [])
    attachments = item.get("attachments", [])

    if fetch_remote and item.get("link") and not item.get("is_external"):
        engine = _get_saia_engine()
        fresh_desc, fresh_att, downloaded_paths = engine.fetch_and_download_assignment_materials(
            assignment_id, item["link"], extra_attachments=item.get("attachments", [])
        )
        if fresh_desc:
            desc_text = fresh_desc
        if fresh_att:
            attachments = fresh_att
        if downloaded_paths:
            local_files = list(dict.fromkeys(local_files + downloaded_paths))
        item = update_assignment_fields(
            assignment_id,
            {
                "description_text": desc_text,
                "attachments_json": json.dumps(attachments, ensure_ascii=False),
                "local_files_json": json.dumps(local_files, ensure_ascii=False),
            },
        ) or item

    teacher_files_content = extract_local_files_text(local_files)

    ai_documents: List[Dict[str, str]] = []
    for rf in item.get("research_files", []):
        lpath = rf.get("local_path", "")
        if lpath and os.path.exists(lpath):
            ai_documents.append(
                {
                    "name": rf.get("name", os.path.basename(lpath)),
                    "category": "Pilar NotebookLM",
                    "local_path": lpath,
                    "url": rf.get("url", ""),
                    "content": extract_local_files_text([lpath]),
                }
            )

    res_path = item.get("resolution_local_path", "")
    if res_path and os.path.exists(res_path):
        ai_documents.append(
            {
                "name": os.path.basename(res_path),
                "category": f"Resolución ({item.get('task_mode', 'digital')})",
                "local_path": res_path,
                "url": item.get("resolution_drive_url", ""),
                "content": extract_local_files_text([res_path]),
            }
        )

    return {
        "assignment": item,
        "teacher_guidelines": desc_text or "Sin texto descriptivo adicional registrado en SAIA.",
        "teacher_attachments": attachments,
        "teacher_local_files": [
            {"name": os.path.basename(p), "local_path": p}
            for p in local_files
            if os.path.exists(p)
        ],
        "teacher_files_extracted_text": teacher_files_content,
        "ai_generated_documents": ai_documents,
    }


@app.post("/api/saia/cookie")
def update_saia_cookie(payload: CookieUpdatePayload) -> Dict[str, Any]:
    new_cookie = payload.moodle_session.strip()
    if not new_cookie:
        raise HTTPException(status_code=400, detail="La cookie MoodleSession no puede estar vacía.")
    set_setting("moodle_session", new_cookie)
    engine = DynamicSaiaEngine(new_cookie)
    verification = engine.verify_session()
    return {
        "ok": True,
        "session_active": verification.get("active", False),
        "user": verification.get("user", ""),
        "reason": verification.get("reason", ""),
    }


@app.post("/api/saia/sync")
def sync_saia_courses() -> Dict[str, Any]:
    engine = _get_saia_engine()
    result = engine.sync_all_courses()
    if result.get("synced") and result.get("courses"):
        upsert_scraped_courses(result["courses"])
    courses = list_courses_with_assignments(include_external=True)
    return {
        "synced": result.get("synced", False),
        "session_active": result.get("session_active", False),
        "reason": result.get("reason", ""),
        "user": result.get("user", "Estudiante PSM"),
        "courses": courses,
    }


@app.patch("/api/assignments/{assignment_id}/controls")
def update_controls(assignment_id: str, payload: AssignmentControlsPayload) -> Dict[str, Any]:
    existing = get_assignment(assignment_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Asignación no encontrada.")

    updates: Dict[str, Any] = {}
    if payload.allow_token_spend is not None:
        updates["allow_token_spend"] = 1 if payload.allow_token_spend else 0
    if payload.task_mode is not None:
        if payload.task_mode not in ("digital", "manuscrito", "video"):
            raise HTTPException(status_code=400, detail="Modo inválido. Usa digital, manuscrito o video.")
        updates["task_mode"] = payload.task_mode

    updated = update_assignment_fields(assignment_id, updates)
    return {"ok": True, "assignment": updated}


@app.post("/api/assignments/{assignment_id}/research")
def investigate_four_pillars(
    assignment_id: str, force: bool = Query(False)
) -> Dict[str, Any]:
    """Executes Button 1: Investigar Tema y generar los 4 Pilares para NotebookLM en Drive."""
    item = get_assignment(assignment_id)
    if not item:
        raise HTTPException(status_code=404, detail="Asignación no encontrada.")

    existing_research_files = item.get("research_files") or []
    if (
        not force
        and existing_research_files
        and all(os.path.exists(f.get("local_path", "")) for f in existing_research_files)
    ):
        return {
            "ok": True,
            "cached": True,
            "simulated": item.get("research_status") == "simulated",
            "message": "Avance previo de 4 Pilares detectado (0 tokens consumidos). Usa 'Regenerar' si deseas crear una versión nueva.",
            "assignment": item,
        }

    _set_progress(assignment_id, 10, "Extrayendo lineamientos y adjuntos de SAIA PSM...", True, "research")
    desc_text = item.get("description_text", "")
    local_files: List[str] = item.get("local_files", [])

    # If SAIA task with link, try fetching fresh instructions and attachments first
    if item.get("link") and not item.get("is_external"):
        engine = _get_saia_engine()
        fresh_desc, fresh_att, downloaded_paths = engine.fetch_and_download_assignment_materials(
            assignment_id, item["link"], extra_attachments=item.get("attachments", [])
        )
        if fresh_desc:
            desc_text = fresh_desc
        if downloaded_paths:
            local_files = list(dict.fromkeys(local_files + downloaded_paths))
        update_assignment_fields(
            assignment_id,
            {
                "description_text": desc_text,
                "attachments_json": json.dumps(fresh_att or item.get("attachments", []), ensure_ascii=False),
                "local_files_json": json.dumps(local_files, ensure_ascii=False),
            },
        )

    checkpoints = {} if force else dict(item.get("checkpoints") or {})
    if force:
        old_cp = dict(item.get("checkpoints") or {})
        for k in ("research_deepseek", "research_gemini", "research_arbiter"):
            old_cp.pop(k, None)
        checkpoints = old_cp

    def _save_cp(cp: Dict[str, Any]) -> None:
        update_assignment_fields(
            assignment_id, {"checkpoints_json": json.dumps(cp, ensure_ascii=False)}
        )

    ai_engine = _get_ai_engine()
    try:
        res = ai_engine.generate_four_pillars_study_material(
            course_name=item.get("course_name", "Materia PSM"),
            assignment_title=item["title"],
            description_text=desc_text,
            local_files=local_files,
            checkpoints=checkpoints,
            on_checkpoint=_save_cp,
            on_progress=lambda p, s: _set_progress(assignment_id, p, s, True, "research"),
        )
    except Exception as exc:
        _set_progress(assignment_id, 0, f"Error: {exc}", False, "research")
        raise

    _set_progress(assignment_id, 88, "Generando los 4 archivos Word (.docx) para NotebookLM...", True, "research")
    docx_paths = create_four_pillars_docx_bundle(
        course_name=item.get("course_name", "Materia PSM"),
        assignment_title=item["title"],
        pillars_content=res["pillars"],
    )

    _set_progress(assignment_id, 95, "Sincronizando carpetas y archivos con Google Drive...", True, "research")
    drive_sync = drive_manager.sync_study_bundle(
        course_name=item.get("course_name", "Materia PSM"),
        assignment_title=item["title"],
        pillar_docx_paths=docx_paths,
        teacher_files=local_files,
    )

    new_tokens = int(item.get("tokens_used", 0)) + int(res.get("tokens_used", 0))
    updated = update_assignment_fields(
        assignment_id,
        {
            "research_status": "simulated" if res.get("simulated") else "completed",
            "research_drive_folder_url": drive_sync["folder_url"],
            "research_files_json": json.dumps(drive_sync["files"], ensure_ascii=False),
            "research_summary": res["summary"],
            "tokens_used": new_tokens,
        },
    )
    _set_progress(assignment_id, 100, "Dossier de 4 Pilares completado y sincronizado.", False, "research")
    return {
        "ok": True,
        "cached": False,
        "simulated": res.get("simulated", False),
        "assignment": updated,
        "drive_sync": drive_sync,
    }


@app.post("/api/assignments/{assignment_id}/resolve")
def resolve_assignment_endpoint(
    assignment_id: str, force: bool = Query(False)
) -> Dict[str, Any]:
    """Executes Button 2: Resolver Tarea mediante Consenso de IA (Requires safety switch ON)."""
    item = get_assignment(assignment_id)
    if not item:
        raise HTTPException(status_code=404, detail="Asignación no encontrada.")

    existing_res_path = item.get("resolution_local_path", "")
    if not force and existing_res_path and os.path.exists(existing_res_path):
        return {
            "ok": True,
            "cached": True,
            "simulated": item.get("resolution_status") == "simulated",
            "message": "Resolución previa cargada (0 tokens consumidos). Usa 'Crear nueva versión (_v2)' si deseas generar otra.",
            "never_auto_uploaded_notice": "Borrador editable previo disponible.",
            "assignment": item,
        }

    # Strict Token Protection Check
    if not item.get("allow_token_spend"):
        raise HTTPException(
            status_code=403,
            detail=(
                "Protección de Tokens Activa: Debes encender primero el switch "
                "'Consumir Tokens de Resolución' en la tarjeta de la tarea antes de resolverla."
            ),
        )

    _set_progress(assignment_id, 10, "Extrayendo pautas y adjuntos del aula virtual SAIA...", True, "resolve")
    desc_text = item.get("description_text", "")
    local_files: List[str] = item.get("local_files", [])

    if item.get("link") and not item.get("is_external"):
        engine = _get_saia_engine()
        fresh_desc, fresh_att, downloaded_paths = engine.fetch_and_download_assignment_materials(
            assignment_id, item["link"], extra_attachments=item.get("attachments", [])
        )
        if fresh_desc:
            desc_text = fresh_desc
        if downloaded_paths:
            local_files = list(dict.fromkeys(local_files + downloaded_paths))
        update_assignment_fields(
            assignment_id,
            {
                "description_text": desc_text,
                "attachments_json": json.dumps(fresh_att or item.get("attachments", []), ensure_ascii=False),
                "local_files_json": json.dumps(local_files, ensure_ascii=False),
            },
        )

    task_mode = item.get("task_mode", "digital")
    checkpoints = dict(item.get("checkpoints") or {})
    if force:
        for k in (
            f"resolve_{task_mode}_deepseek",
            f"resolve_{task_mode}_gemini",
            f"resolve_{task_mode}_arbiter",
            "resolve_deepseek",
            "resolve_gemini",
        ):
            checkpoints.pop(k, None)

    def _save_cp(cp: Dict[str, Any]) -> None:
        update_assignment_fields(
            assignment_id, {"checkpoints_json": json.dumps(cp, ensure_ascii=False)}
        )

    ai_engine = _get_ai_engine()
    try:
        res = ai_engine.resolve_assignment_with_consensus(
            course_name=item.get("course_name", "Materia PSM"),
            assignment_title=item["title"],
            description_text=desc_text,
            task_mode=task_mode,
            local_files=local_files,
            research_files=item.get("research_files", []),
            checkpoints=checkpoints,
            on_checkpoint=_save_cp,
            on_progress=lambda p, s: _set_progress(assignment_id, p, s, True, "resolve"),
        )
    except Exception as exc:
        _set_progress(assignment_id, 0, f"Error: {exc}", False, "resolve")
        raise

    _set_progress(assignment_id, 88, "Maquetando documento Word (.docx) con plantilla institucional...", True, "resolve")
    docx_path = create_resolution_docx(
        course_name=item.get("course_name", "Materia PSM"),
        assignment_title=item["title"],
        task_mode=task_mode,
        resolution_markdown=res["resolution_markdown"],
        is_external=bool(item.get("is_external")),
        teacher_name=item.get("teacher_name", "Docente de la Cátedra"),
        avoid_overwrite=True,
    )

    _set_progress(assignment_id, 95, "Sincronizando resolución con Google Drive...", True, "resolve")
    drive_res = drive_manager.sync_resolution_doc(
        course_name=item.get("course_name", "Materia PSM"),
        assignment_title=item["title"],
        docx_path=docx_path,
    )

    new_tokens = int(item.get("tokens_used", 0)) + int(res.get("tokens_used", 0))
    updated = update_assignment_fields(
        assignment_id,
        {
            "resolution_status": "simulated" if res.get("simulated") else "completed",
            "resolution_drive_url": drive_res["url"],
            "resolution_local_path": drive_res["local_path"],
            "consensus_report": res["consensus_report"],
            "tokens_used": new_tokens,
        },
    )
    _set_progress(assignment_id, 100, "Resolución completada y lista para tu revisión.", False, "resolve")
    return {
        "ok": True,
        "cached": False,
        "simulated": res.get("simulated", False),
        "never_auto_uploaded_notice": "Borrador editable generado. Recuerda revisarlo antes de subirlo manualmente a SAIA.",
        "assignment": updated,
    }


@app.post("/api/external/create")
async def create_external_topic_endpoint(
    title: str = Form(...),
    description_text: str = Form(""),
    category_name: str = Form("Proyectos Libres / Fuera de PSM"),
    task_mode: str = Form("digital"),
    files: Optional[List[UploadFile]] = File(None),
) -> Dict[str, Any]:
    if not title.strip():
        raise HTTPException(status_code=400, detail="El título del tema o evaluación es obligatorio.")

    saved_files: List[str] = []
    if files:
        ext_upload_dir = os.path.join(DOWNLOADS_DIR, "external_uploads")
        os.makedirs(ext_upload_dir, exist_ok=True)
        for uf in files:
            if not uf.filename:
                continue
            dest = os.path.join(ext_upload_dir, uf.filename)
            with open(dest, "wb") as f:
                shutil.copyfileobj(uf.file, f)
            saved_files.append(dest)

    created = create_external_assignment(
        title=title,
        description_text=description_text,
        category_name=category_name,
        task_mode=task_mode,
        local_files=saved_files,
    )
    return {"ok": True, "assignment": created}


@app.get("/api/files/download")
def download_generated_file(path: str = Query(...)) -> FileResponse:
    clean_path = path.replace("local://", "").strip()
    abs_path = os.path.abspath(clean_path)
    allowed_roots = [
        os.path.abspath(os.path.join(BASE_DIR, "Moodle_PSM_Estudio")),
        os.path.abspath(os.path.join(BASE_DIR, "generated_docs")),
        os.path.abspath(DOWNLOADS_DIR),
    ]
    if not any(abs_path.startswith(r) for r in allowed_roots):
        raise HTTPException(status_code=403, detail="Acceso denegado fuera del directorio de estudio.")
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
    return FileResponse(abs_path, filename=os.path.basename(abs_path))


@app.post("/api/drive/oauth")
def connect_google_drive_oauth() -> Dict[str, Any]:
    return drive_manager.start_oauth_local_flow()


@app.post("/api/drive/bridge")
def set_google_drive_bridge(payload: DriveBridgePayload) -> Dict[str, Any]:
    return drive_manager.set_bridge_url(payload.bridge_url)


@app.post("/api/settings/models")
def update_model_settings(payload: ModelSettingsPayload) -> Dict[str, Any]:
    if payload.gemini_model:
        set_setting("gemini_model", payload.gemini_model.strip())
    if payload.gemini_arbiter_model:
        set_setting("gemini_arbiter_model", payload.gemini_arbiter_model.strip())
    if payload.deepseek_model:
        set_setting("deepseek_model", payload.deepseek_model.strip())
    return {
        "ok": True,
        "models": {
            "gemini_model": get_setting("gemini_model"),
            "gemini_arbiter_model": get_setting("gemini_arbiter_model"),
            "deepseek_model": get_setting("deepseek_model"),
        },
    }


@app.post("/api/settings/gemini-key")
def add_extra_gemini_key_endpoint(payload: ExtraGeminiKeyPayload) -> Dict[str, Any]:
    res = add_extra_gemini_key_to_env(payload.api_key)
    if not res.get("ok"):
        raise HTTPException(status_code=400, detail=res.get("message", "Clave inválida"))
    return res
