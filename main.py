import svgwrite
import numpy as np

def generate_signature_points(seed=42):
    np.random.seed(seed)
    
    base_x = np.linspace(0, 300, num=6)
    base_y = 100 + np.random.randn(6) * 30

    points = list(zip(base_x, base_y))
    return points

def create_svg_signature(filename="signature.svg", stroke_width=2, stroke_color="#ffffff"):
    points = generate_signature_points()

    dwg = svgwrite.Drawing(filename, size=("400px", "200px"))
    path_data = f"M {points[0][0]},{points[0][1]} "

    # Draw quadratic or cubic Bézier curves between points
    for i in range(1, len(points) - 2, 2):
        cp1 = points[i]
        cp2 = points[i+1]
        end = points[i+2]
        path_data += f"C {cp1[0]},{cp1[1]} {cp2[0]},{cp2[1]} {end[0]},{end[1]} "

    signature_path = dwg.path(d=path_data,
                              stroke=stroke_color,
                              fill="none",
                              stroke_width=stroke_width,
                              stroke_linecap="round",
                              stroke_linejoin="round")
    dwg.add(signature_path)
    dwg.save()
    print(f"Signature saved as {filename}")

if __name__ == "__main__":
    create_svg_signature()
