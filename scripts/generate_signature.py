from svgwrite import Drawing
from pathlib import Path
import base64
import subprocess
import os
import subprocess

INKSCAPE_PATH = r"C:\Program Files\Inkscape\bin\inkscape.exe"

def embed_font_base64(font_path):
    with open(font_path, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    font_format = 'truetype' if font_path.endswith('.ttf') else 'opentype'
    return f"data:font/{font_format};base64,{encoded}"

def create_font_signature(name, font_path, output_dir, width=500, height=150, font_size=64):
    font_name = Path(font_path).stem
    font_folder = os.path.join(output_dir, font_name)
    os.makedirs(font_folder, exist_ok=True)

    safe_name = name.lower().replace(" ", "_")
    filename = f"{safe_name}_{font_name}.svg"
    output_path = os.path.join(font_folder, filename)

    font_data_url = embed_font_base64(font_path)

    dwg = Drawing(output_path, size=(f"{width}px", f"{height}px"))

    style = f"""
    @font-face {{
        font-family: '{font_name}';
        src: url('{font_data_url}');
    }}
    text {{
        font-family: '{font_name}';
        font-size: {font_size}px;
        fill: black;
    }}
    """
    dwg.defs.add(dwg.style(style))
    dwg.add(dwg.text(name, insert=(20, height // 2), fill="black"))
    dwg.save()

    print(f"[+] Saved SVG with text: {output_path}")

    try:
        subprocess.run([
            INKSCAPE_PATH,
            output_path,
            "--export-plain-svg",
            "--export-text-to-path",
            "--export-filename=" + output_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Error converting to path with Inkscape: {e}")

