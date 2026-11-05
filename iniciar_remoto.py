import os
import re
import sys
import time
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
CLOUDFLARED_EXE = PROJECT_ROOT / "cloudflared.exe"
PYTHON_EXE = PROJECT_ROOT / "backend" / ".venv" / "Scripts" / "python.exe"
if not PYTHON_EXE.exists():
    PYTHON_EXE = Path(sys.executable)


def copy_to_clipboard(text: str):
    try:
        subprocess.run("clip", input=text.strip().encode("utf-8"), check=False)
    except Exception:
        pass


def is_backend_running() -> bool:
    import urllib.request
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/api/health", timeout=1.5) as resp:
            return resp.status == 200
    except Exception:
        return False


def main():
    print("=" * 75)
    print("   🌐 INICIANDO V.I.E.R.N.E.S. CON ACCESO REMOTO SEGURO (CLOUDFLARE)")
    print("=" * 75)
    print("100% Gratis · Sin tarjetas · Sin registro · Conexión segura HTTPS con tu celular\n")

    # 1. Verificar si el backend está activo o levantarlo
    backend_proc = None
    if not is_backend_running():
        print("[1/2] Iniciando servidor backend local...")
        backend_proc = subprocess.Popen(
            [str(PYTHON_EXE), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=str(PROJECT_ROOT / "backend"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # Esperar hasta que responda
        for _ in range(15):
            if is_backend_running():
                break
            time.sleep(0.5)
        print("✅ Backend activo en http://127.0.0.1:8000")
    else:
        print("✅ Servidor backend ya se encuentra activo en http://127.0.0.1:8000")

    # 2. Iniciar Cloudflare Tunnel
    if not CLOUDFLARED_EXE.exists():
        print("❌ No se encontró cloudflared.exe en la carpeta.")
        return

    print("\n[2/2] Creando túnel seguro HTTPS con Cloudflare...")
    cf_proc = subprocess.Popen(
        [str(CLOUDFLARED_EXE), "tunnel", "--url", "http://127.0.0.1:8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )

    tunnel_url = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com")

    # Leer salida en tiempo real hasta capturar la URL
    for line in iter(cf_proc.stdout.readline, ""):
        match = url_pattern.search(line)
        if match:
            tunnel_url = match.group(0)
            break

    if not tunnel_url:
        print("❌ No se pudo obtener la URL de Cloudflare. Revisa tu conexión a internet.")
        if backend_proc:
            backend_proc.terminate()
        return

    # Copiar al portapapeles de Windows
    copy_to_clipboard(tunnel_url)

    print("\n" + "=" * 75)
    print("   🎉 ¡TU SERVIDOR ESTÁ EN LÍNEA Y ACCESIBLE DESDE CUALQUIER TELÉFONO!")
    print("=" * 75)
    print(f"\n📱 Enlace HTTPS Público:")
    print(f"   👉  {tunnel_url}  👈")
    print("\n📋 (¡El enlace ha sido copiado automáticamente a tu portapapeles!)")
    print("   Pégalo en WhatsApp, Telegram o envíatelo al teléfono para abrirlo.")
    print("\n💡 Instrucciones para tu teléfono:")
    print("   1. Abre ese enlace en Chrome o Safari en tu celular.")
    print("   2. Toca 'Agregar a la pantalla de inicio' para instalarlo como App.")
    print("   3. Funciona tanto con Wi-Fi como con datos móviles (4G/5G).")
    print("\n⚠️ Para detener el servidor, mantén presionadas las teclas Ctrl + C.")
    print("=" * 75 + "\n")

    try:
        # Mantener el proceso vivo
        cf_proc.wait()
    except KeyboardInterrupt:
        print("\nDeteniendo túnel y servidor...")
        cf_proc.terminate()
        if backend_proc:
            backend_proc.terminate()
        print("Servicios detenidos.")


if __name__ == "__main__":
    main()
