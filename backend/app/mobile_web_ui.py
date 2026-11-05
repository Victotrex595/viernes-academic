MOBILE_WEB_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <meta name="theme-color" content="#0d0d0f" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  <meta name="apple-mobile-web-app-title" content="V.I.E.R.N.E.S." />
  <meta name="application-name" content="V.I.E.R.N.E.S." />
  <link rel="manifest" href="/manifest.json" />
  <link rel="icon" type="image/svg+xml" href="/icon.svg" />
  <link rel="apple-touch-icon" href="/icon.svg" />
  <title>V.I.E.R.N.E.S.</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-base: #0d0d0f;
      --bg-surface: #141417;
      --bg-elevated: #1c1c21;
      --border-subtle: #26262c;
      --border-focus: #3f3f48;
      --text-primary: #f4f4f6;
      --text-secondary: #90909c;
      --text-muted: #5c5c66;
    }
    body {
      background-color: var(--bg-base);
      color: var(--text-primary);
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      -webkit-font-smoothing: antialiased;
    }
    .font-mono-tech {
      font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, monospace;
    }
    .ag-card {
      background-color: var(--bg-surface);
      border: 1px solid var(--border-subtle);
    }
    .ag-card-interactive {
      background-color: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      transition: border-color 0.15s ease, background-color 0.15s ease;
    }
    .ag-card-interactive:active, .ag-card-interactive:hover {
      background-color: var(--bg-elevated);
      border-color: var(--border-focus);
    }
    .ag-input {
      background-color: #101013;
      border: 1px solid var(--border-subtle);
      color: var(--text-primary);
    }
    .ag-input:focus {
      outline: none;
      border-color: #71717a;
    }
    .ag-btn-primary {
      background-color: #f4f4f6;
      color: #0d0d0f;
      font-weight: 600;
      transition: opacity 0.15s ease;
    }
    .ag-btn-primary:hover { opacity: 0.92; }
    .ag-btn-primary:disabled {
      background-color: #232329;
      color: #52525b;
      cursor: not-allowed;
    }
    .ag-btn-secondary {
      background-color: #1c1c21;
      border: 1px solid #2e2e36;
      color: #e4e4e7;
      font-weight: 500;
    }
    .ag-btn-secondary:hover {
      background-color: #25252c;
      border-color: #3f3f48;
    }
    .no-scrollbar::-webkit-scrollbar { display: none; }
    .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
  </style>
