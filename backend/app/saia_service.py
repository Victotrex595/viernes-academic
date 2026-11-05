import os
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from html import unescape
from typing import Any, Dict, List, Optional, Tuple

import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://saia2.psm.edu.ve"
DEFAULT_COURSE_IDS = ["27752", "27753", "27604", "27611", "27755", "26639"]
BASE_DIR = os.getenv("PHONEAPP_DATA_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.makedirs(BASE_DIR, exist_ok=True)
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = unescape(re.sub(r"<[^>]+>", " ", text)).replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def sanitize_course_name(name: str) -> str:
    clean = re.sub(r"\s+202\d-\d\s+[A-Z]\b", "", name)
    clean = re.sub(r"\s*/\s*", " / ", clean)
    return clean.strip()


def simplify_activity_title(title: str) -> str:
    t = title
    t = re.sub(
        r"I+ERA\s+ACTIVIDAD\s+EVALUATIVA\s+CORRESPONDIENTE\s+AL\s+\w+\s+CORTE\s*[\.\-:]*\s*",
        "",
        t,
        flags=re.I,
    )
    t = re.sub(r"ACTIVIDAD\s+EVALUATIVA\s*[\.\-:]*\s*", "", t, flags=re.I)
    t = re.sub(r"VALOR\s+\d+\s+PUNTOS\s*", "", t, flags=re.I)
    t = re.sub(r"\s+", " ", t).strip(" .:-")
    if t.isupper():
        t = t.capitalize()
    return t or title


class DynamicSaiaEngine:
    """Expanded SAIA scraper based on saia_telegram_bot with dynamic course discovery and rubric/attachment download."""

    def __init__(self, session_cookie: str):
        self.session_cookie = session_cookie.strip()
        self._init_client(self.session_cookie)

    def _init_client(self, cookie: str) -> None:
        self.client = httpx.Client(
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            cookies={"MoodleSession": cookie},
            follow_redirects=False,
            timeout=25.0,
        )

    def update_cookie(self, new_cookie: str) -> None:
        self.session_cookie = new_cookie.strip()
        try:
            self.client.close()
        except Exception:
            pass
        self._init_client(self.session_cookie)

    def verify_session(self, cookie: Optional[str] = None) -> Dict[str, Any]:
        chk_cookie = (cookie or self.session_cookie).strip()
        if not chk_cookie:
            return {"active": False, "reason": "Cookie vacía"}

        c = (
            self.client
            if cookie is None
            else httpx.Client(
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                cookies={"MoodleSession": chk_cookie},
                follow_redirects=False,
                timeout=20.0,
            )
        )
        should_close = cookie is not None
        try:
            r = c.get(f"{BASE_URL}/my/")
            if r.status_code == 200 and "login" not in r.text.lower()[:400]:
                # Extract student name if available
                user_m = re.search(r'<span class="usertext[^"]*">(.*?)</span>', r.text, re.S)
                user_name = clean_text(user_m.group(1)) if user_m else "Estudiante PSM"
                return {"active": True, "user": user_name, "html": r.text}
            loc = r.headers.get("location", "").lower()
            if r.status_code in (301, 302, 303, 307) or "login" in loc:
                return {"active": False, "reason": "Sesión expirada en SAIA (Redirección a login)"}
            return {"active": False, "reason": f"Código HTTP inesperado: {r.status_code}"}
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            return {"active": False, "reason": f"Error de red/timeout con SAIA: {e}"}
        except Exception as e:
            return {"active": False, "reason": str(e)}
        finally:
            if should_close:
                try:
                    c.close()
                except Exception:
                    pass

    def discover_enrolled_course_ids(self, my_html: Optional[str] = None) -> List[str]:
        """Dynamically discovers enrolled course IDs from /my/ and grade overview, merging with known IDs."""
        discovered = []
        html_sources = []
        if my_html:
            html_sources.append(my_html)
        else:
            try:
                r = self.client.get(f"{BASE_URL}/my/")
                if r.status_code == 200:
                    html_sources.append(r.text)
            except Exception:
                pass

        try:
            r_ov = self.client.get(f"{BASE_URL}/grade/report/overview/index.php")
            if r_ov.status_code == 200:
                html_sources.append(r_ov.text)
        except Exception:
            pass

        for html in html_sources:
            matches = re.findall(r"course/view\.php\?id=(\d+)", html)
            for cid in matches:
                if cid != "1" and cid not in discovered:
                    discovered.append(cid)

        # Fallback/Ensure default active semester IDs are included if dynamic page used JS rendering
        for cid in DEFAULT_COURSE_IDS:
            if cid not in discovered:
                discovered.append(cid)
        return discovered

    def sync_all_courses(self) -> Dict[str, Any]:
        status = self.verify_session()
        if not status.get("active"):
            return {
                "synced": False,
                "session_active": False,
                "reason": status.get("reason", "Sesión inactiva"),
                "courses": [],
            }

        course_ids = self.discover_enrolled_course_ids(status.get("html"))
        cal_events = self.get_calendar()

        def scrape_single_course(cid: str) -> Dict[str, Any]:
            cname_raw, total, grades = self.get_course_grades(cid)
            cname = sanitize_course_name(cname_raw)
            acts, teacher_name = self.get_course_activities_and_teacher(cid, cal_events.get(cid, []))
            return {
                "id": cid,
                "name": cname,
                "teacher_name": teacher_name,
                "total": total,
                "grades": grades,
                "activities": acts,
            }

        with ThreadPoolExecutor(max_workers=6) as executor:
            courses_data = list(executor.map(scrape_single_course, course_ids))

        return {
            "synced": True,
            "session_active": True,
            "user": status.get("user", "Estudiante PSM"),
            "courses": courses_data,
        }

    def get_calendar(self) -> Dict[str, List[Dict[str, str]]]:
        url = f"{BASE_URL}/calendar/view.php?view=upcoming"
        events: Dict[str, List[Dict[str, str]]] = {}
        try:
            res = self.client.get(url)
            if res.status_code == 200:
                blocks = re.findall(
                    r'<div[^>]*data-type="event"[^>]*data-course-id="(\d+)"[^>]*>(.*?)</div>\s*</div>\s*</div>',
                    res.text,
                    re.S,
                )
                for cid, block in blocks:
                    title_m = re.search(r'data-event-title="([^"]*)"', block)
                    if not title_m:
                        title_m = re.search(r'<h3[^>]*class="[^"]*name[^"]*"[^>]*>(.*?)</h3>', block, re.S)
                    title = clean_text(title_m.group(1)) if title_m else "Evento"
                    date_m = re.search(r'<span[^>]*class="[^"]*date\b[^"]*"[^>]*>(.*?)</span>', block, re.S)
                    date_str = clean_text(date_m.group(1)) if date_m else ""
                    link_m = re.search(
                        r'<a[^>]*href="(https://saia2\.psm\.edu\.ve/mod/(?:assign|quiz)/view\.php\?id=\d+[^"]*)"',
                        block,
                    )
                    link = link_m.group(1).replace("&amp;", "&") if link_m else ""
                    events.setdefault(cid, []).append({"title": title, "date": date_str, "link": link})
        except Exception:
            pass
        return events

    def get_course_grades(self, cid: str) -> Tuple[str, str, List[Dict[str, str]]]:
        url = f"{BASE_URL}/grade/report/user/index.php?id={cid}"
        try:
            res = self.client.get(url)
            if res.status_code != 200:
                return f"Curso {cid}", "Sin calificar", []
            html = res.text
            h1_m = re.search(r'class="page-header-headings"[^>]*>.*?<h1>(.*?)</h1>', html, re.S)
            if not h1_m:
                h1_m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
            cname = clean_text(h1_m.group(1)) if h1_m else f"Curso {cid}"

            items: List[Dict[str, str]] = []
            course_total = "Sin calificar"
            table_m = re.search(r'<table[^>]*class="[^"]*user-grade[^"]*"[^>]*>(.*?)</table>', html, re.S)
            if table_m:
                rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table_m.group(1), re.S)
                for r in rows:
                    r_clean = re.sub(r'<div[^>]*class="[^"]*action-menu[^"]*"[^>]*>.*?</div>', "", r, flags=re.S)
                    if "total" in r_clean.lower() and "itemname" in r_clean:
                        tds = re.findall(r"<td[^>]*>(.*?)</td>", r_clean, re.S)
                        clean_tds = [clean_text(td) for td in tds]
                        if len(clean_tds) >= 3:
                            nota = clean_tds[1] if clean_tds[1] and clean_tds[1] != "-" else "Sin calificar"
                            rango = clean_tds[2] if clean_tds[2] else ""
                            course_total = (
                                f"{nota} / {rango.split('–')[-1].split('-')[-1].strip()}"
                                if (rango and nota != "Sin calificar")
                                else nota
                            )
                    item_m = re.search(r'<th[^>]*class="[^"]*item\b[^"]*"[^>]*>(.*?)</th>', r_clean, re.S)
                    if item_m:
                        item_title = clean_text(item_m.group(1))
                        for prefix in ["Tarea", "Cuestionario", "Foro"]:
                            if item_title.startswith(prefix):
                                item_title = item_title[len(prefix) :].strip()
                        tds = re.findall(r"<td[^>]*>(.*?)</td>", r_clean, re.S)
                        clean_tds = [clean_text(td) for td in tds]
                        pond = clean_tds[0] if len(clean_tds) > 0 else "-"
                        calif = clean_tds[1] if len(clean_tds) > 1 else "-"
                        items.append({"title": item_title, "ponderacion": pond, "calificacion": calif})
            return cname, course_total, items
        except Exception:
            return f"Curso {cid}", "Sin calificar", []

    def get_course_activities_and_teacher(
        self, cid: str, cal_events: List[Dict[str, str]]
    ) -> Tuple[List[Dict[str, Any]], str]:
        url = f"{BASE_URL}/course/view.php?id={cid}"
        try:
            res = self.client.get(url)
            if res.status_code != 200:
                return [], "Docente de la Cátedra"
            teacher_m = re.search(
                r"(?:Docente|Profesor(?:a)?|Facilitador(?:a)?|Tutor(?:a)?|Ing\.|Lic\.|MSc\.|Dr\.)[:\s]+([A-ZÁÉÍÓÚÑa-záéíóúñ\.\s]{4,45})",
                clean_text(res.text),
            )
            teacher_name = teacher_m.group(1).strip() if teacher_m else "Docente de la Cátedra"

            # Map each activity link to its section title and section resource attachments
            soup_course = BeautifulSoup(res.text, "html.parser")
            link_to_section_meta: Dict[str, Dict[str, Any]] = {}
            for sec in soup_course.find_all(["li", "div"], class_=re.compile(r"\b(?:section|course-section)\b")):
                sec_title_node = sec.find(["h3", "h2", "h4"], class_=re.compile(r"sectionname|course-section-header"))
                if not sec_title_node:
                    sec_title_node = sec.find(["h3", "h2"])
                sec_title = sec_title_node.get_text(" ", strip=True) if sec_title_node else ""
                sec_resources: List[Dict[str, str]] = []
                for a_res in sec.find_all("a", href=re.compile(r"/mod/resource/view\.php\?id=\d+")):
                    r_href = a_res["href"].replace("&amp;", "&")
                    r_name = clean_text(a_res.get_text(" ", strip=True)).replace("Archivo", "").strip() or "Recurso_Unidad"
                    if not any(x["url"] == r_href for x in sec_resources):
                        sec_resources.append({"name": r_name, "url": r_href})
                for a_act in sec.find_all("a", href=re.compile(r"/mod/(?:assign|quiz)/view\.php\?id=\d+")):
                    a_href = a_act["href"].replace("&amp;", "&")
                    link_to_section_meta[a_href] = {
                        "section_title": sec_title,
                        "section_resources": sec_resources,
                    }

            matches = re.findall(
                r'<a[^>]*href="(https://saia2\.psm\.edu\.ve/mod/(assign|quiz)/view\.php\?id=\d+)"[^>]*>(.*?)</a>',
                res.text,
                re.S,
            )
            activities = []
            seen = set()
            for link, mod_type, raw_title in matches:
                if link in seen:
                    continue
                seen.add(link)
                title = clean_text(raw_title)
                for suffix in ["Tarea", "Cuestionario"]:
                    if title.endswith(suffix):
                        title = title[: -len(suffix)].strip()
                detail = self.check_activity_detail(link, mod_type)

                sec_meta = link_to_section_meta.get(link, {})
                sec_title = sec_meta.get("section_title", "")
                if sec_title and detail.get("description_text") and not detail["description_text"].startswith("UNIDAD / SECCIÓN:"):
                    detail["description_text"] = f"UNIDAD / SECCIÓN: {sec_title}\n\n{detail['description_text']}"
                if sec_meta.get("section_resources"):
                    existing_urls = {x["url"] for x in detail.get("attachments", [])}
                    for sr in sec_meta["section_resources"]:
                        if sr["url"] not in existing_urls:
                            detail.setdefault("attachments", []).append(sr)

                act_id_m = re.search(r"[?&]id=(\d+)", link)
                act_id = act_id_m.group(1) if act_id_m else ""

                matched_date = None
                for ev in cal_events:
                    ev_link = ev.get("link", "")
                    ev_id_m = re.search(r"[?&]id=(\d+)", ev_link)
                    ev_id = ev_id_m.group(1) if ev_id_m else ""
                    if act_id and ev_id and act_id == ev_id:
                        matched_date = ev["date"]
                        break
                    if link and ev_link and link == ev_link:
                        matched_date = ev["date"]
                        break
                    clean_act = re.sub(r"[^a-z0-9]", "", simplify_activity_title(title).lower())
                    clean_ev = re.sub(r"[^a-z0-9]", "", simplify_activity_title(ev.get("title", "")).lower())
                    if clean_act and clean_ev and (clean_act == clean_ev or clean_act in clean_ev):
                        matched_date = ev["date"]
                        break

                fecha_final = detail.get("fecha_entrega") or matched_date
                activities.append(
                    {
                        "title": title,
                        "type": "Tarea" if mod_type == "assign" else "Cuestionario",
                        "link": link,
                        "fecha_calendario": fecha_final,
                        **detail,
                    }
                )
            return activities, teacher_name
        except Exception:
            return [], "Docente de la Cátedra"

    def check_activity_detail(self, link: str, mod_type: str) -> Dict[str, Any]:
        try:
            res = self.client.get(link)
            if res.status_code != 200:
                return {
                    "estado": "Sin datos",
                    "tiempo": "-",
                    "fecha_entrega": None,
                    "es_realizada": False,
                    "es_atrasada": False,
                    "description_text": "",
                    "attachments": [],
                }
            html = res.text
            desc_text, attachments = self._parse_description_and_attachments(html)

            if mod_type == "assign":
                entrega_m = re.search(r"<th[^>]*>Estado de la entrega</th>\s*<td[^>]*>(.*?)</td>", html, re.S | re.I)
                calif_m = re.search(
                    r"<th[^>]*>Estado de la calificaci[^\"]*</th>\s*<td[^>]*>(.*?)</td>", html, re.S | re.I
                )
                tiempo_m = re.search(r"<th[^>]*>Tiempo restante</th>\s*<td[^>]*>(.*?)</td>", html, re.S | re.I)
                fecha_m = re.search(r"<th[^>]*>Fecha de entrega</th>\s*<td[^>]*>(.*?)</td>", html, re.S | re.I)

                estado = clean_text(entrega_m.group(1)) if entrega_m else "Sin envíos"
                calif_est = clean_text(calif_m.group(1)) if calif_m else "-"
                tiempo = clean_text(tiempo_m.group(1)) if tiempo_m else "-"
                fecha_entrega = clean_text(fecha_m.group(1)) if fecha_m else None

                if not fecha_entrega:
                    f_alt = re.search(r"(?:Fecha de entrega|Cierre)[^\.\n<]*?:\s*([^\n<]+)", html, re.I)
                    if f_alt:
                        fecha_entrega = clean_text(f_alt.group(1))

                es_realizada = (
                    any(x in estado.lower() for x in ["enviado para calificar", "entregado"])
                    or "calificado" in calif_est.lower()
                )
                es_atrasada = "retrasada" in tiempo.lower() or "overdue" in tiempo.lower()
                return {
                    "estado": estado,
                    "tiempo": tiempo,
                    "fecha_entrega": fecha_entrega,
                    "es_realizada": es_realizada,
                    "es_atrasada": es_atrasada,
                    "description_text": desc_text,
                    "attachments": attachments,
                }
            else:
                html_lower = html.lower()
                es_realizada = (
                    "reintentar el cuestionario" in html_lower
                    or "resumen de sus intentos anteriores" in html_lower
                    or "calificación más alta" in html_lower
                    or ("revisión" in html_lower and "finalizado" in html_lower)
                )
                fecha_cierre = None
                es_atrasada = False
                cierre_pasado_m = re.search(r"(?:Cerró|se cerró el|cerrado el)[^\.\n<]*?:\s*([^\n<]+)", html, re.I)
                if not cierre_pasado_m:
                    cierre_pasado_m = re.search(r"Este cuestionario se cerr[oó] el\s*([^<\.]+)", html, re.I)
                if cierre_pasado_m:
                    fecha_cierre = clean_text(cierre_pasado_m.group(1))
                    if not es_realizada:
                        es_atrasada = True
                    tiempo = f"Cerró: {fecha_cierre}"
                else:
                    cierre_futuro_m = re.search(
                        r"(?:Cierra|se cerrar[aá] el|Cierre)[^\.\n<]*?:\s*([^\n<]+)", html, re.I
                    )
                    if not cierre_futuro_m:
                        cierre_futuro_m = re.search(r"Este cuestionario se cerrar[aá] el\s*([^<\.]+)", html, re.I)
                    if cierre_futuro_m:
                        fecha_cierre = clean_text(cierre_futuro_m.group(1))
                        es_atrasada = False
                        tiempo = f"Cierra: {fecha_cierre}"
                    else:
                        if "este cuestionario está cerrado" in html_lower or "cuestionario cerrado" in html_lower:
                            if not es_realizada:
                                es_atrasada = True
                            tiempo = "Cuestionario cerrado"
                        else:
                            tiempo = "-"
                estado = "Realizado" if es_realizada else ("Vencido" if es_atrasada else "Pendiente")
                return {
                    "estado": estado,
                    "tiempo": tiempo,
                    "fecha_entrega": fecha_cierre,
                    "es_realizada": es_realizada,
                    "es_atrasada": es_atrasada,
                    "description_text": desc_text,
                    "attachments": attachments,
                }
        except Exception:
            return {
                "estado": "Error",
                "tiempo": "-",
                "fecha_entrega": None,
                "es_realizada": False,
                "es_atrasada": False,
                "description_text": "",
                "attachments": [],
            }

    def _parse_description_and_attachments(self, html: str) -> Tuple[str, List[Dict[str, str]]]:
        soup = BeautifulSoup(html, "html.parser")
        intro_nodes = soup.find_all("div", class_=re.compile(r"activity-description|activity-instruction|intro"))
        if not intro_nodes:
            single = soup.find(id="intro") or soup.find("div", class_="generalbox")
            if single:
                intro_nodes = [single]

        desc_parts: List[str] = []
        for node in intro_nodes:
            raw_txt = node.get_text("\n", strip=True)
            cleaned_lines = [line.strip() for line in raw_txt.splitlines() if line.strip()]
            block = "\n".join(cleaned_lines)
            if block and block not in desc_parts:
                desc_parts.append(block)
        desc_text = "\n\n".join(desc_parts)

        attachments: List[Dict[str, str]] = []
        seen_urls = set()
        for a in soup.find_all("a", href=True):
            href = a["href"].replace("&amp;", "&")
            if "pluginfile.php" in href or "/mod/resource/view.php" in href:
                if href not in seen_urls:
                    seen_urls.add(href)
                    parsed = urllib.parse.urlparse(href)
                    filename = urllib.parse.unquote(os.path.basename(parsed.path))
                    if not filename or filename == "view.php":
                        filename = clean_text(a.get_text(" ", strip=True)) or "adjunto_docente"
                    attachments.append({"name": filename, "url": href})
        return desc_text.strip(), attachments

    def fetch_and_download_assignment_materials(
        self,
        assignment_id: str,
        link: str,
        extra_attachments: Optional[List[Dict[str, str]]] = None,
    ) -> Tuple[str, List[Dict[str, str]], List[str]]:
        """Fetches fresh description and downloads any teacher attachments from SAIA."""
        if not link:
            return "", [], []
        try:
            res = self.client.get(link)
            if res.status_code != 200:
                return "", [], []
            desc_text, attachments = self._parse_description_and_attachments(res.text)
            seen_u = {x["url"] for x in attachments}
            for ea in extra_attachments or []:
                if ea.get("url") and ea["url"] not in seen_u:
                    seen_u.add(ea["url"])
                    attachments.append(ea)

            local_paths: List[str] = []
            target_dir = os.path.join(DOWNLOADS_DIR, assignment_id)
            os.makedirs(target_dir, exist_ok=True)

            for att in attachments:
                url = att["url"]
                safe_name = re.sub(r'[<>:"/\\|?*]', "_", att["name"]).strip()
                try:
                    file_res = self.client.get(url, follow_redirects=True)
                    if file_res.status_code == 200 and len(file_res.content) > 0:
                        redirected_path = urllib.parse.unquote(
                            os.path.basename(urllib.parse.urlparse(str(file_res.url)).path)
                        )
                        _, redir_ext = os.path.splitext(redirected_path)
                        _, cur_ext = os.path.splitext(safe_name)
                        if redir_ext and not cur_ext:
                            safe_name = f"{safe_name}{redir_ext}"
                        elif redirected_path and redirected_path != "view.php" and not cur_ext:
                            safe_name = re.sub(r'[<>:"/\\|?*]', "_", redirected_path)
                        dest_path = os.path.join(target_dir, safe_name)
                        with open(dest_path, "wb") as f:
                            f.write(file_res.content)
                        local_paths.append(dest_path)
                except Exception:
                    pass
            return desc_text, attachments, local_paths
        except Exception:
            return "", [], []
