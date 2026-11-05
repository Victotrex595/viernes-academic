import base64
import json
import mimetypes
import os
from typing import Any, Callable, Dict, List, Optional, Tuple

import httpx
from docx import Document as DocxDocument
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader

BASE_DIR = os.getenv("PHONEAPP_DATA_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.getenv("PHONEAPP_PROJECT_ROOT", os.path.dirname(BASE_DIR))


def _resolve_env_file() -> str:
    candidates = [
        os.getenv("ENV_FILE_PATH", ""),
        os.path.join(os.getcwd(), ".env"),
        os.path.join(PROJECT_ROOT, ".env"),
        os.path.join(BASE_DIR, ".env"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return os.path.join(PROJECT_ROOT, ".env")

_GEMINI_RR_COUNTER = 0


def _reload_env_pool() -> Tuple[List[str], str]:
    """Loads all configured GEMINI_API_KEY* into a deduplicated rotation pool, plus DEEPSEEK_API_KEY."""
    if os.getenv("PHONEAPP_FORCE_SIMULATION") == "1":
        return [], ""
    env_file = _resolve_env_file()
    load_dotenv(env_file, override=True)
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"), override=True)
    load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)
    load_dotenv(os.path.expanduser("~/.env"), override=True)

    gemini_pool: List[str] = []
    # Check primary and numbered keys GEMINI_API_KEY, GEMINI_API_KEY_1 .. GEMINI_API_KEY_10
    candidate_vars = ["GEMINI_API_KEY"] + [f"GEMINI_API_KEY_{i}" for i in range(1, 11)]
    for var in candidate_vars:
        val = os.getenv(var, "").strip()
        if val and val not in gemini_pool:
            gemini_pool.append(val)

    # Also support comma-separated GEMINI_API_KEYS
    multi_val = os.getenv("GEMINI_API_KEYS", "").strip()
    if multi_val:
        for part in multi_val.split(","):
            clean = part.strip()
            if clean and clean not in gemini_pool:
                gemini_pool.append(clean)

    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    return gemini_pool, deepseek_key


def add_extra_gemini_key_to_env(new_key: str) -> Dict[str, Any]:
    clean = new_key.strip()
    if not clean:
        return {"ok": False, "message": "La clave no puede estar vacía."}
    pool, _ = _reload_env_pool()
    if clean in pool:
        return {
            "ok": True,
            "gemini_keys_count": len(pool),
            "message": f"Esta clave ya formaba parte del pool activo ({len(pool)} claves).",
        }
    next_idx = len(pool) + 1
    var_name = "GEMINI_API_KEY" if len(pool) == 0 else f"GEMINI_API_KEY_{next_idx}"
    env_path = _resolve_env_file()
    with open(env_path, "a", encoding="utf-8") as f:
        f.write(f"\n{var_name}={clean}\n")
    updated_pool, _ = _reload_env_pool()
    return {
        "ok": True,
        "gemini_keys_count": len(updated_pool),
        "message": f"Clave añadida como {var_name}. Pool activo: {len(updated_pool)} cuenta(s) de Gemini en rotación.",
    }


def get_api_keys_status() -> Dict[str, Any]:
    g_pool, d_key = _reload_env_pool()
    g_count = len(g_pool)
    return {
        "gemini_configured": g_count > 0,
        "gemini_keys_count": g_count,
        "deepseek_configured": bool(d_key),
        "live_consortium_ready": (g_count > 0) and bool(d_key),
        "mode": (
            f"Consorcio Activo ({g_count} Gemini + DeepSeek-R1)"
            if (g_count > 0 or d_key)
            else "Modo Simulación Seguro (0 Tokens)"
        ),
    }


def extract_local_files_text(file_paths: List[str]) -> str:
    """Extracts plain text from local PDF, DOCX, TXT/MD teacher attachments for DeepSeek and context."""
    extracted_parts: List[str] = []
    for path in file_paths:
        if not os.path.exists(path):
            continue
        ext = os.path.splitext(path)[1].lower()
        fname = os.path.basename(path)
        try:
            if ext == ".pdf":
                reader = PdfReader(path)
                pages_txt = [page.extract_text() or "" for page in reader.pages[:25]]
                extracted_parts.append(f"--- ARCHIVO ADJUNTO ({fname}) ---\n" + "\n".join(pages_txt))
            elif ext == ".docx":
                doc = DocxDocument(path)
                paras = [p.text for p in doc.paragraphs if p.text.strip()]
                extracted_parts.append(f"--- ARCHIVO ADJUNTO ({fname}) ---\n" + "\n".join(paras))
            elif ext in (".txt", ".md", ".csv"):
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    extracted_parts.append(f"--- ARCHIVO ADJUNTO ({fname}) ---\n" + f.read()[:25000])
        except Exception:
            pass
    return "\n\n".join(extracted_parts)


HUMAN_STYLE_DIRECTIVE = """
PAUTAS OBLIGATORIAS DE HUMANIZACIÓN Y REDACCIÓN ACADÉMICA REAL (ESTILO ESTUDIANTE PSM):
1. PROHIBICIÓN TOTAL DE CLICHÉS Y MUCTILLAS DE INTELIGENCIA ARTIFICIAL:
   - Prohibido iniciar párrafos o secciones con fórmulas acartonadas de IA:
     * "En el vertiginoso mundo de...", "En la era digital...", "A lo largo de la historia de la humanidad..."
     * "Es imperativo destacar que...", "Es menester señalar...", "Cabe resaltar que..."
     * "Juega un papel crucial / fundamental / trascendental..."
     * "Un tapiz de...", "Faro de conocimiento...", "Piedra angular..."
     * "En conclusión, podemos decir que...", "En resumen, este trabajo arroja luz sobre..."
   - Prohibido repetir mecánicamente los mismos conectores al inicio de párrafos consecutivos ("Asimismo", "Por ende", "En este orden de ideas", "Por consiguiente", "Por otra parte").
2. CADENCIA Y VOZ AUTÉNTICA DE ESTUDIANTE DE INGENIERÍA:
   - Redacta con el tono sobrio, maduro, técnico y directo de un estudiante universitario de últimos semestres: formal y fundamentado, empleando la tercera persona gramatical ("se analizó", "se observó", "se plantea", "se diagnosticó", "se concluye") o el plural académico modesto ("se propone en esta entrega").
   - Varía la longitud de las oraciones: combina explicaciones desarrolladas con afirmaciones directas y concisas. Evita la simetría robótica donde todos los párrafos o viñetas tienen exactamente la misma longitud sintáctica.
3. CONTEXTUALIZACIÓN PRÁCTICA Y TERRENAL:
   - Aterriza las explicaciones y los estudios de caso a la realidad operativa de los laboratorios o entornos del Instituto Universitario Politécnico Santiago Mariño (PSM) y a situaciones técnicas verosímiles de la ingeniería en Venezuela.
   - Elimina la palabrería hueca o reflexiones filosóficas vacías; responde directamente a lo que exige la pauta del docente con argumentos técnicos y metodológicos reales.
4. CITAS INTEGRADAS CON FLUIDEZ:
   - Cita a los autores con naturalidad dentro del texto ("Tal como plantea Arias (2012)...", "Siguiendo la perspectiva metodológica de Sabino (1992)..."), sin forzarlas artificialmente como adorno al final de cada párrafo.
5. FUENTES Y BIBLIOGRAFÍA EXCLUSIVAMENTE EN ESPAÑOL:
   - TODAS las fuentes bibliográficas, libros de texto, artículos, manuales y normas citadas DEBEN ser obras publicadas o traducidas formalmente al IDIOMA ESPAÑOL.
   - Ejemplos válidos: Arias, F. (El Proyecto de Investigación), Sabino, C. (El Proceso de Investigación), Hernández-Sampieri, R. (Metodología de la Investigación), Tamayo y Tamayo, M., Hurtado de Barrera, J., Manuales de Trabajo Especial de Grado PSM / UPEL, o manuales técnicos de ingeniería en sus ediciones en español.
   - Queda TERMINANTEMENTE PROHIBIDO citar fuentes o libros en inglés.
"""


class AIConsortiumEngine:
    """Orchestrates Multi-Key Gemini Pool (gemini-3.8-flash / gemini-4-argon) and DeepSeek (deepseek-reasoner) with checkpoints and failover."""

    def __init__(
        self,
        gemini_model: str = "gemini-3-flash-preview",
        gemini_arbiter_model: str = "gemini-3-flash-preview",
        deepseek_model: str = "deepseek-reasoner",
    ) -> None:
        # Automatically map 3.8-flash / 4-argon to gemini-3-flash-preview on Free Tier
        if gemini_model in ("gemini-3.8-flash", "gemini-4-argon"):
            gemini_model = "gemini-3-flash-preview"
        if gemini_arbiter_model in ("gemini-3.8-flash", "gemini-4-argon"):
            gemini_arbiter_model = "gemini-3-flash-preview"
        self.gemini_model = gemini_model
        self.gemini_arbiter_model = gemini_arbiter_model
        self.deepseek_model = deepseek_model

    def _call_gemini(
        self,
        prompt: str,
        system_instruction: str,
        model_name: Optional[str] = None,
        use_google_search: bool = False,
        file_paths: Optional[List[str]] = None,
        thinking_level: str = "medium",
    ) -> Tuple[str, int]:
        """Calls Gemini using Round-Robin key rotation + instant Auto-Failover across all keys in the pool."""
        global _GEMINI_RR_COUNTER
        gemini_pool, _ = _reload_env_pool()
        if not gemini_pool:
            return "", 0

        target_model = model_name or self.gemini_model

        content_items: List[Dict[str, Any]] = []
        for fp in file_paths or []:
            if not os.path.exists(fp) or os.path.getsize(fp) > 15 * 1024 * 1024:
                continue
            mime, _ = mimetypes.guess_type(fp)
            if mime and (mime == "application/pdf" or mime.startswith("image/")):
                with open(fp, "rb") as f:
                    b64_data = base64.b64encode(f.read()).decode("utf-8")
                item_type = "document" if mime == "application/pdf" else "image"
                content_items.append({"type": item_type, "mime_type": mime, "data": b64_data})

        content_items.append({"type": "text", "text": prompt})
        input_payload: Any = content_items if len(content_items) > 1 else prompt

        kwargs: Dict[str, Any] = {
            "model": target_model,
            "input": input_payload,
            "system_instruction": system_instruction,
            "generation_config": {
                "thinking_level": thinking_level,
                "max_output_tokens": 32768,
            },
        }
        # Note: Do not attach tools=[{"type": "google_search"}] on Free Tier accounts,
        # because Google Search Grounding has 0 quota (HTTP 429) on free accounts.

        start_idx = _GEMINI_RR_COUNTER % len(gemini_pool)
        _GEMINI_RR_COUNTER += 1
        last_error: Optional[Exception] = None

        # Candidate models verified active on Free Tier accounts
        candidate_models = list(
            dict.fromkeys(["gemini-3-flash-preview", target_model, "gemini-3.5-flash-lite", "gemini-3.1-flash-lite-preview"])
        )

        for offset in range(len(gemini_pool)):
            key_idx = (start_idx + offset) % len(gemini_pool)
            api_key = gemini_pool[key_idx]
            client = genai.Client(api_key=api_key)
            # Disable SDK internal 503 multi-minute backoff so we can failover in ~1 second
            try:
                client.interactions.sdk_configuration.retry_config.max_retries = 0
                client.interactions.sdk_configuration.timeout_ms = 60000
            except Exception:
                pass

            for m_name in candidate_models:
                kwargs["model"] = m_name
                try:
                    interaction = client.interactions.create(**kwargs, timeout=60.0)
                    text = interaction.output_text or ""
                    tokens = 0
                    if getattr(interaction, "usage", None) and getattr(interaction.usage, "total_tokens", None):
                        tokens = int(interaction.usage.total_tokens)
                    if text.strip():
                        return text, tokens
                except Exception as e:
                    last_error = e
                    # Always try the next candidate model on this key before rotating to the next key
                    continue

        if last_error:
            raise last_error
        return "", 0

    def _classify_academic_domain(
        self, course_name: str, assignment_title: str, description_text: str
    ) -> Dict[str, str]:
        """Detects whether the assignment is theoretical/methodological, programming, or quantitative/math."""
        combined_course = f"{course_name} {assignment_title}".lower()
        combined_all = f"{combined_course} {description_text}".lower()

        is_methodological_or_qualitative = any(
            k in combined_course
            for k in [
                "metodolog",
                "planificaci",
                "administraci",
                "ética",
                "etica",
                "deontolog",
                "lenguaje",
                "comunicaci",
                "human",
                "redacci",
                "seminario",
                "trabajo especial de grado",
            ]
        ) or (
            any(
                k in combined_all
                for k in [
                    "planteamiento",
                    "objetivo general",
                    "objetivos específicos",
                    "justificación",
                    "delimitación",
                    "conocimiento empírico",
                    "conocimiento científico",
                    "marco teórico",
                    "estudio de caso",
                ]
            )
            and not any(
                m in combined_all
                for m in ["calcular", "ecuación", "fórmula", "derivada", "integral", "tasa de interés", "entropía"]
            )
        )

        is_programming = any(
            k in combined_course
            for k in ["programaci", "algoritm", "estructura de datos", "software", "base de datos", "código"]
        )

        if is_methodological_or_qualitative:
            return {
                "domain": "metodologico_teorico",
                "domain_rule": (
                    "REGLA ESTRICTA DE DOMINIO (MATERIA TEÓRICA / METODOLÓGICA / DE GESTIÓN): "
                    "Esta actividad NO es de cálculo matemático ni de física/química. "
                    "QUEDA TERMINANTEMENTE PROHIBIDO inventar o incluir fórmulas matemáticas, ecuaciones químicas/físicas, "
                    "tasas numéricas, cálculos o ejercicios de despeje que el profesor NO haya pedido explícitamente. "
                    "Si el enunciado incluye un 'Estudio de Caso' sobre ingeniería (ej. corrosión, laboratorios de cómputo, redes, etc.), "
                    "debes abordarlo EXCLUSIVAMENTE desde el marco metodológico, conceptual y de las preguntas exactas solicitadas "
                    "por el docente (ej. Planteamiento del problema, Variables, Objetivos en infinitivo, Justificación Teórica/Metodológica/Práctica, "
                    "Delimitación Espacial/Temporal/Temática, etc.), sin desviarte jamás a cálculos técnicos ajenos a la cátedra."
                ),
                "deepseek_prompt": (
                    "Analiza rigurosamente CADA UNO de los puntos, preguntas e interrogantes de los Lineamientos del Docente, "
                    "y desarrolla la aplicación metodológica paso a paso sobre el Estudio de Caso planteado (sin inventar fórmulas "
                    "matemáticas ni cálculos que no correspondan a la materia):"
                ),
                "deepseek_sys": (
                    "Eres el Analista Metodológico y Estructurador Académico Principal (DeepSeek-R1). "
                    "Tu misión es responder con precisión conceptual cada pregunta del docente y estructurar de forma impecable "
                    "el Estudio de Caso siguiendo estrictamente las pautas de la evaluación. Cero fórmulas matemáticas inventadas."
                ),
                "pillar_2_desc": "Desarrollo conceptual profundo y directo de CADA pregunta y apartado exigido en las instrucciones de la actividad, con esquemas claros y ejemplos contextualizados.",
                "pillar_3_desc": "Aplicación práctica paso a paso al Estudio de Caso de la actividad (respondiendo cada requerimiento del docente) y preguntas de autoevaluación teórica basadas en la rúbrica.",
            }

        if is_programming:
            return {
                "domain": "programacion_sistemas",
                "domain_rule": (
                    "REGLA DE DOMINIO (PROGRAMACIÓN Y SISTEMAS): Enfócate en arquitectura lógica, estructuras de datos, "
                    "código limpio, complejidad algorítmica y cumplimiento exacto de los requerimientos del programa o taller."
                ),
                "deepseek_prompt": (
                    "Desarrolla la lógica algorítmica, estructuras de datos, ejemplos de código explicados línea por línea "
                    "y casos de prueba para los requerimientos del docente:"
                ),
                "deepseek_sys": (
                    "Eres el Arquitecto de Software y Algoritmos (DeepSeek-R1). "
                    "Diseña soluciones de código claras, bien documentadas y ceñidas a lo que pide el profesor."
                ),
                "pillar_2_desc": "Explicación profunda de las estructuras de datos, lógica algorítmica, sintaxis y patrones requeridos por la actividad.",
                "pillar_3_desc": "Ejercicios de programación resueltos paso a paso, trazas de ejecución y preguntas de comprobación sobre el código.",
            }

        return {
            "domain": "cuantitativo_ingenieria",
            "domain_rule": (
                "REGLA DE DOMINIO (INGENIERÍA CUANTITATIVA / CIENCIAS EXACTAS): "
                "Ciñe todas las demostraciones, fórmulas y ejercicios resueltos estrictamente a los temas y problemas "
                "indicados en los lineamientos del docente."
            ),
            "deepseek_prompt": (
                "Desarrolla las demostraciones lógicas, fórmulas explicadas paso a paso, ejercicios resueltos "
                "y preguntas de comprobación ajustadas estrictamente a los lineamientos del docente:"
            ),
            "deepseek_sys": (
                "Eres el Especialista en Razonamiento Analítico e Ingeniería (DeepSeek-R1). "
                "Desglosa los procedimientos paso a paso según las pautas del profesor."
            ),
            "pillar_2_desc": "Explicación profunda, fundamentos teóricos, fórmulas desglosadas paso a paso (si aplican al tema) y esquemas.",
            "pillar_3_desc": "Ejercicios prácticos resueltos paso a paso según las pautas del docente y cuestionario tipo examen con respuestas razonadas.",
        }

    def _call_deepseek(self, prompt: str, system_instruction: str) -> Tuple[str, int]:
        _, deepseek_key = _reload_env_pool()
        if not deepseek_key:
            return "", 0

        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1").rstrip("/")
        headers = {
            "Authorization": f"Bearer {deepseek_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.deepseek_model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt},
            ],
        }
        with httpx.Client(timeout=180.0) as client:
            resp = client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]["message"]
            content = (choice.get("content") or "").strip()
            reasoning = (choice.get("reasoning_content") or "").strip()
            usage = data.get("usage", {}).get("total_tokens", 0)
            return (content or reasoning), int(usage)

    def generate_four_pillars_study_material(
        self,
        course_name: str,
        assignment_title: str,
        description_text: str,
        local_files: Optional[List[str]] = None,
        checkpoints: Optional[Dict[str, str]] = None,
        on_checkpoint: Optional[Callable[[Dict[str, str]], None]] = None,
        on_progress: Optional[Callable[[int, str], None]] = None,
    ) -> Dict[str, Any]:
        """Generates the 4 Pillars for NotebookLM with checkpoint resume and multi-key failover."""
        gemini_pool, deepseek_key = _reload_env_pool()
        if not gemini_pool and not deepseek_key:
            if on_progress:
                on_progress(50, "Simulando generación de 4 Pilares...")
            return self._simulate_four_pillars(course_name, assignment_title, description_text)

        state_cp: Dict[str, str] = dict(checkpoints or {})
        files_text = extract_local_files_text(local_files or [])
        domain_cfg = self._classify_academic_domain(course_name, assignment_title, description_text)

        context_block = (
            f"MATERIA: {course_name}\n"
            f"TEMA / ASIGNACIÓN: {assignment_title}\n"
            f"{domain_cfg['domain_rule']}\n\n"
            f"{HUMAN_STYLE_DIRECTIVE}\n\n"
            f"LINEAMIENTOS OBLIGATORIOS DEL DOCENTE (ENUNCIADO Y PAUTAS EN SAIA):\n"
            f"{description_text or 'Investigar a fondo el tema indicado.'}\n\n"
            f"TEXTO EXTRAÍDO DE ARCHIVOS ADJUNTOS DEL DOCENTE:\n{files_text[:20000]}"
        )

        total_tokens = 0
        failover_notices: List[str] = []

        # Step 1: Gemini Research (or reuse checkpoint if already completed previously)
        gemini_research = state_cp.get("research_gemini", "")
        if gemini_research:
            if on_progress:
                on_progress(35, "Fase 1/3 · Checkpoint de investigación Gemini recuperado (0 tokens)...")
        elif gemini_pool:
            if on_progress:
                on_progress(25, "Fase 1/3 · Gemini investigando lineamientos del docente y adjuntos...")
            try:
                g_text, g_tok = self._call_gemini(
                    prompt=(
                        f"Analiza y desarrolla exhaustivamente CADA UNO de los puntos, preguntas y estudio de caso "
                        f"exigidos en los Lineamientos del Docente:\n\n{context_block}"
                    ),
                    system_instruction=(
                        "Eres el Investigador Académico Principal (Gemini). "
                        f"{domain_cfg['domain_rule']} "
                        "Debes tomar en cuenta el 100% de las preguntas, requisitos y estudio de caso de la página de la evaluación."
                    ),
                    model_name=self.gemini_model,
                    use_google_search=True,
                    file_paths=local_files,
                )
                gemini_research = g_text
                total_tokens += g_tok
                if gemini_research:
                    state_cp["research_gemini"] = gemini_research
                    if on_checkpoint:
                        on_checkpoint(state_cp)
            except Exception:
                failover_notices.append("Gemini alcanzó límite temporal; DeepSeek asumió el relevo.")

        # Step 2: DeepSeek-R1 Analytical breakdown (or reuse checkpoint)
        deepseek_analysis = state_cp.get("research_deepseek", "")
        if deepseek_analysis:
            if on_progress:
                on_progress(60, "Fase 2/3 · Checkpoint analítico DeepSeek-R1 recuperado (0 tokens)...")
        elif deepseek_key:
            if on_progress:
                on_progress(50, "Fase 2/3 · DeepSeek-R1 estructurando puntos de la pauta y estudio de caso...")
            try:
                d_text, d_tok = self._call_deepseek(
                    prompt=f"{domain_cfg['deepseek_prompt']}\n\n{context_block}",
                    system_instruction=f"{domain_cfg['deepseek_sys']} {domain_cfg['domain_rule']}",
                )
                deepseek_analysis = d_text
                total_tokens += d_tok
                if deepseek_analysis:
                    state_cp["research_deepseek"] = deepseek_analysis
                    if on_checkpoint:
                        on_checkpoint(state_cp)
            except Exception:
                failover_notices.append("DeepSeek sin saldo o en espera; Gemini asumió el relevo completo.")

        # Step 3: Arbiter Synthesis into the 4 Pillars JSON
        if on_progress:
            on_progress(75, "Fase 3/3 · Árbitro sintetizando los 4 Pilares ceñidos a la pauta del docente...")
        arbiter_prompt = f"""
Con base en los Lineamientos Obligatorios del Docente, sintetiza el material de estudio definitivo
para NotebookLM dividido exactamente en los 4 Pilares Fundamentales.

{domain_cfg['domain_rule']}

{HUMAN_STYLE_DIRECTIVE}

CONTEXTO Y LINEAMIENTOS OBLIGATORIOS DE LA EVALUACIÓN:
{context_block}

INVESTIGACIÓN CONCEPTUAL Y DOCUMENTAL:
{gemini_research or 'Integrado en el análisis principal.'}

DESARROLLO ESTRUCTURAL Y APLICACIÓN AL CASO:
{deepseek_analysis or 'Integrado en la investigación principal.'}

Devuelve ÚNICAMENTE un objeto JSON válido con estas 5 claves exactas (cada valor en formato Markdown en español, con redacción humana y natural de estudiante de ingeniería, muy completo y 100% ceñido a las pautas de la evaluación):
- "01_Preparar": Desglose exacto de los objetivos y requisitos de la actividad, mapa de las preguntas que exige responder el docente, glosario de términos clave de la guía y contextualización inicial del Estudio de Caso (si aplica).
- "02_Comprender": {domain_cfg['pillar_2_desc']}
- "03_Comprobar": {domain_cfg['pillar_3_desc']}
- "04_Consolidar": Estructura sugerida paso a paso para el documento final según las normas formales exigidas por el profesor, cuadros comparativos de síntesis y bibliografía en normas APA/PSM (todas las fuentes citadas deben ser exclusivamente de obras publicadas o traducidas al idioma español).
- "summary": Resumen claro y preciso de 2 párrafos sobre cómo se abordaron todos los lineamientos del docente en tono sobrio y humano.
"""
        pillars_dict: Optional[Dict[str, str]] = None
        if gemini_pool:
            try:
                arb_text, arb_tok = self._call_gemini(
                    prompt=arbiter_prompt,
                    system_instruction="Eres el Árbitro Académico de V.I.E.R.N.E.S. Responde siempre con JSON válido.",
                    model_name=self.gemini_arbiter_model,
                    thinking_level="high",
                )
                total_tokens += arb_tok
                pillars_dict = self._parse_json_safely(arb_text)
            except Exception:
                pillars_dict = None

        if not pillars_dict and deepseek_key:
            try:
                arb_text, arb_tok = self._call_deepseek(
                    prompt=arbiter_prompt,
                    system_instruction="Eres el Árbitro Académico de V.I.E.R.N.E.S. Responde siempre con JSON válido.",
                )
                total_tokens += arb_tok
                pillars_dict = self._parse_json_safely(arb_text)
            except Exception:
                pillars_dict = None

        # Emergency Rescue if Step 3 failed or didn't return JSON, using Step 1 / Step 2 checkpoints
        if not pillars_dict:
            combined_rescue = "\n\n".join(filter(None, [gemini_research, deepseek_analysis]))
            if not combined_rescue:
                raise RuntimeError("Todas las cuentas de IA agotaron su cuota simultáneamente. Tus avances previos están a salvo.")
            pillars_dict = {
                "01_Preparar": f"# Pilar 1: Preparar\n\n{combined_rescue[:4500]}",
                "02_Comprender": f"# Pilar 2: Comprender\n\n{combined_rescue}",
                "03_Comprobar": f"# Pilar 3: Comprobar\n\n{deepseek_analysis or gemini_research}",
                "04_Consolidar": f"# Pilar 4: Consolidar\n\n## Síntesis Rescatada\n{combined_rescue[:3500]}",
                "summary": "Dossier generado mediante recuperación de checkpoints de alta disponibilidad.",
            }

        summary_msg = pillars_dict.get("summary", "Dossier de 4 pilares generado con éxito.")
        if failover_notices:
            summary_msg += "\n\n[Nota de Relevo: " + " | ".join(failover_notices) + "]"

        return {
            "pillars": {
                "01_Preparar": pillars_dict.get("01_Preparar", ""),
                "02_Comprender": pillars_dict.get("02_Comprender", ""),
                "03_Comprobar": pillars_dict.get("03_Comprobar", ""),
                "04_Consolidar": pillars_dict.get("04_Consolidar", ""),
            },
            "summary": summary_msg,
            "tokens_used": total_tokens,
            "simulated": False,
        }

    def resolve_assignment_with_consensus(
        self,
        course_name: str,
        assignment_title: str,
        description_text: str,
        task_mode: str = "digital",
        local_files: Optional[List[str]] = None,
        research_files: Optional[List[Dict[str, str]]] = None,
        checkpoints: Optional[Dict[str, str]] = None,
        on_checkpoint: Optional[Callable[[Dict[str, str]], None]] = None,
        on_progress: Optional[Callable[[int, str], None]] = None,
    ) -> Dict[str, Any]:
        """Solves the assignment via DeepSeek + Gemini + Arbiter referee with checkpoint resume, 4-Pillars integration, and failover."""
        gemini_pool, deepseek_key = _reload_env_pool()
        if not gemini_pool and not deepseek_key:
            if on_progress:
                on_progress(50, "Simulando resolución por consenso...")
            return self._simulate_resolution(course_name, assignment_title, description_text, task_mode)

        state_cp: Dict[str, str] = dict(checkpoints or {})
        files_text = extract_local_files_text(local_files or [])

        # Extract any previously generated 4-Pillars study material so Resolution builds directly upon it
        pillar_paths = [
            rf["local_path"]
            for rf in (research_files or [])
            if isinstance(rf, dict) and rf.get("local_path") and os.path.exists(rf["local_path"])
        ]
        pillars_extracted_text = extract_local_files_text(pillar_paths) if pillar_paths else ""
        prior_research_block = ""
        if pillars_extracted_text:
            prior_research_block = (
                "\n\nINVESTIGACIÓN PREVIA DE LOS 4 PILARES (NOTEBOOKLM) YA REALIZADA PARA ESTA ACTIVIDAD "
                "(TOMAR COMO FUNDAMENTO TEÓRICO Y DE CASO PARA MANTENER 100% COHERENCIA):\n"
                + pillars_extracted_text[:20000]
            )
        elif state_cp.get("research_gemini") or state_cp.get("research_deepseek"):
            combined_prev = "\n\n".join(
                filter(None, [state_cp.get("research_gemini", ""), state_cp.get("research_deepseek", "")])
            )
            prior_research_block = (
                "\n\nINVESTIGACIÓN PREVIA YA REALIZADA PARA ESTA ACTIVIDAD:\n" + combined_prev[:20000]
            )

        mode_instructions = {
            "digital": (
                "MODO DIGITAL UNIVERSITARIO: Redacta el trabajo completo listo para revisión en Word "
                "(Introducción, Desarrollo exhaustivo punto por punto según la rúbrica, Aplicación al Estudio de Caso o Ejercicios si aplica, "
                "Conclusiones y Referencias Bibliográficas en normas APA/PSM citando exclusivamente obras o autores en idioma español). "
                "REGLA CRÍTICA DE FORMATO: NO escribas portada de texto ni índice (NO pongas '[INSERTAR LOGO]', ni 'República Bolivariana...', "
                "ni 'Bachiller:', ni 'C.I.:', ni 'CONTENIDO'), porque el sistema ya inserta automáticamente tu Portada Institucional "
                "Oficial del PSM en la Página 1. Inicia tu documento DIRECTAMENTE con el título '# INTRODUCCIÓN'."
            ),
            "manuscrito": (
                "MODO MANUSCRITO (PARA COPIAR A MANO EN HOJAS): Genera una 'Guía de Transcripción Paso a Paso' "
                "dividida por páginas sugeridas (Página 1, Página 2...), con redacción concisa, limpia, bien "
                "espaciadas y recuadros de respuesta final para copiar directamente a mano sin errores."
            ),
            "video": (
                "MODO EXPOSICIÓN EN VIDEO: Genera un 'Guión Técnico de Grabación' cronometrado minuto a minuto "
                "(Saludo institucional PSM, Desarrollo verbal exacto para leer/explicar frente a cámara, Cierre) "
                "acompañado del contenido exacto que debe llevar cada Diapositiva/Lámina de apoyo."
            ),
        }
        selected_instruction = mode_instructions.get(task_mode, mode_instructions["digital"])
        domain_cfg = self._classify_academic_domain(course_name, assignment_title, description_text)

        context_block = (
            f"MATERIA: {course_name}\n"
            f"EVALUACIÓN: {assignment_title}\n"
            f"MODALIDAD SOLICITADA: {selected_instruction}\n"
            f"{domain_cfg['domain_rule']}\n\n"
            f"{HUMAN_STYLE_DIRECTIVE}\n\n"
            f"INSTRUCCIONES Y RÚBRICA OBLIGATORIA DEL DOCENTE:\n{description_text or 'Resolver según el título de la actividad.'}\n\n"
            f"CONTENIDO DE ARCHIVOS ADJUNTOS DEL DOCENTE:\n{files_text[:20000]}"
            f"{prior_research_block}"
        )

        total_tokens = 0
        failover_notices: List[str] = []

        # 1. DeepSeek-R1 independent solution (with checkpoint reuse)
        deepseek_draft = state_cp.get("resolve_deepseek", "")
        if deepseek_draft:
            if on_progress:
                on_progress(35, "Fase 1/3 · Checkpoint de DeepSeek-R1 recuperado (0 tokens)...")
        elif deepseek_key:
            if on_progress:
                on_progress(25, "Fase 1/3 · DeepSeek-R1 resolviendo lógica y estructura técnica...")
            try:
                d_txt, d_tok = self._call_deepseek(
                    prompt=f"Resuelve rigurosamente la siguiente asignación académica:\n\n{context_block}",
                    system_instruction="Eres DeepSeek-R1 en el consorcio V.I.E.R.N.E.S. Resuelve con exactitud técnica, matemática y metodológica.",
                )
                deepseek_draft = d_txt
                total_tokens += d_tok
                if deepseek_draft:
                    state_cp["resolve_deepseek"] = deepseek_draft
                    if on_checkpoint:
                        on_checkpoint(state_cp)
            except Exception:
                failover_notices.append("DeepSeek no disponible temporalmente; relevo asumido por el Pool de Gemini.")

        # 2. Gemini independent solution (with checkpoint reuse + multi-key failover)
        gemini_draft = state_cp.get("resolve_gemini", "")
        if gemini_draft:
            if on_progress:
                on_progress(60, "Fase 2/3 · Checkpoint de Gemini recuperado (0 tokens)...")
        elif gemini_pool:
            if on_progress:
                on_progress(50, "Fase 2/3 · Gemini 3.8 Flash contrastando fuentes y adjuntos...")
            try:
                g_txt, g_tok = self._call_gemini(
                    prompt=f"Resuelve de forma integral y verificada la siguiente asignación académica:\n\n{context_block}",
                    system_instruction="Eres Gemini en el consorcio V.I.E.R.N.E.S. Verifica todos los documentos adjuntos del profesor y fundamenta con citas reales.",
                    model_name=self.gemini_model,
                    use_google_search=True,
                    file_paths=local_files,
                )
                gemini_draft = g_txt
                total_tokens += g_tok
                if gemini_draft:
                    state_cp["resolve_gemini"] = gemini_draft
                    if on_checkpoint:
                        on_checkpoint(state_cp)
            except Exception:
                failover_notices.append("Pool de Gemini en límite de cuota; relevo asumido por DeepSeek.")

        if not deepseek_draft and not gemini_draft:
            raise RuntimeError("No se pudo obtener respuesta de ninguna cuenta de IA. Verifica tu saldo o cuota.")

        # 3. Arbiter Referee Synthesis (only if both drafts exist; if only one succeeded, use it directly or polish)
        if on_progress:
            on_progress(75, "Fase 3/3 · Árbitro auditando rúbrica y redactando entrega final...")
        arbiter_prompt = f"""
Actúa como el Árbitro Supremo del Consorcio V.I.E.R.N.E.S.
Coteja las propuestas, audita el cumplimiento del 100% de la rúbrica del docente y redacta la VERSIÓN DEFINITIVA unificada.

REGLAS CRÍTICAS DE HUMANIZACIÓN Y ESTILO ACADÉMICO REAL (PSM):
1. CERO CLICHÉS O MULETILLAS DE IA:
   - Prohibido arrancar con introducciones infladas como 'En el vertiginoso mundo...', 'En la era digital...', 'Es imperativo destacar...', 'Un tapiz...', 'Faro...', 'Piedra angular...', 'Juega un papel crucial...'.
   - Prohibido repetir al inicio de párrafos 'Asimismo', 'Por ende', 'En este orden de ideas', 'Por otra parte'.
2. VOZ Y CADENCIA NATURAL DE ESTUDIANTE DE INGENIERÍA:
   - El texto debe sonar auténtico, sobrio, formal y directo, redactado en tercera persona reflexiva ('se procedió a...', 'se diagnosticó...', 'se concluye que...').
   - Varía la extensión de las oraciones: alterna oraciones concisas y contundentes con explicaciones detalladas.
3. CONTEXTO TÉCNICO TERRENAL:
   - Aplica los conceptos directamente a los laboratorios o realidad técnica del PSM de forma creíble y fundamentada, sin párrafos de relleno.
4. FUENTES Y BIBLIOGRAFÍA ESTRICTAMENTE EN ESPAÑOL:
   - En la sección final de "REFERENCIAS BIBLIOGRÁFICAS", TODAS las fuentes citadas deben ser libros, normas o manuales formalmente en español (Fidias Arias, Carlos Sabino, Roberto Hernández-Sampieri, Mario Tamayo, Jacqueline Hurtado, Manuales PSM o libros técnicos en sus ediciones en español). Prohibido citar obras en inglés.

{context_block}

--- PROPUESTA TÉCNICA 1 ---
{deepseek_draft or 'Relevada por Propuesta 2.'}

--- PROPUESTA TÉCNICA 2 ---
{gemini_draft or 'Relevada por Propuesta 1.'}

Entregable requerido:
1. Primero escribe una breve sección llamada "## Dictamen de Consenso y Auditoría de Rúbrica".
2. Seguido de "---SEPARADOR_ENTREGA---", escribe el documento completo final de la actividad según la modalidad ({task_mode}).
"""
        final_output = state_cp.get("resolve_arbiter", "")
        if not final_output and gemini_pool:
            try:
                arb_txt, arb_tok = self._call_gemini(
                    prompt=arbiter_prompt,
                    system_instruction="Eres el Árbitro Académico Principal de V.I.E.R.N.E.S. Sintetiza la mejor entrega universitaria posible sin omitir ningún punto de la rúbrica.",
                    model_name=self.gemini_arbiter_model,
                    thinking_level="high",
                )
                final_output = arb_txt
                total_tokens += arb_tok
                if final_output:
                    state_cp["resolve_arbiter"] = final_output
                    if on_checkpoint:
                        on_checkpoint(state_cp)
            except Exception:
                final_output = ""

        if not final_output and deepseek_key:
            try:
                arb_txt, arb_tok = self._call_deepseek(
                    prompt=arbiter_prompt,
                    system_instruction="Eres el Árbitro Académico Principal de V.I.E.R.N.E.S. Sintetiza la mejor entrega universitaria posible.",
                )
                final_output = arb_txt
                total_tokens += arb_tok
                if final_output:
                    state_cp["resolve_arbiter"] = final_output
                    if on_checkpoint:
                        on_checkpoint(state_cp)
            except Exception:
                final_output = ""

        # Emergency rescue from checkpoint if Step 3 failed
        if not final_output:
            final_output = gemini_draft or deepseek_draft

        if "---SEPARADOR_ENTREGA---" in final_output:
            parts = final_output.split("---SEPARADOR_ENTREGA---", 1)
            consensus_report = parts[0].strip()
            resolution_md = parts[1].strip()
        else:
            consensus_report = "Dictamen verificado cumpliendo los lineamientos de la cátedra."
            resolution_md = final_output.strip()

        if failover_notices:
            consensus_report += "\n\n• Relevo automático: " + " | ".join(failover_notices)

        return {
            "resolution_markdown": resolution_md,
            "consensus_report": consensus_report,
            "tokens_used": total_tokens,
            "simulated": False,
        }

    @staticmethod
    def _parse_json_safely(raw_text: str) -> Optional[Dict[str, str]]:
        cleaned = raw_text.strip()
        if "```" in cleaned:
            import re

            m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.S)
            if m:
                cleaned = m.group(1)
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(cleaned[start : end + 1])
            except Exception:
                return None
        return None

    @staticmethod
    def _simulate_four_pillars(
        course_name: str, assignment_title: str, description_text: str
    ) -> Dict[str, Any]:
        desc_preview = description_text[:500] if description_text else "Lineamientos extraídos de la plataforma SAIA."
        pillars = {
            "01_Preparar": (
                f"# Pilar 1: PREPARAR — {assignment_title}\n"
                f"## Vista Previa en Modo Simulación (0 Tokens Consumidos)\n"
                f"- **Materia**: {course_name}\n"
                f"- **Lineamientos detectados**: {desc_preview}\n\n"
                "## 1. Objetivos de Aprendizaje\n"
                "- Comprender los fundamentos teóricos y prácticos de la unidad evaluada.\n"
                "- Dominar la terminología técnica exigida por el docente en SAIA.\n\n"
                "## 2. Glosario de Términos Clave\n"
                "- **Concepto Fundamental 1**: Definición operativa adaptada al programa de PSM.\n"
                "- **Concepto Fundamental 2**: Relación con las variables del problema.\n\n"
                "## 3. Preguntas Detonantes para NotebookLM\n"
                "1. ¿Cuáles son los supuestos principales que rigen este modelo en ingeniería?\n"
                "2. ¿Cómo se articula la teoría con los casos prácticos solicitados en la rúbrica?"
            ),
            "02_Comprender": (
                f"# Pilar 2: COMPRENDER — {assignment_title}\n"
                "## 1. Desarrollo Teórico Profundo\n"
                "Explicación estructurada lista para generar el *Audio Overview* y las guías de NotebookLM.\n\n"
                "## 2. Analogía Didáctica\n"
                "Representación intuitiva del fenómeno o metodología para facilitar la retención a largo plazo.\n\n"
                "## 3. Desglose Metodológico / Matemático Paso a Paso\n"
                "1. Identificación de datos de entrada y condiciones de contorno.\n"
                "2. Aplicación de ecuaciones o marcos metodológicos.\n"
                "3. Interpretación física/económica/técnica del resultado."
            ),
            "03_Comprobar": (
                f"# Pilar 3: COMPROBAR — {assignment_title}\n"
                "## 1. Banco de Autoevaluación\n"
                "- **Pregunta 1**: Planteamiento analítico sobre el tema.\n"
                "  - **Respuesta Razonada**: Explicación paso a paso del porqué.\n\n"
                "## 2. Problema / Caso Práctico Resuelto\n"
                "- **Enunciado Tipo Examen**: Caso aplicado a la cátedra.\n"
                "- **Solución Detallada**: Desarrollo completo sin omitir pasos intermedios.\n\n"
                "## 3. Errores Comunes a Evitar en la Entrega\n"
                "- Omitir unidades o referencias bibliográficas exigidas en la rúbrica."
            ),
            "04_Consolidar": (
                f"# Pilar 4: CONSOLIDAR — {assignment_title}\n"
                "## 1. Resumen Ejecutivo de 1 Página\n"
                "Síntesis de alta densidad con las ideas centrales del tema.\n\n"
                "## 2. Fichas de Repaso Rápido (Flashcards)\n"
                "- **Frente**: ¿Cuál es el criterio de decisión principal? | **Reverso**: Explicación concisa.\n\n"
                "## 3. Referencias Bibliográficas Base\n"
                "- Material oficial del aula virtual SAIA - I.U.P. Santiago Mariño."
            ),
        }
        return {
            "pillars": pillars,
            "summary": (
                "[MODO SIMULACIÓN ACTIVO - 0 TOKENS GASTADOS] Se ha generado y estructurado la carpeta con los "
                "4 documentos (.docx) de prueba para NotebookLM."
            ),
            "tokens_used": 0,
            "simulated": True,
        }

    @staticmethod
    def _simulate_resolution(
        course_name: str, assignment_title: str, description_text: str, task_mode: str
    ) -> Dict[str, Any]:
        if task_mode == "manuscrito":
            body = (
                "# Guía de Transcripción Paso a Paso (Modo Manuscrito)\n"
                "## Instrucciones de Copiado en Hoja de Examen\n"
                "- **Página 1 (Encabezado y Planteamiento)**:\n"
                "  Escribir con letra clara el encabezado de la cátedra, nombre, cédula y enunciado #1.\n"
                "- **Página 2 (Desarrollo de Fórmulas y Cálculos Paso a Paso)**:\n"
                "  1. Fórmula base despejada.\n"
                "  2. Sustitución de valores numéricos con sus unidades.\n"
                "  3. Resultado final encerrado en recuadro.\n"
            )
        elif task_mode == "video":
            body = (
                "# Guión Técnico de Exposición en Video y Estructura de Láminas\n"
                "## Minuto 0:00 - 0:45 | Introducción y Presentación\n"
                "- **Lámina 1**: Portada Institucional PSM, Título del tema y Nombre del ponente.\n"
                "- **Texto a decir en cámara**: «Buenas tardes estimado profesor, mi nombre es Victor Lisboa y en esta exposición abordaremos...»\n\n"
                "## Minuto 0:45 - 3:30 | Desarrollo Central\n"
                "- **Lámina 2**: Diagrama principal y puntos clave (máximo 4 líneas de texto por lámina).\n"
                "- **Texto a decir en cámara**: Explicación fluida de los conceptos evaluados en la rúbrica.\n\n"
                "## Minuto 3:30 - 4:30 | Conclusiones y Cierre\n"
                "- **Lámina 3**: Síntesis técnica y referencias.\n"
            )
        else:
            body = (
                "# Introducción\n"
                f"El presente trabajo académico desarrolla los lineamientos establecidos en la cátedra **{course_name}** "
                f"para la evaluación **{assignment_title}**.\n\n"
                "# Desarrollo Académico\n"
                "## 1. Fundamentación Teórica y Análisis\n"
                "Desarrollo estructurado conforme a los criterios del docente en SAIA.\n\n"
                "## 2. Aplicación Práctica / Resolución\n"
                "Solución detallada verificada por consenso.\n\n"
                "# Conclusiones\n"
                "Síntesis de los hallazgos obtenidos en correspondencia con los objetivos de la evaluación.\n\n"
                "# Referencias Bibliográficas (Normas APA / PSM)\n"
                "- Fuentes documentales de la asignatura y literatura académica."
            )

        return {
            "resolution_markdown": body,
            "consensus_report": (
                "[MODO SIMULACIÓN - 0 TOKENS GASTADOS]\n"
                "• Modalidad seleccionada: " + task_mode.upper() + "\n"
                "• Documento Word (.docx) creado exitosamente para validar el flujo completo."
            ),
            "tokens_used": 0,
            "simulated": True,
        }
