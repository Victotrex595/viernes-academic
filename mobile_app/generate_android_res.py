import os
from PIL import Image, ImageDraw

def create_master_images():
    # 1. Master Full Icon with white background (512x512)
    full_icon = Image.new("RGBA", (512, 512), (255, 255, 255, 255))
    draw_full = ImageDraw.Draw(full_icon)

    # Shadow for badge
    draw_full.rounded_rectangle([68, 72, 444, 448], radius=85, fill=(225, 225, 232, 255))
    # Badge
    draw_full.rounded_rectangle([64, 64, 448, 448], radius=85, fill=(15, 15, 18, 255), outline=(46, 46, 54, 255), width=4)

    # Top board
    draw_full.polygon([(256, 168), (406, 236), (256, 304), (106, 236)], fill=(245, 245, 248, 255))
    draw_full.polygon([(256, 178), (386, 236), (256, 294), (126, 236)], outline=(200, 200, 208, 255), width=2)
    # Center button
    draw_full.ellipse([244, 230, 268, 242], fill=(20, 20, 24, 255))
    # Base
    draw_full.polygon([(165, 272), (165, 338), (256, 390), (347, 338), (347, 272), (256, 312)], fill=(210, 210, 218, 255))
    # Tassel
    draw_full.line([(256, 236), (368, 266), (368, 342)], fill=(245, 245, 250, 255), width=7)
    draw_full.ellipse([360, 338, 376, 354], fill=(220, 220, 228, 255))
    draw_full.polygon([(353, 352), (383, 352), (387, 388), (349, 388)], fill=(245, 245, 250, 255))

    # 2. Master Foreground for Adaptive Icons (432x432 transparent canvas, badge in center safe zone)
    # In Android adaptive icons, safe zone is inner 66% (radius ~140 on 432x432)
    fg_icon = Image.new("RGBA", (432, 432), (0, 0, 0, 0))
    # Resize the badge area from full_icon
    # Crop badge area from full_icon
    badge_crop = full_icon.crop((50, 50, 462, 462))
    # Scale badge to fit safe zone: ~270x270
    badge_scaled = badge_crop.resize((270, 270), Image.Resampling.LANCZOS)
    # Paste centered at (432-270)/2 = 81
    fg_icon.paste(badge_scaled, (81, 81), badge_scaled)

    # 3. Master Round Icon (512x512 with circle mask)
    round_icon = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    mask = Image.new("L", (512, 512), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse([0, 0, 512, 512], fill=255)
    round_icon.paste(full_icon, (0, 0), mask)

    return full_icon, fg_icon, round_icon

def export_android_res():
    full_icon, fg_icon, round_icon = create_master_images()
    base_dir = "mobile_app/android_res"
    os.makedirs(base_dir, exist_ok=True)

    # Values folder for colors.xml
    values_dir = os.path.join(base_dir, "values")
    os.makedirs(values_dir, exist_ok=True)
    with open(os.path.join(values_dir, "colors.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#FFFFFF</color>\n</resources>\n')

    # Anydpi-v26 folder for adaptive icon xmls
    anydpi_dir = os.path.join(base_dir, "mipmap-anydpi-v26")
    os.makedirs(anydpi_dir, exist_ok=True)
    with open(os.path.join(anydpi_dir, "ic_launcher.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n    <background android:drawable="@color/ic_launcher_background"/>\n    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>\n</adaptive-icon>\n')
    with open(os.path.join(anydpi_dir, "ic_launcher_round.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n    <background android:drawable="@color/ic_launcher_background"/>\n    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>\n</adaptive-icon>\n')

    # Densities: (folder, full_size, fg_size)
    densities = [
        ("mipmap-mdpi", 48, 108),
        ("mipmap-hdpi", 72, 162),
        ("mipmap-xhdpi", 96, 216),
        ("mipmap-xxhdpi", 144, 324),
        ("mipmap-xxxhdpi", 192, 432),
    ]

    for folder, size, fg_size in densities:
        dir_path = os.path.join(base_dir, folder)
        os.makedirs(dir_path, exist_ok=True)

        # Legacy square
        full_scaled = full_icon.resize((size, size), Image.Resampling.LANCZOS)
        full_scaled.save(os.path.join(dir_path, "ic_launcher.png"), "PNG")

        # Legacy round
        round_scaled = round_icon.resize((size, size), Image.Resampling.LANCZOS)
        round_scaled.save(os.path.join(dir_path, "ic_launcher_round.png"), "PNG")

        # Adaptive foreground
        fg_scaled = fg_icon.resize((fg_size, fg_size), Image.Resampling.LANCZOS)
        fg_scaled.save(os.path.join(dir_path, "ic_launcher_foreground.png"), "PNG")

        print(f"Generated {folder}: {size}x{size} and fg {fg_size}x{fg_size}")

if __name__ == "__main__":
    export_android_res()
    print("✓ Todos los recursos de iconos Android generados con fondo blanco y logo V.I.E.R.N.E.S.")
