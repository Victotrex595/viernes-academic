import base64
import hashlib
import json
import os
import shutil
from typing import Any, Dict, List, Optional

import httpx
from docx import Document as DocxDocument

from .database import get_setting, set_setting

BASE_DIR = os.getenv("PHONEAPP_DATA_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "google_credentials.json")
TOKEN_PATH = os.path.join(BASE_DIR, "google_token.json")
LOCAL_DRIVE_MIRROR = os.path.join(BASE_DIR, "Moodle_PSM_Estudio")

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _extract_plain_text_from_docx(docx_path: str) -> str:
    try:
        doc = DocxDocument(docx_path)
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception:
        return ""


def _file_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class GoogleDriveManager:
    """Manages hierarchical folders and Google Docs in Google Drive via Apps Script Bridge or OAuth2, with local mirror."""

    def __init__(self) -> None:
        os.makedirs(LOCAL_DRIVE_MIRROR, exist_ok=True)

    def _resolve_env_path(self) -> str:
        candidates = [
            os.getenv("ENV_FILE_PATH", ""),
            os.path.join(os.getcwd(), ".env"),
            os.path.join(os.path.dirname(BASE_DIR), ".env"),
            os.path.join(BASE_DIR, ".env"),
        ]
        for c in candidates:
            if c and os.path.exists(c):
                return c
        return os.path.join(os.path.dirname(BASE_DIR), ".env")

    def get_bridge_url(self) -> str:
        from dotenv import load_dotenv

        load_dotenv(self._resolve_env_path(), override=True)
        env_url = os.getenv("GOOGLE_DRIVE_BRIDGE_URL", "").strip()
        return get_setting("google_drive_bridge_url", "").strip() or env_url

    def set_bridge_url(self, url: str) -> Dict[str, Any]:
        clean = url.strip()
        set_setting("google_drive_bridge_url", clean)
        env_path = self._resolve_env_path()
        if clean:
            lines = (
                open(env_path, "r", encoding="utf-8").read().splitlines()
                if os.path.exists(env_path)
                else []
            )
            lines = [l for l in lines if not l.startswith("GOOGLE_DRIVE_BRIDGE_URL=")]
            lines.append(f"GOOGLE_DRIVE_BRIDGE_URL={clean}")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
        if not clean:
            return {"ok": False, "message": "URL vacía."}
        # Quick ping test
        try:
            with httpx.Client(follow_redirects=True, timeout=20.0) as client:
                r = client.post(
                    clean,
                    json={"action": "ping", "root_folder": "Moodle_PSM_Estudio"},
                )
                if r.status_code == 200:
                    data = r.json()
                    return {
                        "ok": True,
                        "folder_url": data.get("folder_url", ""),
                        "message": "Google Drive conectado y carpeta 'Moodle_PSM_Estudio' verificada en tu nube.",
                    }
        except Exception as e:
            return {
                "ok": True,
                "message": f"URL guardada (aviso al verificar ping: {e}).",
            }
        return {"ok": True, "message": "URL de Google Drive guardada."}

    def get_status(self) -> Dict[str, Any]:
        bridge_url = self.get_bridge_url()
        has_creds = os.path.exists(CREDENTIALS_PATH)
        has_token = os.path.exists(TOKEN_PATH)
        connected = bool(bridge_url) or has_token
        return {
            "oauth_configured": has_creds,
            "bridge_configured": bool(bridge_url),
            "connected": connected,
            "local_mirror_path": LOCAL_DRIVE_MIRROR,
            "instructions": (
                "Sincronización en vivo con Google Drive activa."
                if connected
                else "Modo espejo local activo. Vincula tu URL de puente Google Drive en Configuración."
            ),
        }

    def start_oauth_local_flow(self) -> Dict[str, Any]:
        if not os.path.exists(CREDENTIALS_PATH):
            return {
                "ok": False,
                "message": (
                    "Para conectar sin Google Cloud Console, usa el 'Puente Rápido de Google Drive (Apps Script)' "
                    "pegando la URL arriba."
                ),
            }
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow

            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, "w", encoding="utf-8") as token_file:
                token_file.write(creds.to_json())
            return {"ok": True, "message": "Cuenta de Google vinculada con éxito vía OAuth2."}
        except Exception as e:
            return {"ok": False, "message": f"Error durante autenticación OAuth2: {e}"}

    def _sync_via_bridge(
        self,
        bridge_url: str,
        course_name: str,
        assignment_title: str,
        docs_payload: List[Dict[str, str]],
        teacher_files_payload: Optional[List[Dict[str, str]]] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            with httpx.Client(follow_redirects=True, timeout=60.0) as client:
                resp = client.post(
                    bridge_url,
                    json={
                        "action": "sync_bundle",
                        "root_folder": "Moodle_PSM_Estudio",
                        "course_name": course_name,
                        "assignment_title": assignment_title,
                        "documents": docs_payload,
                        "teacher_files": teacher_files_payload or [],
                    },
                )
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            return None
        return None

    def sync_study_bundle(
        self,
        course_name: str,
        assignment_title: str,
        pillar_docx_paths: Dict[str, str],
        teacher_files: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        from .docx_generator import safe_folder_name

        c_dir = safe_folder_name(course_name)
        t_dir = safe_folder_name(assignment_title)
        local_task_dir = os.path.join(LOCAL_DRIVE_MIRROR, c_dir, t_dir)
        local_sources_dir = os.path.join(local_task_dir, "00_Fuentes_Docente")
        os.makedirs(local_sources_dir, exist_ok=True)

        mirrored_files: List[Dict[str, str]] = []
        bridge_docs: List[Dict[str, str]] = []

        for key, path in pillar_docx_paths.items():
            if os.path.exists(path):
                dest = os.path.join(local_task_dir, os.path.basename(path))
                if os.path.abspath(path) != os.path.abspath(dest):
                    shutil.copy2(path, dest)
                mirrored_files.append({"name": os.path.basename(path), "local_path": dest, "url": ""})
                with open(dest, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                bridge_docs.append(
                    {
                        "name": os.path.basename(dest).replace(".docx", ""),
                        "filename": os.path.basename(dest),
                        "text_content": _extract_plain_text_from_docx(dest),
                        "base64_docx": b64,
                    }
                )

        bridge_teacher_files: List[Dict[str, str]] = []
        for tf in teacher_files or []:
            if os.path.exists(tf):
                dest = os.path.join(local_sources_dir, os.path.basename(tf))
                if os.path.abspath(tf) != os.path.abspath(dest):
                    shutil.copy2(tf, dest)
                if os.path.getsize(dest) < 10 * 1024 * 1024:
                    with open(dest, "rb") as f:
                        bridge_teacher_files.append(
                            {
                                "filename": os.path.basename(dest),
                                "base64": base64.b64encode(f.read()).decode("utf-8"),
                            }
                        )

        # 1. Check Google Apps Script Bridge first (with SHA-256 deduplication)
        bridge_url = self.get_bridge_url()
        if bridge_url:
            hash_cache = json.loads(get_setting("drive_uploaded_hashes", "{}") or "{}")
            docs_to_upload = []
            for d in bridge_docs:
                full_p = os.path.join(local_task_dir, d["filename"])
                f_hash = _file_sha256(full_p) if os.path.exists(full_p) else ""
                cache_key = f"{course_name}/{assignment_title}/{d['filename']}"
                if f_hash and hash_cache.get(cache_key) == f_hash:
                    continue
                d["_hash"] = f_hash
                d["_cache_key"] = cache_key
                docs_to_upload.append(d)

            if not docs_to_upload and mirrored_files:
                return {
                    "cloud_synced": True,
                    "deduplicated": True,
                    "folder_url": get_setting(f"drive_folder_{course_name}_{assignment_title}", ""),
                    "files": mirrored_files,
                }

            res = self._sync_via_bridge(
                bridge_url=bridge_url,
                course_name=course_name,
                assignment_title=assignment_title,
                docs_payload=docs_to_upload or bridge_docs,
                teacher_files_payload=bridge_teacher_files,
            )
            if res and res.get("ok"):
                for d in docs_to_upload:
                    if d.get("_hash") and d.get("_cache_key"):
                        hash_cache[d["_cache_key"]] = d["_hash"]
                set_setting("drive_uploaded_hashes", json.dumps(hash_cache))
                if res.get("folder_url"):
                    set_setting(f"drive_folder_{course_name}_{assignment_title}", res["folder_url"])
                remote_urls = {f["name"]: f["url"] for f in res.get("files", [])}
                for item in mirrored_files:
                    clean_key = item["name"].replace(".docx", "")
                    if clean_key in remote_urls:
                        item["url"] = remote_urls[clean_key]
                    elif item["name"] in remote_urls:
                        item["url"] = remote_urls[item["name"]]
                return {
                    "cloud_synced": True,
                    "folder_url": res.get("folder_url", ""),
                    "files": mirrored_files,
                }

        return {
            "cloud_synced": False,
            "folder_url": f"local://{local_task_dir}",
            "files": mirrored_files,
        }

    def sync_resolution_doc(
        self,
        course_name: str,
        assignment_title: str,
        docx_path: str,
    ) -> Dict[str, str]:
        from .docx_generator import safe_folder_name

        c_dir = safe_folder_name(course_name)
        t_dir = safe_folder_name(assignment_title)
        local_task_dir = os.path.join(LOCAL_DRIVE_MIRROR, c_dir, t_dir)
        os.makedirs(local_task_dir, exist_ok=True)
        dest = os.path.join(local_task_dir, os.path.basename(docx_path))
        if os.path.exists(docx_path) and os.path.abspath(docx_path) != os.path.abspath(dest):
            shutil.copy2(docx_path, dest)

        bridge_url = self.get_bridge_url()
        if bridge_url and os.path.exists(dest):
            with open(dest, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            doc_name = os.path.basename(dest).replace(".docx", "")
            res = self._sync_via_bridge(
                bridge_url=bridge_url,
                course_name=course_name,
                assignment_title=assignment_title,
                docs_payload=[
                    {
                        "name": doc_name,
                        "filename": os.path.basename(dest),
                        "text_content": _extract_plain_text_from_docx(dest),
                        "base64_docx": b64,
                    }
                ],
            )
            if res and res.get("ok") and res.get("files"):
                return {
                    "url": res["files"][0].get("url", f"local://{dest}"),
                    "local_path": dest,
                }

        return {"url": f"local://{dest}", "local_path": dest}
