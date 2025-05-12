import re
import json
import xml.etree.ElementTree as ET
from pathlib import Path

def normalize_coords(coords, width=400, height=200):
    norm = []
    for i in range(0, len(coords) - 1, 2):
        try:
            x = float(coords[i]) / width
            y = float(coords[i + 1]) / height
            norm.extend([x, y])
        except ValueError:
            print(f"[!] Error converting coordinates: {coords[i]}, {coords[i+1]}")
    return norm

def parse_svg_path(d_attr):
    tokens = re.findall(r'[A-Za-z]|-?\d*\.?\d+', d_attr)
    result = []
    i = 0
    while i < len(tokens):
        cmd = tokens[i]
        i += 1
        coords = []
        while i < len(tokens) and re.match(r'-?\d*\.?\d+', tokens[i]):
            coords.append(tokens[i])
            i += 1
        coords = normalize_coords(coords)
        result.append([cmd] + coords)
    return result

def extract_path_d(svg_path):
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]
        path = root.find('.//path')
        if path is None:
            print(f"[!] No path found in {svg_path}")
            return None
        return path.attrib.get('d') if path is not None else None
    except ET.ParseError as e:
        print(f"[!] Error parsing SVG: {svg_path} -> {e}")
        return None

def convert_svg_folder_to_dataset(input_dir, output_file="tokenized_signatures.json"):
    input_dir = Path(input_dir)
    dataset = []
    
    for font_dir in input_dir.iterdir():
        if font_dir.is_dir():
            print(f"[+] Processing font directory: {font_dir.name}")
            for svg_file in font_dir.glob("*.svg"):
                print(f"    [+] Processing SVG file: {svg_file.name}")
                d_attr = extract_path_d(svg_file)
                print(f"        [*] Extracted d attribute: {d_attr}")
                if d_attr:
                    tokens = parse_svg_path(d_attr)
                    sample = {
                        "name": svg_file.stem,
                        "font": font_dir.name,
                        "tokens": tokens
                    }
                    dataset.append(sample)
                else:
                    print(f"    [!] No path found in {svg_file.name}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)
    print(f"[✓] Saved dataset with {len(dataset)} samples to {output_file}")