</head>
<body class="min-h-screen pb-12 selection:bg-zinc-700 selection:text-white">

  <!-- Top Header -->
  <header class="sticky top-0 z-30 bg-[#0d0d0f]/90 backdrop-blur-md border-b border-[#222228] px-4 py-3">
    <div class="max-w-xl mx-auto flex items-center justify-between">
      <div class="flex items-center gap-3">
        <button id="btn-back-home" onclick="navigate('home')" class="hidden p-1.5 -ml-1.5 rounded-lg border border-[#26262c] bg-[#141417] text-zinc-300 hover:text-white">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
        </button>
        <div onclick="openAcrosticModal()" class="flex items-center gap-2.5 cursor-pointer group" title="Ver especificación de V.I.E.R.N.E.S.">
          <img src="/icon.svg" alt="V.I.E.R.N.E.S." class="w-8 h-8 rounded-lg border border-[#2e2e36] group-hover:border-zinc-400 transition-colors shrink-0" />
          <div>
            <div class="flex items-center gap-2">
              <h1 class="text-sm font-bold tracking-widest text-zinc-100 group-hover:text-white" id="header-title">V.I.E.R.N.E.S.</h1>
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400" id="status-dot"></span>
            </div>
            <p id="ai-mode-badge" class="text-[11px] font-mono-tech text-zinc-500 mt-0.5">Inicializando entorno...</p>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <button id="btn-sync-header" onclick="syncSaia()" class="hidden ag-btn-secondary text-xs px-2.5 py-1.5 rounded-lg flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          <span>Sincronizar</span>
        </button>
        <button onclick="navigate('settings')" class="p-2 rounded-lg border border-[#26262c] bg-[#141417] text-zinc-400 hover:text-zinc-100" title="Configuración">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
        </button>
      </div>
    </div>
  </header>

  <main class="max-w-xl mx-auto px-4 pt-5">

    <!-- ==================== VIEW: HOME (2 MAIN BUTTONS + ARCHIVE) ==================== -->
    <section id="view-home" class="space-y-6">
      <div>
        <h2 class="text-xs font-mono-tech uppercase tracking-wider text-zinc-500 mb-3">Espacios de Trabajo</h2>
        <div class="grid grid-cols-1 gap-3.5">

          <!-- Main Button 1: Tareas del PSM -->
          <button onclick="navigate('psm')" class="ag-card-interactive rounded-xl p-5 text-left flex items-center justify-between group">
            <div class="space-y-1.5 pr-4">
              <div class="flex items-center gap-2">
                <svg class="w-4 h-4 text-zinc-300" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
                <span class="text-base font-semibold text-zinc-100">Asignaciones PSM (SAIA)</span>
              </div>
              <p class="text-xs text-zinc-400 leading-relaxed">
                Gestiona tus materias inscritas, revisa los lineamientos del docente, genera los 4 pilares para NotebookLM o resuelve actividades por consenso.
              </p>
              <div class="pt-1 flex items-center gap-3 text-[11px] font-mono-tech text-zinc-500" id="home-psm-stats">
                <span>Cargando materias...</span>
              </div>
            </div>
            <div class="p-2.5 rounded-lg bg-[#1c1c21] border border-[#2e2e36] text-zinc-300 group-hover:text-white shrink-0">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
            </div>
          </button>

          <!-- Main Button 2: Tema Libre / Fuera de PSM -->
          <button onclick="navigate('external')" class="ag-card-interactive rounded-xl p-5 text-left flex items-center justify-between group">
            <div class="space-y-1.5 pr-4">
              <div class="flex items-center gap-2">
                <svg class="w-4 h-4 text-zinc-300" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
                <span class="text-base font-semibold text-zinc-100">Tema Libre y Evaluación Externa</span>
              </div>
              <p class="text-xs text-zinc-400 leading-relaxed">
                Investiga cualquier tema ajeno a la universidad bajo la estructura de los 4 pilares o adjunta enunciados externos para su resolución.
              </p>
              <div class="pt-1 flex items-center gap-3 text-[11px] font-mono-tech text-zinc-500" id="home-ext-stats">
                <span>Proyectos independientes</span>
              </div>
            </div>
            <div class="p-2.5 rounded-lg bg-[#1c1c21] border border-[#2e2e36] text-zinc-300 group-hover:text-white shrink-0">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
            </div>
          </button>

        </div>
      </div>

      <!-- Biblioteca de Documentos ya creados por el Consorcio y Lineamientos agrupada por Materia -->
      <div>
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-xs font-mono-tech uppercase tracking-wider text-zinc-500">Documentación por Materia</h2>
          <span class="text-[11px] font-mono-tech text-zinc-600" id="repo-count">0 materias</span>
        </div>
        <div id="home-repository-list" class="space-y-2.5"></div>
      </div>
    </section>

    <!-- ==================== VIEW: PSM ASSIGNMENTS ==================== -->
    <section id="view-psm" class="hidden space-y-4">
      <div class="flex items-center gap-2 overflow-x-auto no-scrollbar pb-1" id="course-chips"></div>
      <div id="assignments-list" class="space-y-3.5"></div>
    </section>

    <!-- ==================== VIEW: EXTERNAL FREE TOPICS ==================== -->
    <section id="view-external" class="hidden space-y-5">
      <div class="ag-card rounded-xl p-4 space-y-3.5">
        <div class="border-b border-[#222228] pb-2.5">
          <h2 class="text-sm font-semibold text-zinc-100">Nueva Investigación o Evaluación Externa</h2>
          <p class="text-xs text-zinc-400 mt-0.5">Define el tema o pega las pautas de evaluación. Puedes adjuntar documentos de soporte o imágenes.</p>
        </div>

        <div class="space-y-3">
          <div>
            <label class="block text-[11px] font-mono-tech text-zinc-400 mb-1">TÍTULO DEL TEMA O EVALUACIÓN *</label>
            <input id="ext-title" type="text" placeholder="Ej. Sistemas Distribuidos / Certificación Cloud" class="w-full ag-input rounded-lg px-3 py-2 text-sm" />
          </div>

          <div>
            <label class="block text-[11px] font-mono-tech text-zinc-400 mb-1">CARPETA DE DESTINO</label>
            <input id="ext-cat" type="text" value="Proyectos Libres" class="w-full ag-input rounded-lg px-3 py-2 text-sm" />
          </div>

          <div>
            <label class="block text-[11px] font-mono-tech text-zinc-400 mb-1">LINEAMIENTOS O PUNTOS A ABORDAR</label>
            <textarea id="ext-desc" rows="3" placeholder="Especifica los lineamientos, preguntas o enfoque técnico..." class="w-full ag-input rounded-lg px-3 py-2 text-sm"></textarea>
          </div>

          <div>
            <label class="block text-[11px] font-mono-tech text-zinc-400 mb-1">FORMATO DE SALIDA</label>
            <div class="grid grid-cols-3 gap-2 text-xs">
              <button type="button" onclick="setExtMode('digital')" id="ext-mode-digital" class="py-2 rounded-lg border border-zinc-300 bg-zinc-100 text-zinc-950 font-semibold">Digital</button>
              <button type="button" onclick="setExtMode('manuscrito')" id="ext-mode-manuscrito" class="py-2 rounded-lg border border-[#26262c] bg-[#101013] text-zinc-400">Manuscrito</button>
              <button type="button" onclick="setExtMode('video')" id="ext-mode-video" class="py-2 rounded-lg border border-[#26262c] bg-[#101013] text-zinc-400">Exposición</button>
            </div>
          </div>

          <div>
            <label class="block text-[11px] font-mono-tech text-zinc-400 mb-1">MATERIAL DE APOYO ADJUNTO (PDF, DOCX, IMÁGENES)</label>
            <input id="ext-files" type="file" multiple class="block w-full text-xs text-zinc-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border file:border-[#2e2e36] file:text-xs file:font-medium file:bg-[#1c1c21] file:text-zinc-200" />
          </div>

          <div class="grid grid-cols-2 gap-2.5 pt-2">
            <button onclick="createExternal(false)" class="ag-btn-secondary text-xs py-2.5 rounded-lg">Registrar Tema</button>
            <button onclick="createExternal(true)" class="ag-btn-primary text-xs py-2.5 rounded-lg">Generar 4 Pilares</button>
          </div>
        </div>
      </div>

      <div>
        <h3 class="text-xs font-mono-tech uppercase tracking-wider text-zinc-500 mb-2.5">Temas Libres Registrados</h3>
        <div id="external-list" class="space-y-3.5"></div>
      </div>
    </section>

    <!-- ==================== VIEW: SETTINGS ==================== -->
    <section id="view-settings" class="hidden space-y-4">
      <div class="ag-card rounded-xl p-4 space-y-3">
        <h2 class="text-sm font-semibold text-zinc-100">Sesión SAIA PSM (MoodleSession)</h2>
        <p class="text-xs text-zinc-400">Actualiza el identificador de sesión cuando caduque en la plataforma SAIA.</p>
        <input id="cookie-input" type="text" placeholder="Pegar valor de cookie MoodleSession..." class="w-full ag-input rounded-lg px-3 py-2 text-sm font-mono-tech" />
        <button onclick="saveCookie()" class="w-full ag-btn-primary text-xs py-2.5 rounded-lg">Verificar y Guardar Sesión</button>
      </div>

      <div class="ag-card rounded-xl p-4 space-y-3 text-xs">
        <div class="flex items-center justify-between">
          <h2 class="text-sm font-semibold text-zinc-100">Pool Multi-Cuenta de Google Gemini</h2>
          <span id="gemini-pool-badge" class="text-[11px] font-mono-tech text-zinc-400">Cargando...</span>
        </div>
        <p class="text-xs text-zinc-400">Agrega claves adicionales de otras cuentas de Google AI Studio. V.I.E.R.N.E.S. las rotará automáticamente (Round-Robin) y cambiará al instante si una cuenta alcanza el límite de cuota (Error 429).</p>
        <input id="extra-gemini-key-input" type="password" autocomplete="off" placeholder="Pegar API Key adicional de Google Gemini..." class="w-full ag-input rounded-lg px-3 py-2 text-xs font-mono-tech" />
        <button onclick="addExtraGeminiKey()" class="w-full ag-btn-primary text-xs py-2.5 rounded-lg">Añadir Cuenta al Pool de Rotación</button>
      </div>

      <div class="ag-card rounded-xl p-4 space-y-3 text-xs">
        <h2 class="text-sm font-semibold text-zinc-100">Conexión Directa con Google Drive (NotebookLM)</h2>
        <p class="text-xs text-zinc-400">Pega aquí la URL de tu aplicación web de Google Apps Script para crear automáticamente las carpetas por materia y los Google Docs en tu nube personal.</p>
        <input id="drive-bridge-input" type="text" placeholder="https://script.google.com/macros/s/.../exec" class="w-full ag-input rounded-lg px-3 py-2 text-xs font-mono-tech" />
        <button onclick="saveDriveBridge()" class="w-full ag-btn-primary text-xs py-2.5 rounded-lg">Vincular y Verificar Carpeta en Google Drive</button>
      </div>

      <div class="ag-card rounded-xl p-4 space-y-3 text-xs">
        <h2 class="text-sm font-semibold text-zinc-100">Estado del Consorcio y Almacenamiento</h2>
        <div id="health-details" class="space-y-2 text-zinc-400 font-mono-tech text-[11px]"></div>
      </div>
    </section>

  </main>

  <!-- ==================== MODAL: DOCUMENT & GUIDELINES INSPECTOR ==================== -->
  <div id="inspector-modal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm hidden flex flex-col">
    <div class="bg-[#0d0d0f] border-b border-[#26262c] px-4 py-3 flex items-center justify-between">
      <div class="pr-3">
        <span class="text-[10px] font-mono-tech uppercase tracking-wider text-zinc-500" id="insp-course">MATERIA</span>
        <h3 class="text-sm font-semibold text-zinc-100 line-clamp-1" id="insp-title">Inspección de Documentos</h3>
      </div>
      <button onclick="closeInspector()" class="p-1.5 rounded-lg border border-[#26262c] bg-[#141417] text-zinc-400 hover:text-white">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
      </button>
    </div>

    <!-- Modal Tabs -->
    <div class="bg-[#141417] border-b border-[#26262c] px-4 flex gap-4">
      <button onclick="switchInspectorTab('teacher')" id="insp-tab-teacher" class="py-2.5 text-xs font-semibold border-b-2 border-zinc-100 text-zinc-100">
        Lineamientos y Archivos del Docente
      </button>
      <button onclick="switchInspectorTab('ai')" id="insp-tab-ai" class="py-2.5 text-xs font-medium border-b-2 border-transparent text-zinc-500">
        Documentos del Consorcio IA
      </button>
    </div>

    <!-- Modal Body -->
    <div class="flex-1 overflow-y-auto p-4 max-w-2xl w-full mx-auto space-y-4">
      <!-- Teacher Tab Content -->
      <div id="insp-body-teacher" class="space-y-4">
        <div class="flex items-center justify-between">
          <span class="text-xs font-mono-tech text-zinc-400">PAUTAS EXTRAÍDAS DEL AULA VIRTUAL</span>
          <button id="btn-refresh-saia-doc" class="ag-btn-secondary text-[11px] px-2.5 py-1 rounded-md">Extraer en vivo de SAIA</button>
        </div>
        <div id="insp-guidelines-text" class="ag-card rounded-xl p-4 text-xs text-zinc-200 whitespace-pre-line leading-relaxed"></div>

        <div>
          <h4 class="text-xs font-mono-tech text-zinc-400 mb-2">ARCHIVOS ADJUNTOS DEL PROFESOR</h4>
          <div id="insp-teacher-files" class="space-y-2"></div>
        </div>

        <div id="insp-teacher-extracted-box" class="hidden">
          <h4 class="text-xs font-mono-tech text-zinc-400 mb-2">CONTENIDO EXTRAÍDO DE LOS ADJUNTOS DEL DOCENTE</h4>
          <div id="insp-teacher-extracted-text" class="ag-card rounded-xl p-4 text-xs text-zinc-300 font-mono-tech whitespace-pre-line max-h-96 overflow-y-auto"></div>
        </div>
      </div>

      <!-- AI Documents Tab Content -->
      <div id="insp-body-ai" class="hidden space-y-4">
        <div id="insp-ai-docs-list" class="space-y-3"></div>
      </div>
    </div>
  </div>

  <!-- ==================== MODAL: V.I.E.R.N.E.S. ACROSTIC ==================== -->
  <div id="acrostic-modal" onclick="if(event.target===this) closeAcrosticModal()" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="bg-[#0d0d0f] border border-[#2e2e36] rounded-2xl max-w-md w-full overflow-hidden shadow-2xl">
      <div class="bg-[#141417] border-b border-[#26262c] px-5 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <img src="/icon.svg" alt="Logo" class="w-9 h-9 rounded-lg border border-[#2e2e36]" />
          <div>
            <h3 class="text-sm font-bold tracking-widest text-zinc-100">V.I.E.R.N.E.S.</h3>
            <p class="text-[10px] font-mono-tech text-zinc-400 uppercase">Arquitectura de Consorcio Académico</p>
          </div>
        </div>
        <button onclick="closeAcrosticModal()" class="p-1.5 rounded-lg border border-[#26262c] bg-[#0d0d0f] text-zinc-400 hover:text-white">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <div class="p-5 space-y-2.5 text-xs">
        <div class="flex items-start gap-3 p-2.5 rounded-lg bg-[#141417] border border-[#222228]">
          <span class="font-mono-tech font-bold text-sm text-zinc-100 w-5 shrink-0">V</span>
          <div><b class="text-zinc-100">Verificación</b> <span class="text-zinc-400">— Extracción y contraste de pautas, rúbricas y adjuntos desde SAIA PSM.</span></div>
        </div>
        <div class="flex items-start gap-3 p-2.5 rounded-lg bg-[#141417] border border-[#222228]">
          <span class="font-mono-tech font-bold text-sm text-zinc-100 w-5 shrink-0">I</span>
          <div><b class="text-zinc-100">Investigación</b> <span class="text-zinc-400">— Recopilación multimodal y búsqueda académica bajo los 4 Pilares para NotebookLM.</span></div>
        </div>
        <div class="flex items-start gap-3 p-2.5 rounded-lg bg-[#141417] border border-[#222228]">
          <span class="font-mono-tech font-bold text-sm text-zinc-100 w-5 shrink-0">E</span>
          <div><b class="text-zinc-100">Estructuración</b> <span class="text-zinc-400">— Organización jerárquica automatizada por materia y actividad en Google Drive.</span></div>
        </div>
        <div class="flex items-start gap-3 p-2.5 rounded-lg bg-[#141417] border border-[#222228]">
          <span class="font-mono-tech font-bold text-sm text-zinc-100 w-5 shrink-0">R</span>
          <div><b class="text-zinc-100">Razonamiento</b> <span class="text-zinc-400">— Resolución lógico-matemática y analítica combinando DeepSeek-R1 y Gemini.</span></div>
        </div>
        <div class="flex items-start gap-3 p-2.5 rounded-lg bg-[#141417] border border-[#222228]">
          <span class="font-mono-tech font-bold text-sm text-zinc-100 w-5 shrink-0">N</span>
          <div><b class="text-zinc-100">Neutralidad</b> <span class="text-zinc-400">— Arbitraje cruzado para eliminar contradicciones y auditar el 100% de la rúbrica.</span></div>
        </div>
        <div class="flex items-start gap-3 p-2.5 rounded-lg bg-[#141417] border border-[#222228]">
          <span class="font-mono-tech font-bold text-sm text-zinc-100 w-5 shrink-0">E</span>
          <div><b class="text-zinc-100">Evaluación</b> <span class="text-zinc-400">— Asistencia adaptada a entregas digitales, guías manuscritas o guiones de video.</span></div>
        </div>
        <div class="flex items-start gap-3 p-2.5 rounded-lg bg-[#141417] border border-[#222228]">
          <span class="font-mono-tech font-bold text-sm text-zinc-100 w-5 shrink-0">S</span>
          <div><b class="text-zinc-100">Síntesis</b> <span class="text-zinc-400">— Consolidación de conocimiento en los 4 pilares: Preparar, Comprender, Comprobar y Consolidar.</span></div>
        </div>
      </div>
    </div>
  </div>

  <!-- ==================== MODAL: LIVE PROGRESS TRACKER ==================== -->
  <div id="progress-modal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="bg-[#0d0d0f] border border-[#2e2e36] rounded-2xl max-w-md w-full p-5 space-y-4 shadow-2xl">
      <div class="flex items-center justify-between border-b border-[#222228] pb-3">
        <div class="flex items-center gap-2.5">
          <span id="prog-dot" class="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
          <span id="prog-header-title" class="text-xs font-mono-tech uppercase tracking-wider text-zinc-200">CONSORCIO V.I.E.R.N.E.S. EN EJECUCIÓN</span>
        </div>
        <span id="prog-timer" class="text-xs font-mono-tech text-zinc-400">00:00s</span>
      </div>

      <div class="space-y-2">
        <div class="flex items-center justify-between text-xs">
          <span id="prog-stage-text" class="text-zinc-200 font-medium pr-2">Inicializando motores...</span>
          <span id="prog-percent-text" class="font-mono-tech font-bold text-zinc-100 shrink-0">0%</span>
        </div>

        <div class="w-full h-2.5 bg-[#18181c] border border-[#26262c] rounded-full overflow-hidden">
          <div id="prog-bar-fill" class="h-full bg-zinc-100 transition-all duration-500 ease-out" style="width: 5%"></div>
        </div>
      </div>

      <!-- 5-Step Pipeline Indicator -->
      <div class="grid grid-cols-5 gap-1.5 pt-1 text-[10px] font-mono-tech text-center">
        <div id="prog-step-1" class="py-1.5 px-1 rounded border border-[#26262c] bg-[#141417] text-zinc-500">1. SAIA</div>
        <div id="prog-step-2" class="py-1.5 px-1 rounded border border-[#26262c] bg-[#141417] text-zinc-500">2. IA 1</div>
        <div id="prog-step-3" class="py-1.5 px-1 rounded border border-[#26262c] bg-[#141417] text-zinc-500">3. IA 2</div>
        <div id="prog-step-4" class="py-1.5 px-1 rounded border border-[#26262c] bg-[#141417] text-zinc-500">4. Árbitro</div>
        <div id="prog-step-5" class="py-1.5 px-1 rounded border border-[#26262c] bg-[#141417] text-zinc-500">5. Drive</div>
      </div>

      <!-- Actions when finished -->
      <div id="prog-actions" class="hidden pt-2 grid grid-cols-2 gap-2.5">
        <button onclick="closeProgressModal()" class="ag-btn-secondary text-xs py-2.5 rounded-lg">Cerrar</button>
        <button id="prog-open-docs-btn" class="ag-btn-primary text-xs py-2.5 rounded-lg">Abrir Documentos</button>
      </div>
    </div>
  </div>

  <!-- Toast -->
  <div id="toast" class="fixed bottom-5 left-4 right-4 max-w-md mx-auto bg-[#18181c] border border-[#3f3f46] text-zinc-100 text-xs px-4 py-3 rounded-xl shadow-2xl hidden z-50 font-medium"></div>

  <script>
    let stateCourses = [];
    let currentView = 'home';
    let selectedCourseId = null;
    let onlyPending = false;
    let extMode = 'digital';

    function openAcrosticModal() {
      document.getElementById('acrostic-modal').classList.remove('hidden');
    }

    function closeAcrosticModal() {
      document.getElementById('acrostic-modal').classList.add('hidden');
    }

    function showToast(msg) {
      const t = document.getElementById('toast');
      t.textContent = msg;
      t.classList.remove('hidden');
      setTimeout(() => t.classList.add('hidden'), 4000);
    }

    function navigate(view) {
      currentView = view;
      ['home', 'psm', 'external', 'settings'].forEach(v => {
        document.getElementById('view-' + v).classList.toggle('hidden', v !== view);
      });
      document.getElementById('btn-back-home').classList.toggle('hidden', view === 'home');
      document.getElementById('btn-sync-header').classList.toggle('hidden', view !== 'psm');

      const titles = {
        home: 'V.I.E.R.N.E.S.',
        psm: 'V.I.E.R.N.E.S. · SAIA PSM',
        external: 'V.I.E.R.N.E.S. · TEMA LIBRE',
        settings: 'V.I.E.R.N.E.S. · SISTEMA'
      };
      document.getElementById('header-title').textContent = titles[view] || 'V.I.E.R.N.E.S.';
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function setExtMode(m) {
      extMode = m;
      ['digital', 'manuscrito', 'video'].forEach(k => {
        const btn = document.getElementById('ext-mode-' + k);
        btn.className = k === m
          ? 'py-2 rounded-lg border border-zinc-300 bg-zinc-100 text-zinc-950 font-semibold'
          : 'py-2 rounded-lg border border-[#26262c] bg-[#101013] text-zinc-400';
      });
    }

    async function loadAll() {
      const [hRes, cRes] = await Promise.all([fetch('/api/health'), fetch('/api/courses')]);
      const health = await hRes.json();
      const cData = await cRes.json();
      stateCourses = cData.courses || [];

      document.getElementById('ai-mode-badge').textContent =
        `${health.ai_keys.mode} · ${health.total_tokens_used} tokens`;

      const poolCount = health.ai_keys.gemini_keys_count || 0;
      const poolBadge = document.getElementById('gemini-pool-badge');
      if (poolBadge) {
        poolBadge.textContent = `${poolCount} clave(s) activa(s)`;
      }

      document.getElementById('health-details').innerHTML = `
        <div class="flex justify-between py-1 border-b border-[#222228]"><span>MOTOR GEMINI (${health.models.gemini_model})</span><span class="text-zinc-200">${health.ai_keys.gemini_configured ? 'CONECTADO (' + poolCount + ' KEYS)' : 'SIMULACIÓN'}</span></div>
        <div class="flex justify-between py-1 border-b border-[#222228]"><span>ÁRBITRO (${health.models.gemini_arbiter_model})</span><span class="text-zinc-200">${health.ai_keys.gemini_configured ? 'CONECTADO (' + poolCount + ' KEYS)' : 'SIMULACIÓN'}</span></div>
        <div class="flex justify-between py-1 border-b border-[#222228]"><span>MOTOR DEEPSEEK (${health.models.deepseek_model})</span><span class="text-zinc-200">${health.ai_keys.deepseek_configured ? 'CONECTADO' : 'SIMULACIÓN'}</span></div>
        <div class="flex justify-between py-1 border-b border-[#222228]"><span>GOOGLE DRIVE</span><span class="text-zinc-200">${health.drive.connected ? 'VINCULADO' : 'ESPEJO LOCAL'}</span></div>
        <div class="pt-1 text-zinc-500 break-all">Ruta local: ${health.drive.local_mirror_path}</div>
      `;

      renderHomeStatsAndRepo();
      renderChips();
      renderAssignments();
    }

    let expandedRepoCourses = {};

    function toggleRepoCourse(cid) {
      expandedRepoCourses[cid] = !expandedRepoCourses[cid];
      renderHomeStatsAndRepo();
    }

    function renderHomeStatsAndRepo() {
      const psmCourses = stateCourses.filter(c => !c.is_external);
      const psmActs = psmCourses.flatMap(c => (c.assignments || []).filter(a => !a.is_overdue));
      const pendingCount = psmActs.filter(a => !a.is_completed).length;

      document.getElementById('home-psm-stats').innerHTML = `
        <span>${psmCourses.length} materias inscritas</span>
        <span>·</span>
        <span class="text-zinc-300">${pendingCount} entregas activas</span>
      `;

      const extActs = stateCourses
        .filter(c => c.is_external)
        .flatMap(c => (c.assignments || []).filter(a => !a.is_overdue));
      document.getElementById('home-ext-stats').innerHTML = `
        <span>${extActs.length} temas registrados</span>
      `;

      const visibleCourses = stateCourses.filter(c => !c.is_external || (c.assignments && c.assignments.length > 0));
      document.getElementById('repo-count').textContent = `${visibleCourses.length} materias`;

      const listContainer = document.getElementById('home-repository-list');
      if (visibleCourses.length === 0) {
        listContainer.innerHTML = `<div class="ag-card rounded-xl p-4 text-xs text-zinc-500 text-center">No hay materias registradas.</div>`;
        return;
      }

      listContainer.innerHTML = visibleCourses.map(course => {
        const acts = (course.assignments || []).filter(a => !a.is_overdue);
        const isExpanded = Boolean(expandedRepoCourses[course.id]);
        const docsTotal = acts.reduce((acc, a) => acc + (a.research_files ? a.research_files.length : 0) + (a.resolution_local_path ? 1 : 0), 0);

        const actsInsideHtml = acts.length === 0
          ? `<div class="px-4 py-3 text-xs text-zinc-500 font-mono-tech border-t border-[#222228]">Sin actividades activas en esta materia.</div>`
          : acts.map(a => {
              const pillarCount = (a.research_files || []).length;
              const hasRes = Boolean(a.resolution_local_path);
              return `
                <div onclick="openInspector('${a.id}')" class="px-4 py-3 border-t border-[#222228] hover:bg-[#1c1c21] cursor-pointer flex items-center justify-between gap-3 transition-colors">
                  <div class="min-w-0">
                    <div class="text-xs font-medium text-zinc-200 truncate">${a.title}</div>
                    <div class="flex items-center gap-2 mt-1 text-[10px] font-mono-tech">
                      <span class="${pillarCount > 0 ? 'text-zinc-200 bg-zinc-800 px-1.5 py-0.5 rounded' : 'text-zinc-500'}">
                        ${pillarCount > 0 ? pillarCount + ' Pilares' : 'Sin pilares'}
                      </span>
                      <span class="${hasRes ? 'text-zinc-200 bg-zinc-800 px-1.5 py-0.5 rounded' : 'text-zinc-500'}">
                        ${hasRes ? 'Resolución lista' : 'Sin resolución'}
                      </span>
                    </div>
                  </div>
                  <div class="text-[11px] font-mono-tech text-zinc-400 shrink-0 flex items-center gap-1">
                    <span>Abrir</span>
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                  </div>
                </div>
              `;
            }).join('');

        return `
          <div class="ag-card rounded-xl overflow-hidden">
            <button onclick="toggleRepoCourse('${course.id}')" class="w-full p-4 text-left flex items-center justify-between gap-3 hover:bg-[#19191e] transition-colors">
              <div class="min-w-0">
                <div class="text-xs font-semibold text-zinc-100 truncate">${course.name}</div>
                <div class="text-[11px] font-mono-tech text-zinc-500 mt-0.5">
                  ${acts.length} actividad(es) activa(s) · ${docsTotal} documento(s) IA
                </div>
              </div>
              <svg class="w-4 h-4 text-zinc-400 shrink-0 transition-transform ${isExpanded ? 'rotate-180' : ''}" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>
            <div class="${isExpanded ? 'block bg-[#101013]' : 'hidden'}">
              ${actsInsideHtml}
            </div>
          </div>
        `;
      }).join('');
    }

    function renderChips() {
      const psm = stateCourses.filter(c => !c.is_external);
      let html = `
        <button onclick="onlyPending=!onlyPending;renderChips();renderAssignments();" class="shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium border ${onlyPending ? 'bg-zinc-100 border-zinc-100 text-zinc-950' : 'bg-[#141417] border-[#26262c] text-zinc-400'}">Pendientes</button>
        <button onclick="selectedCourseId=null;renderChips();renderAssignments();" class="shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium border ${selectedCourseId===null ? 'bg-zinc-100 border-zinc-100 text-zinc-950' : 'bg-[#141417] border-[#26262c] text-zinc-400'}">Todas (${psm.length})</button>
      `;
      psm.forEach(c => {
        const active = selectedCourseId === c.id;
        html += `<button onclick="selectedCourseId='${c.id}';renderChips();renderAssignments();" class="shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium border ${active ? 'bg-zinc-100 border-zinc-100 text-zinc-950' : 'bg-[#141417] border-[#26262c] text-zinc-400'}">${c.name.slice(0, 24)}</button>`;
      });
      document.getElementById('course-chips').innerHTML = html;
    }

    function renderCardHtml(a) {
      const statusDot = a.is_completed ? 'bg-emerald-400' : 'bg-amber-400';
      const statusLabel = a.is_completed ? 'ENTREGADA' : 'PENDIENTE';

      const filesHtml = (a.research_files || []).map(f => {
        const dl = `/api/files/download?path=${encodeURIComponent(f.local_path)}`;
        return `<a href="${f.url || dl}" target="_blank" class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-[#101013] border border-[#26262c] hover:border-zinc-500 text-zinc-200 text-[11px] font-mono-tech">${f.name}</a>`;
      }).join(' ');

      const resLink = a.resolution_local_path
        ? `<a href="${a.resolution_drive_url && !a.resolution_drive_url.startsWith('local://') ? a.resolution_drive_url : '/api/files/download?path=' + encodeURIComponent(a.resolution_local_path)}" target="_blank" class="block w-full text-center mt-2 py-2 rounded-lg ag-btn-primary text-xs">Descargar Documento Editable (.docx)</a>`
        : '';

      return `
        <div class="ag-card rounded-xl p-4 space-y-3.5">
          <div class="flex items-center justify-between gap-2">
            <span class="text-[11px] font-mono-tech text-zinc-400 truncate">${a.course_name || ''}</span>
            <div class="flex items-center gap-1.5 shrink-0">
              <span class="w-1.5 h-1.5 rounded-full ${statusDot}"></span>
              <span class="text-[10px] font-mono-tech text-zinc-400">${statusLabel}</span>
            </div>
          </div>

          <h3 class="text-sm font-semibold text-zinc-100 leading-snug">${a.title}</h3>

          <div class="text-[11px] font-mono-tech text-zinc-500 flex flex-wrap gap-3">
            <span>Fecha: ${a.due_date || 'No especificada'}</span>
            <span>·</span>
            <span>Estado: ${a.time_remaining || '-'}</span>
          </div>

          <!-- Button to inspect teacher guidelines & previously generated AI documents -->
          <button onclick="openInspector('${a.id}')" class="w-full ag-btn-secondary py-2 px-3 rounded-lg text-xs flex items-center justify-between">
            <span>Ver Lineamientos del Docente y Documentos Creados</span>
            <span class="font-mono-tech text-[10px] text-zinc-400">${(a.research_files || []).length + (a.resolution_local_path ? 1 : 0)} docs →</span>
          </button>

          <!-- Mode Selector -->
          <div class="grid grid-cols-3 gap-1.5 text-xs">
            <button onclick="updateControls('${a.id}', null, 'digital')" class="py-1.5 rounded-lg border ${a.task_mode==='digital' ? 'border-zinc-300 bg-zinc-100 text-zinc-950 font-semibold' : 'border-[#26262c] bg-[#101013] text-zinc-400'}">Digital</button>
            <button onclick="updateControls('${a.id}', null, 'manuscrito')" class="py-1.5 rounded-lg border ${a.task_mode==='manuscrito' ? 'border-zinc-300 bg-zinc-100 text-zinc-950 font-semibold' : 'border-[#26262c] bg-[#101013] text-zinc-400'}">Manuscrito</button>
            <button onclick="updateControls('${a.id}', null, 'video')" class="py-1.5 rounded-lg border ${a.task_mode==='video' ? 'border-zinc-300 bg-zinc-100 text-zinc-950 font-semibold' : 'border-[#26262c] bg-[#101013] text-zinc-400'}">Exposición</button>
          </div>

          <!-- Token Switch -->
          <label class="flex items-center justify-between bg-[#101013] px-3 py-2.5 rounded-lg border border-[#26262c] cursor-pointer">
            <div>
              <div class="text-xs font-medium text-zinc-200">Autorizar Resolución con Consorcio IA</div>
              <div class="text-[11px] text-zinc-500">${a.allow_token_spend ? 'Habilitado para consumir tokens de resolución' : 'Bloqueado para evitar gasto innecesario'}</div>
            </div>
            <input type="checkbox" ${a.allow_token_spend ? 'checked' : ''} onchange="updateControls('${a.id}', this.checked, null)" class="w-4 h-4 accent-zinc-200" />
          </label>

          <!-- Two Main Action Buttons -->
          <div class="grid grid-cols-2 gap-2">
            <button onclick="runResearch('${a.id}', false)" class="ag-btn-secondary text-xs py-2.5 px-2 rounded-lg">
              ${(a.research_files && a.research_files.length > 0) ? '4 Pilares Listos<br/><span class="text-[10px] font-mono-tech text-zinc-400">0 tokens · Ver avance</span>' : 'Investigar Tema<br/><span class="text-[10px] font-mono-tech text-zinc-400">4 Pilares NotebookLM</span>'}
            </button>
            <button onclick="runResolve('${a.id}', false)" ${(a.allow_token_spend || a.resolution_local_path) ? '' : 'disabled'} class="ag-btn-primary text-xs py-2.5 px-2 rounded-lg">
              ${a.resolution_local_path ? 'Resolución Lista<br/><span class="text-[10px] font-mono-tech opacity-75">0 tokens · Ver avance</span>' : 'Resolver Actividad<br/><span class="text-[10px] font-mono-tech opacity-75">Consenso IA</span>'}
            </button>
          </div>

          ${(a.research_files && a.research_files.length > 0) || a.resolution_local_path ? `
            <div class="flex items-center justify-end gap-3 pt-0.5">
              ${(a.research_files && a.research_files.length > 0) ? `<button onclick="runResearch('${a.id}', true)" class="text-[10px] font-mono-tech text-zinc-500 hover:text-zinc-200 underline">Regenerar 4 Pilares</button>` : ''}
              ${(a.resolution_local_path && a.allow_token_spend) ? `<button onclick="runResolve('${a.id}', true)" class="text-[10px] font-mono-tech text-zinc-500 hover:text-zinc-200 underline">Crear nueva versión (_v2)</button>` : ''}
            </div>
          ` : ''}

          ${filesHtml ? `<div class="bg-[#101013] border border-[#26262c] rounded-lg p-3 space-y-2"><div class="text-[11px] font-mono-tech text-zinc-400 uppercase">4 Pilares Generados (NotebookLM):</div><div class="flex flex-wrap gap-1.5">${filesHtml}</div></div>` : ''}

          ${a.consensus_report ? `<div class="bg-[#101013] border border-[#26262c] rounded-lg p-3 space-y-2"><div class="text-[11px] font-mono-tech text-zinc-400 uppercase">Dictamen del Árbitro de Consenso:</div><p class="text-xs text-zinc-300 whitespace-pre-line leading-relaxed">${a.consensus_report}</p>${resLink}</div>` : ''}
        </div>
      `;
    }

    function renderAssignments() {
      const psm = stateCourses.filter(c => !c.is_external && (selectedCourseId === null || c.id === selectedCourseId));
      const acts = psm.flatMap(c => c.assignments.filter(a => !a.is_overdue).map(a => ({...a, course_name: c.name}))).filter(a => !onlyPending || !a.is_completed);
      document.getElementById('assignments-list').innerHTML = acts.length
        ? acts.map(renderCardHtml).join('')
        : '<div class="text-center text-zinc-500 text-xs py-12 font-mono-tech">Sin actividades pendientes o vigentes en esta materia.</div>';

      const ext = stateCourses.filter(c => c.is_external).flatMap(c => c.assignments.filter(a => !a.is_overdue).map(a => ({...a, course_name: c.name})));
      document.getElementById('external-list').innerHTML = ext.map(renderCardHtml).join('');
    }

    async function openInspector(assignmentId, fetchRemote = false) {
      const modal = document.getElementById('inspector-modal');
      modal.classList.remove('hidden');
      document.getElementById('insp-guidelines-text').textContent = 'Cargando lineamientos y documentos...';
      document.getElementById('insp-ai-docs-list').innerHTML = '';

      const btnRefresh = document.getElementById('btn-refresh-saia-doc');
      btnRefresh.onclick = () => openInspector(assignmentId, true);

      const r = await fetch(`/api/assignments/${assignmentId}/inspect?fetch_remote=${fetchRemote}`);
      const d = await r.json();

      document.getElementById('insp-course').textContent = d.assignment.course_name || 'MATERIA';
      document.getElementById('insp-title').textContent = d.assignment.title;
      document.getElementById('insp-guidelines-text').textContent = d.teacher_guidelines;

      // Teacher attachments
      const tFiles = d.teacher_local_files || [];
      const rawAtt = d.teacher_attachments || [];
      const tfContainer = document.getElementById('insp-teacher-files');
      if (tFiles.length > 0) {
        tfContainer.innerHTML = tFiles.map(f => `
          <a href="/api/files/download?path=${encodeURIComponent(f.local_path)}" target="_blank" class="ag-card-interactive rounded-lg p-3 flex items-center justify-between text-xs">
            <span class="font-mono-tech text-zinc-200">${f.name}</span>
            <span class="text-zinc-400">Descargar original →</span>
          </a>
        `).join('');
      } else if (rawAtt.length > 0) {
        tfContainer.innerHTML = rawAtt.map(f => `
          <div class="ag-card rounded-lg p-3 flex items-center justify-between text-xs">
            <span class="font-mono-tech text-zinc-300">${f.name}</span>
            <span class="text-zinc-500">Pulsa "Extraer en vivo de SAIA" para descargar</span>
          </div>
        `).join('');
      } else {
        tfContainer.innerHTML = `<div class="text-xs text-zinc-500 font-mono-tech">No se detectaron archivos adjuntos del profesor en esta actividad.</div>`;
      }

      const extBox = document.getElementById('insp-teacher-extracted-box');
      if (d.teacher_files_extracted_text && d.teacher_files_extracted_text.trim().length > 0) {
        extBox.classList.remove('hidden');
        document.getElementById('insp-teacher-extracted-text').textContent = d.teacher_files_extracted_text;
      } else {
        extBox.classList.add('hidden');
      }

      // AI Generated Documents
      const aiDocs = d.ai_generated_documents || [];
      const aiContainer = document.getElementById('insp-ai-docs-list');
      if (aiDocs.length === 0) {
        aiContainer.innerHTML = `<div class="ag-card rounded-xl p-6 text-center text-xs text-zinc-500">Aún no se han generado documentos con el Consorcio de IA para esta actividad. Usa los botones "Investigar Tema" o "Resolver Actividad".</div>`;
      } else {
        aiContainer.innerHTML = aiDocs.map(doc => `
          <div class="ag-card rounded-xl p-4 space-y-3">
            <div class="flex items-center justify-between border-b border-[#222228] pb-2.5">
              <div>
                <span class="text-[10px] font-mono-tech uppercase text-zinc-500">${doc.category}</span>
                <h4 class="text-xs font-semibold text-zinc-100 font-mono-tech">${doc.name}</h4>
              </div>
              <a href="${doc.url && !doc.url.startsWith('local://') ? doc.url : '/api/files/download?path=' + encodeURIComponent(doc.local_path)}" target="_blank" class="ag-btn-primary text-[11px] px-3 py-1.5 rounded-md">
                Descargar .docx
              </a>
            </div>
            <div class="text-xs text-zinc-300 whitespace-pre-line leading-relaxed max-h-80 overflow-y-auto pr-1">${doc.content || 'Sin vista previa de texto.'}</div>
          </div>
        `).join('');
      }

      if (fetchRemote) {
        showToast('Lineamientos y adjuntos sincronizados desde SAIA.');
        await loadAll();
      }
    }

    function closeInspector() {
      document.getElementById('inspector-modal').classList.add('hidden');
    }

    function switchInspectorTab(tab) {
      const isTeacher = tab === 'teacher';
      document.getElementById('insp-body-teacher').classList.toggle('hidden', !isTeacher);
      document.getElementById('insp-body-ai').classList.toggle('hidden', isTeacher);

      document.getElementById('insp-tab-teacher').className = isTeacher
        ? 'py-2.5 text-xs font-semibold border-b-2 border-zinc-100 text-zinc-100'
        : 'py-2.5 text-xs font-medium border-b-2 border-transparent text-zinc-500';
      document.getElementById('insp-tab-ai').className = !isTeacher
        ? 'py-2.5 text-xs font-semibold border-b-2 border-zinc-100 text-zinc-100'
        : 'py-2.5 text-xs font-medium border-b-2 border-transparent text-zinc-500';
    }

    async function updateControls(id, allow, mode) {
      const body = {};
      if (allow !== null) body.allow_token_spend = allow;
      if (mode !== null) body.task_mode = mode;
      await fetch(`/api/assignments/${id}/controls`, {
        method: 'PATCH',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body)
      });
      await loadAll();
    }

    let progPollInterval = null;
    let progTimerInterval = null;
    let progStartTime = 0;
    let displayedPercent = 5;
    let backendPercent = 8;

    function getStageCeiling(bPct) {
      if (bPct < 25) return 22;
      if (bPct < 50) return 47;
      if (bPct < 75) return 72;
      if (bPct < 88) return 86;
      return 98;
    }

    function updateStepPills(bPct) {
      const thresholds = [10, 25, 50, 75, 88];
      for (let i = 0; i < 5; i++) {
        const el = document.getElementById('prog-step-' + (i + 1));
        if (!el) continue;
        const nextThresh = thresholds[i + 1] || 100;
        if (bPct >= 100 || bPct >= nextThresh) {
          el.className = 'py-1.5 px-1 rounded border border-zinc-300 bg-zinc-100 text-zinc-950 font-semibold';
        } else if (bPct >= thresholds[i]) {
          el.className = 'py-1.5 px-1 rounded border border-zinc-400 bg-[#1c1c21] text-zinc-100 font-semibold';
        } else {
          el.className = 'py-1.5 px-1 rounded border border-[#26262c] bg-[#141417] text-zinc-500';
        }
      }
    }

    function startProgressModal(assignmentId, initialTitle) {
      const modal = document.getElementById('progress-modal');
      modal.classList.remove('hidden');
      document.getElementById('prog-actions').classList.add('hidden');
      document.getElementById('prog-dot').className = 'w-2 h-2 rounded-full bg-amber-400 animate-pulse';
      document.getElementById('prog-header-title').textContent = initialTitle;
      document.getElementById('prog-stage-text').textContent = 'Conectando con SAIA PSM y preparando contexto...';
      displayedPercent = 8;
      backendPercent = 10;
      document.getElementById('prog-percent-text').textContent = '8%';
      const fill = document.getElementById('prog-bar-fill');
      fill.className = 'h-full bg-zinc-100 transition-all duration-500 ease-out';
      fill.style.width = '8%';
      updateStepPills(backendPercent);

      progStartTime = Date.now();
      document.getElementById('prog-timer').textContent = '00:00s';
      if (progTimerInterval) clearInterval(progTimerInterval);
      progTimerInterval = setInterval(() => {
        const sec = Math.floor((Date.now() - progStartTime) / 1000);
        const mm = String(Math.floor(sec / 60)).padStart(2, '0');
        const ss = String(sec % 60).padStart(2, '0');
        document.getElementById('prog-timer').textContent = `${mm}:${ss}s`;
        // Smooth micro-increment strictly within the current stage ceiling so it never jumps to '5. Drive' prematurely
        const ceiling = getStageCeiling(backendPercent);
        if (displayedPercent < ceiling) {
          displayedPercent = Math.min(ceiling, displayedPercent + 1);
          document.getElementById('prog-percent-text').textContent = `${displayedPercent}%`;
          document.getElementById('prog-bar-fill').style.width = `${displayedPercent}%`;
        }
      }, 1200);

      if (progPollInterval) clearInterval(progPollInterval);
      progPollInterval = setInterval(async () => {
        try {
          const r = await fetch(`/api/assignments/${assignmentId}/progress`);
          if (!r.ok) return;
          const p = await r.json();
          if (p.percent) {
            backendPercent = p.percent;
            if (p.percent > displayedPercent) {
              displayedPercent = p.percent;
            }
          }
          if (p.stage && p.stage !== 'En espera...') {
            document.getElementById('prog-stage-text').textContent = p.stage;
          }
          document.getElementById('prog-percent-text').textContent = `${displayedPercent}%`;
          document.getElementById('prog-bar-fill').style.width = `${displayedPercent}%`;
          updateStepPills(backendPercent);
        } catch (e) {}
      }, 900);
    }

    function finishProgressModal(assignmentId, success, finalMsg) {
      if (progPollInterval) clearInterval(progPollInterval);
      if (progTimerInterval) clearInterval(progTimerInterval);
      const fill = document.getElementById('prog-bar-fill');
      if (success) {
        displayedPercent = 100;
        document.getElementById('prog-dot').className = 'w-2 h-2 rounded-full bg-emerald-400';
        document.getElementById('prog-header-title').textContent = 'PROCESO COMPLETADO · 100%';
        document.getElementById('prog-stage-text').textContent = finalMsg;
        document.getElementById('prog-percent-text').textContent = '100%';
        fill.className = 'h-full bg-emerald-400 transition-all duration-300 ease-out';
        fill.style.width = '100%';
        updateStepPills(100);
      } else {
        document.getElementById('prog-dot').className = 'w-2 h-2 rounded-full bg-red-400';
        document.getElementById('prog-header-title').textContent = 'AVISO DEL SISTEMA';
        document.getElementById('prog-stage-text').textContent = finalMsg;
        fill.className = 'h-full bg-red-400 transition-all duration-300 ease-out';
      }
      const actions = document.getElementById('prog-actions');
      actions.classList.remove('hidden');
      const openBtn = document.getElementById('prog-open-docs-btn');
      openBtn.onclick = () => {
        closeProgressModal();
        openInspector(assignmentId, false);
        switchInspectorTab('ai');
      };
    }

    function closeProgressModal() {
      if (progPollInterval) clearInterval(progPollInterval);
      if (progTimerInterval) clearInterval(progTimerInterval);
      document.getElementById('progress-modal').classList.add('hidden');
    }

    async function runResearch(id, force = false) {
      startProgressModal(id, force ? 'REGENERANDO 4 PILARES' : 'INVESTIGANDO 4 PILARES NOTEBOOKLM');
      try {
        const r = await fetch(`/api/assignments/${id}/research?force=${force}`, {method: 'POST'});
        const d = await r.json();
        await loadAll();
        if (d.cached) {
          closeProgressModal();
          showToast(d.message || 'Avance previo cargado sin gastar tokens.');
          openInspector(id, false);
          switchInspectorTab('ai');
        } else if (r.ok && d.ok) {
          finishProgressModal(id, true, 'Los 4 documentos (.docx) están listos y sincronizados en Google Drive.');
        } else {
          finishProgressModal(id, false, 'Error: ' + (d.detail || 'No se pudo completar'));
        }
      } catch (err) {
        finishProgressModal(id, false, 'Error de conexión con el servidor local.');
      }
    }

    async function runResolve(id, force = false) {
      startProgressModal(id, force ? 'CREANDO NUEVA VERSIÓN (_v2)' : 'RESOLVIENDO ACTIVIDAD POR CONSENSO');
      try {
        const r = await fetch(`/api/assignments/${id}/resolve?force=${force}`, {method: 'POST'});
        const d = await r.json();
        await loadAll();
        if (d.cached) {
          closeProgressModal();
          showToast(d.message || 'Resolución previa cargada sin gastar tokens.');
          openInspector(id, false);
          switchInspectorTab('ai');
        } else if (r.ok && d.ok) {
          finishProgressModal(id, true, 'Borrador Word (.docx) con plantilla PSM completado y listo para tu revisión.');
        } else {
          finishProgressModal(id, false, 'Aviso: ' + (d.detail || 'No se pudo completar'));
        }
      } catch (err) {
        finishProgressModal(id, false, 'Error de conexión con el servidor local.');
      }
    }

    async function syncSaia() {
      showToast('Sincronizando materias y actividades con SAIA PSM...');
      const r = await fetch('/api/saia/sync', {method: 'POST'});
      const d = await r.json();
      showToast(d.synced ? 'Sincronización con SAIA completada.' : ('Estado SAIA: ' + d.reason));
      await loadAll();
    }

    async function createExternal(autoResearch) {
      const title = document.getElementById('ext-title').value.trim();
      if (!title) return showToast('El título del tema es obligatorio.');
      const fd = new FormData();
      fd.append('title', title);
      fd.append('category_name', document.getElementById('ext-cat').value.trim());
      fd.append('description_text', document.getElementById('ext-desc').value.trim());
      fd.append('task_mode', extMode);
      const files = document.getElementById('ext-files').files;
      for (let i = 0; i < files.length; i++) fd.append('files', files[i]);

      showToast('Registrando tema libre...');
      const r = await fetch('/api/external/create', {method: 'POST', body: fd});
      const d = await r.json();
      if (d.ok && autoResearch) {
        await runResearch(d.assignment.id);
      } else {
        showToast('Tema libre registrado.');
        await loadAll();
      }
      document.getElementById('ext-title').value = '';
      document.getElementById('ext-desc').value = '';
    }

    async function saveCookie() {
      const c = document.getElementById('cookie-input').value.trim();
      if (!c) return showToast('Ingresa primero el valor de la cookie MoodleSession.');
      const r = await fetch('/api/saia/cookie', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({moodle_session: c})
      });
      const d = await r.json();
      showToast(d.session_active ? 'Sesión SAIA verificada y activa.' : ('Cookie guardada: ' + d.reason));
      await loadAll();
    }

    async function saveDriveBridge() {
      const url = document.getElementById('drive-bridge-input').value.trim();
      if (!url) return showToast('Ingresa la URL de Google Apps Script.');
      showToast('Verificando conexión con tu Google Drive...');
      const r = await fetch('/api/drive/bridge', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({bridge_url: url})
      });
      const d = await r.json();
      showToast(d.message || 'Conectado.');
      await loadAll();
    }

    async function addExtraGeminiKey() {
      const input = document.getElementById('extra-gemini-key-input');
      const key = input.value.trim();
      if (!key) return showToast('Pega primero la API Key adicional de Google Gemini.');
      const r = await fetch('/api/settings/gemini-key', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({api_key: key})
      });
      const d = await r.json();
      if (r.ok && d.ok) {
        input.value = '';
        showToast(d.message);
        await loadAll();
      } else {
        showToast('Error: ' + (d.detail || d.message || 'No se pudo guardar'));
      }
    }

    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').catch(() => {});
    }
    loadAll();
  </script>
</body>
</html>
"""
