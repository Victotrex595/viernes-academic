import os
import sys
import webbrowser
from pathlib import Path
from dotenv import dotenv_values

try:
    from huggingface_hub import HfApi
except ImportError:
    print("❌ Falta la librería 'huggingface_hub'.")
    print("Instalando dependencia...")
    os.system(f'"{sys.executable}" -m pip install huggingface_hub')
    from huggingface_hub import HfApi


PROJECT_ROOT = Path(__file__).resolve().parent


def main():
    print("=" * 75)
    print("   🚀 DESPLIEGUE AUTOMÁTICO A HUGGING FACE SPACES - V.I.E.R.N.E.S.")
    print("=" * 75)
    print("Este asistente creará o actualizará tu Space en Hugging Face (24/7 Gratis).")
    print("16 GB RAM · 2 vCPU · SSL Gratis · Sin necesidad de tarjeta de crédito.\n")

    # 1. Solicitar Token de Hugging Face
    token = os.getenv("HF_TOKEN", "").strip()
    if not token:
        print("Para continuar necesitas un Access Token de Hugging Face con permisos 'Write':")
        print("  1. Abre en tu navegador: https://huggingface.co/settings/tokens")
        print("  2. Haz clic en 'Create new token'")
        print("  3. Elige Type: 'Write' (o 'Fine-grained' con permisos de Spaces)")
        print("  4. Dale un nombre (ej. 'viernes-deploy') y copia el token que empieza por 'hf_...'\n")
        token = input("Pega tu Token de Hugging Face aquí: ").strip()

    if not token:
        print("❌ Token no proporcionado. Abortando.")
        return

    api = HfApi(token=token)

    # 2. Validar identidad del usuario
    try:
        user_info = api.whoami()
        username = user_info.get("name") or user_info.get("preferred_username")
        print(f"\n✅ Conectado exitosamente como: @{username}")
    except Exception as e:
        print(f"\n❌ Error de autenticación con Hugging Face: {e}")
        print("Verifica que el token sea correcto y tenga permisos 'Write'.")
        return

    # 3. Solicitar nombre del Space
    default_space_name = "viernes-academic"
    space_name_input = input(f"\nNombre del Space [{default_space_name}]: ").strip()
    space_name = space_name_input or default_space_name
    repo_id = f"{username}/{space_name}"

    # 4. Verificar si el Space existe o crearlo
    print(f"\n[1/3] Verificando estado del Space '{repo_id}'...")
    exists = False
    try:
        exists = api.repo_exists(repo_id=repo_id, repo_type="space")
    except Exception:
        exists = False

    if not exists:
        print(f"El Space '{repo_id}' aún no existe. Intentando crearlo automáticamente...")
        created = False
        try:
            api.create_repo(
                repo_id=repo_id,
                repo_type="space",
                space_sdk="docker",
                exist_ok=True,
                private=False,
            )
            created = True
            print(f"✅ Space creado exitosamente: https://huggingface.co/spaces/{repo_id}")
        except Exception as e:
            err_msg = str(e)
            print("\n" + "!" * 75)
            print("⚠️ No se pudo crear el Space automáticamente mediante la API.")
            print(f"Detalle del error: {err_msg}")
            print("!" * 75)

            # Causas comunes
            if "verify your email" in err_msg.lower() or "403" in err_msg:
                print("\n📌 CAUSA PRINCIPAL EN CUENTAS RECIÉN CREADAS:")
                print("1. Hugging Face requiere CONFIRMAR TU CORREO ELECTRÓNICO antes de permitir crear Spaces.")
                print("   Revisa tu bandeja de entrada (o Spam) y haz clic en el enlace de confirmación de Hugging Face.")
                print("2. O tu Token fue creado con rol 'Read' en lugar de 'Write'.")

            new_space_url = "https://huggingface.co/new-space"
            print("\n💡 SOLUCIÓN FÁCIL:")
            print(f"1. Abre este enlace para crearlo en 10 segundos desde la web:")
            print(f"   {new_space_url}")
            print(f"2. Configura:")
            print(f"   - Space name: {space_name}")
            print(f"   - Space SDK: Docker (Blank)")
            print(f"   - Visibility: Public")
            print(f"3. Haz clic en 'Create Space'.\n")

            choice = input("¿Deseas abrir la página para crearlo en el navegador ahora? (S/n): ").strip().lower()
            if choice != "n":
                try:
                    webbrowser.open(new_space_url)
                except Exception:
                    pass

            input("\nCuando hayas creado el Space en la web (o verificado tu correo), presiona ENTER para continuar...")

            # Re-verificar si ya existe
            try:
                if api.repo_exists(repo_id=repo_id, repo_type="space"):
                    print(f"✅ ¡Space detectado correctamente en: https://huggingface.co/spaces/{repo_id}!")
                else:
                    print(f"❌ Aún no se detecta el Space '{repo_id}'. Asegúrate de crearlo con ese mismo nombre exacto.")
                    return
            except Exception as ex_check:
                print(f"❌ Error al comprobar el Space: {ex_check}")
                return
    else:
        print(f"✅ Space existente encontrado: https://huggingface.co/spaces/{repo_id}")

    # 5. Sincronizar Secretos (API Keys) desde .env
    print(f"\n[2/3] Sincronizando Secretos y Claves API de forma encriptada...")
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        env_vars = dotenv_values(env_file)
        secret_keys = [
            "GEMINI_API_KEY",
            "GEMINI_API_KEY_2",
            "GEMINI_API_KEY_3",
            "DEEPSEEK_API_KEY",
            "GOOGLE_DRIVE_BRIDGE_URL",
            "SAIA_USERNAME",
            "SAIA_PASSWORD",
        ]
        synced_count = 0
        for k in secret_keys:
            val = env_vars.get(k)
            if val and val.strip():
                try:
                    api.add_space_secret(repo_id=repo_id, key=k, value=val.strip())
                    print(f"   [✓] Secreto configurado: {k}")
                    synced_count += 1
                except Exception as ex:
                    print(f"   [!] Nota con {k}: {ex}")
        if synced_count > 0:
            print(f"✅ {synced_count} secreto(s) encriptado(s) en Hugging Face Settings.")
    else:
        print("ℹ️ No se encontró archivo .env local. Recuerda agregar tus secretos en:")
        print(f"   https://huggingface.co/spaces/{repo_id}/settings")

    # 6. Subir archivos del proyecto
    print(f"\n[3/3] Subiendo archivos del proyecto al Space...")
    ignore_patterns = [
        ".venv/**",
        "backend/.venv/**",
        ".git/**",
        "*.pyc",
        "__pycache__/**",
        "backend/**/__pycache__/**",
        "mobile_app/**",
        ".pytest_cache/**",
        "backend/.pytest_cache/**",
        "*.bat",
        ".env",
        ".env.example",
        "caddy_data/**",
        "caddy_config/**",
        "subir_a_huggingface.py",
        "deploy_oracle_cloud.sh",
        "docker-compose.yml",
        "Caddyfile",
        "data/downloads/**",
        "backend/downloads/**",
        "Moodle_PSM_Estudio/**",
        "backend/Moodle_PSM_Estudio/**",
    ]

    try:
        api.upload_folder(
            folder_path=str(PROJECT_ROOT),
            repo_id=repo_id,
            repo_type="space",
            commit_message="Despliegue V.I.E.R.N.E.S. PhoneApp Academic a Hugging Face Spaces",
            ignore_patterns=ignore_patterns,
        )
        print("✅ Archivos subidos exitosamente.")
    except Exception as e:
        print(f"❌ Error al subir los archivos: {e}")
        return

    # URL directa de la web app en Hugging Face
    clean_space_name = space_name.lower().replace("_", "-")
    clean_username = username.lower().replace("_", "-")
    direct_app_url = f"https://{clean_username}-{clean_space_name}.hf.space"

    print("\n" + "=" * 75)
    print("   🎉 ¡DESPLIEGUE INICIADO EXITOSAMENTE EN HUGGING FACE SPACES!")
    print("=" * 75)
    print("Hugging Face está construyendo el contenedor Docker (toma ~1 o 2 minutos).")
    print(f"\n📍 Panel de Control y Logs en vivo:")
    print(f"   https://huggingface.co/spaces/{repo_id}")
    print(f"\n📱 URL Pública Directa (para tu teléfono y navegador):")
    print(f"   {direct_app_url}")
    print(f"\n📑 Documentación de la API (Swagger):")
    print(f"   {direct_app_url}/docs")
    print("\n¡Ya puedes abrir esa URL directa en tu teléfono desde cualquier parte!")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    main()
