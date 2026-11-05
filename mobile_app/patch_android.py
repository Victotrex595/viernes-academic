import os
import re
import glob

def patch():
    manifest_path = os.path.join("android", "app", "src", "main", "AndroidManifest.xml")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            content = f.read()

        if "android.permission.INTERNET" not in content:
            content = re.sub(
                r'(<manifest[^>]*>)',
                r'\1\n    <uses-permission android:name="android.permission.INTERNET"/>\n    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>',
                content,
                count=1,
            )

        if "usesCleartextTraffic" not in content:
            content = content.replace("<application", '<application\n        android:usesCleartextTraffic="true"', 1)

        content = re.sub(r'android:label="[^"]*"', 'android:label="V.I.E.R.N.E.S."', content, count=1)

        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✓ AndroidManifest.xml parcheado con permisos INTERNET, red y etiqueta V.I.E.R.N.E.S.")
    else:
        print(f"WARN: No se encontró {manifest_path}")

    # Forzar compileSdk 36 en build.gradle y build.gradle.kts
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
                print(f"✓ Actualizado compileSdk a 36 en {gfile}")
        except Exception as e:
            print(f"Error procesando {gfile}: {e}")

    # local.properties
    local_props = os.path.join("android", "local.properties")
    if os.path.exists(local_props):
        with open(local_props, "r", encoding="utf-8") as f:
            lp = f.read()
        if "flutter.compileSdkVersion" not in lp:
            with open(local_props, "a", encoding="utf-8") as f:
                f.write("\nflutter.compileSdkVersion=36\n")
            print("✓ Agregado flutter.compileSdkVersion=36 en local.properties")

if __name__ == "__main__":
    patch()
