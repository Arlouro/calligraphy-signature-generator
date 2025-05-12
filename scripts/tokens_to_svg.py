import json
# Removed unused import
import svgwrite

def convert_flat_tokens_to_svg_tokens(flat_tokens):
    if len(flat_tokens) % 2 != 0:
        raise ValueError("[!] Token length must be even (x, y pairs)")

    svg_tokens = []

    for i in range(0, len(flat_tokens), 2):
        x = flat_tokens[i]
        y = flat_tokens[i + 1]
        cmd = "M" if i == 0 else "L"  # Start with MoveTo, then LineTo
        svg_tokens.append([cmd, x, y])

    return svg_tokens

def tokens_to_path_d(tokens):
    path_d = []
    for token in tokens:
        if not isinstance(token, list) or not isinstance(token[0], str):
            raise ValueError(f"[!] Malformed token: expected list starting with str command, got {token}")
        cmd = token[0]
        coords = token[1:]
        path_d.append(cmd + " " + " ".join(str(round(c * 400, 2)) for c in coords))  # scale up
    return " ".join(path_d)

def tokens_to_animated_svg(json_path, output_svg_path="output/generated_signature.svg"):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    tokens = data["tokens"]

    # If flat list, convert
    if tokens and isinstance(tokens[0], float):
        tokens = convert_flat_tokens_to_svg_tokens(tokens)

    d_attr = tokens_to_path_d(tokens)

    dwg = svgwrite.Drawing(output_svg_path, profile='tiny', size=("400px", "200px"))
    path = dwg.path(d=d_attr, fill="none", stroke="black", stroke_width=2)

    # Animate path drawing
    path_length = 1000  # rough estimate, you can make it dynamic
    path.update({"stroke-dasharray": path_length, "stroke-dashoffset": path_length})

    animate = svgwrite.animate.Animate(
        attributeName="stroke-dashoffset",
        from_=str(path_length),
        to="0",
        dur="2s",
        fill="freeze"
    )
    path.add(animate)
    dwg.add(path)
    dwg.save()

    print(f"[✓] Saved animated signature to {output_svg_path}")
