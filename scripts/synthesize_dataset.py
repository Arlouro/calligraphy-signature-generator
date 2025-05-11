import os
import json
from pathlib import Path  
from scripts.generate_signature import create_font_signature

def synthesize_dataset(names, font_dir="fonts", output_dir="data/signatures", label_file="data/labels.json"):
    os.makedirs(output_dir, exist_ok=True)  
    font_paths = list(Path(font_dir).glob("*.ttf"))  

    name_to_file = {}  

    for name in names:
        for font_path in font_paths:
            create_font_signature(name, str(font_path), output_dir)
            
            font_name = Path(font_path).stem
            safe_name = name.lower().replace(" ", "_")
            filename = f"{safe_name}_{font_name}.svg"
            name_to_file[f"{name}_{font_name}"] = os.path.join(output_dir, font_name, filename)

    with open(label_file, "w") as f:
        json.dump(name_to_file, f, indent=2)

    print(f"[✓] Dataset generation complete. Labels saved to {label_file}")
