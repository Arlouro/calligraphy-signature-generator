import svgwrite
import numpy as np

# np.random.seed(0)

def generate_signature_points(num_points=10, width=400, height=200):
    points = []
    spacing = width / (num_points - 1)
    for i in range(num_points):
        x = i * spacing
        y = height / 2 + np.random.uniform(-30, 30)
        points.append((x, y))
    return points

def catmull_rom_to_bezier(points):
    beziers = []
    for i in range(1, len(points) - 2):
        p0, p1, p2, p3 = points[i-1:i+3]
        cp1 = (
            p1[0] + (p2[0] - p0[0]) / 6,
            p1[1] + (p2[1] - p0[1]) / 6
        )
        cp2 = (
            p2[0] - (p3[0] - p1[0]) / 6,
            p2[1] - (p3[1] - p1[1]) / 6
        )
        beziers.append((p1, cp1, cp2, p2))
    return beziers

def create_svg_signature(filename="signature.svg", width=400, height=200, animate=False):
    points = generate_signature_points()
    segments = catmull_rom_to_bezier(points)

    dwg = svgwrite.Drawing(filename, size=(f"{width}px", f"{height}px"))
    
    path_data = f"M {segments[0][0][0]},{segments[0][0][1]} "
    for p1, cp1, cp2, p2 in segments:
        path_data += f"C {cp1[0]},{cp1[1]} {cp2[0]},{cp2[1]} {p2[0]},{p2[1]} "

    path = dwg.path(
        d=path_data,
        stroke="#ffffff",
        fill="none",
        stroke_width=2,
        stroke_linecap="round",
        stroke_linejoin="round",
        id="signaturePath"
    )
    dwg.add(path)

    if animate:
        path_length = 10000
        path.update({
            'stroke-dasharray': path_length,
            'stroke-dashoffset': path_length,
        })
        animate_tag = svgwrite.animate.Animate(
            attributeName="stroke-dashoffset",
            from_=str(path_length),
            to="0",
            dur="2s",
            fill="freeze",
            begin="0s"
        )
        path.add(animate_tag)

    dwg.save()
    print(f"Signature saved to: {filename}")

if __name__ == "__main__":
    create_svg_signature("stylized_signature.svg", animate=True)
