import svgwrite
import numpy as np

def generate_signature_points(seed=42):
    np.random.seed(seed)
    
    base_x = np.linspace(0, 300, num=6)
    base_y = 100 + np.random.randn(6) * 30

    points = list(zip(base_x, base_y))
    return points

def catmull_rom_to_bezier(points):
    result = []
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
        result.append((p1, cp1, cp2, p2))
    return result

def create_svg_signature(filename="signature_smooth.svg", color="#FFFFFF"):
    points = generate_signature_points()
    segments = catmull_rom_to_bezier(points)

    dwg = svgwrite.Drawing(filename, size=("400px", "200px"))
    path_data = f"M {segments[0][0][0]},{segments[0][0][1]} "
    
    for p1, cp1, cp2, p2 in segments:
        path_data += f"C {cp1[0]},{cp1[1]} {cp2[0]},{cp2[1]} {p2[0]},{p2[1]} "

    path = dwg.path(d=path_data, stroke=color, fill="none", stroke_width=2, stroke_linecap="round", stroke_linejoin="round")
    dwg.add(path)
    dwg.save()
    print(f"Signature saved as {filename}")


if __name__ == "__main__":
    create_svg_signature()
