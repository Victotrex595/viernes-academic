import os
import re
import glob
import shutil

def patch():
    # 1. Copiar recursos de iconos a android/app/src/main/res/
    res_source = os.path.join(os.path.dirname(__file__), "android_res")
    res_dest = os.path.join("android", "app", "src", "main", "res")
    if os.path.exists(res_source) and os.path.exists(res_dest):
        for root, dirs, files in os.walk(res_source):
            rel_path = os.path.relpath(root, res_source)
            target_dir = os.path.join(res_dest, rel_path)
            os.makedirs(target_dir, exist_ok=True)
            for f in files:
                src_file = os.path.join(root, f)
                dst_file = os.path.join(target_dir, f)
                shutil.copy2(src_file, dst_file)
        print("Iconos de V.I.E.R.N.E.S. con fondo blanco copiados exitosamente a res/")
    else:
        print(f"WARN: res_source={res_source} o res_dest={res_dest} no encontrados")

    # 2. Configurar strings.xml con nombre V.I.E.R.N.E.S.
    values_dir = os.path.join("android", "app", "src", "main", "res", "values")
    os.makedirs(values_dir, exist_ok=True)
    strings_path = os.path.join(values_dir, "strings.xml")
    strings_content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">V.I.E.R.N.E.S.</string>
</resources>
"""
    with open(strings_path, "w", encoding="utf-8") as f:
        f.write(strings_content)
    print("strings.xml creado con app_name=V.I.E.R.N.E.S.")

    # 3. Patch AndroidManifest.xml
    manifest_path = os.path.join("android", "app", "src", "main", "AndroidManifest.xml")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Permisos
        if "android.permission.INTERNET" not in content:
            content = re.sub(
                r'(<manifest[^>]*>)',
                r'\1\n    <uses-permission android:name="android.permission.INTERNET"/>\n    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>',
                content,
                count=1,
            )

        # Cleartext
        if "usesCleartextTraffic" not in content:
            content = content.replace("<application", '<application\n        android:usesCleartextTraffic="true"', 1)

        # Label & Icons
        content = re.sub(r'android:label="[^"]*"', 'android:label="V.I.E.R.N.E.S."', content)
        if 'android:roundIcon' not in content:
            content = content.replace('<application', '<application\n        android:roundIcon="@mipmap/ic_launcher_round"', 1)
        if 'android:icon' not in content:
            content = content.replace('<application', '<application\n        android:icon="@mipmap/ic_launcher"', 1)

        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("AndroidManifest.xml actualizado con permisos, iconos y nombre V.I.E.R.N.E.S.")
    else:
        print(f"WARN: No se encontro {manifest_path}")

    # 4. Forzar compileSdk 36 en build.gradle y build.gradle.kts
    gradle_files = glob.glob("android/**/*.gradle*", recursive=True)
    for gfile in gradle_files:
        try:
            with open(gfile, "r", encoding="utf-8") as f:
                gcontent = f.read()
            gcontent_mod = re.sub(r'compileSdk\s*=\s*\d+', 'compileSdk = 36', gcontent)
            gcontent_mod = re.sub(r'compileSdkVersion\s*\d+', 'compileSdkVersion 36', gcontent_mod)
            gcontent_mod = re.sub(r'compileSdk\s*=\s*flutter\.compileSdkVersion', 'compileSdk = 36', gcontent_mod)
            gcontent_mod = re.sub(r'compileSdkVersion\s*flutter\.compileSdkVersion', 'compileSdkVersion 36', gcontent_mod)
            if gcontent_mod != gcontent:
                with open(gfile, "w", encoding="utf-8") as f:
                    f.write(gcontent_mod)
                print(f"Actualizado compileSdk a 36 en {gfile}")
        except Exception as e:
            print(f"Error procesando {gfile}: {e}")

    # 5. local.properties
    local_props = os.path.join("android", "local.properties")
    if os.path.exists(local_props):
        with open(local_props, "r", encoding="utf-8") as f:
            lp = f.read()
        if "flutter.compileSdkVersion" not in lp:
            with open(local_props, "a", encoding="utf-8") as f:
                f.write("\nflutter.compileSdkVersion=36\n")
            print("Agregado flutter.compileSdkVersion=36 en local.properties")

if __name__ == "__main__":
    patch()
