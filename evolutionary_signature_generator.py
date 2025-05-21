import os
import random
import uuid
import math
import numpy as np
from io import BytesIO
import xml.etree.ElementTree as ET
from xml.dom import minidom
import matplotlib.pyplot as plt
from inference_sdk import InferenceHTTPClient
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from PIL import Image

# ==== CONFIGURATION ====
FONT_PATH = "fonts/Bastliga One.ttf"
MODEL_ID = "doctors-handwritten-recognition/2"
API_KEY = "tSOyBot6l990FV1g9HRI"

# ==== UTILITY FUNCTIONS ====
def svg_to_image(svg_str):
    try:
        import cairosvg
    except ImportError:
        raise ImportError("cairosvg is required for SVG to image conversion. Please install it with 'pip install cairosvg'.")

    try:
        png_data = cairosvg.svg2png(bytestring=svg_str.encode("utf-8"), output_width=500, output_height=200)
        image = Image.open(BytesIO(png_data)).convert("RGBA")
        background = Image.new("RGBA", image.size, (255, 255, 255, 255))
        image = Image.alpha_composite(background, image)
        return image.convert("RGB")
    except Exception as e:
        raise RuntimeError(f"Failed to convert SVG to image: {e}")

def save_temp_image(image, directory="tmp"):
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"temp_{uuid.uuid4().hex[:8]}.png")
    image.save(path)
    return path

def plot_fitness(history):
    plt.plot(history, label='Average Fitness')
    plt.title("Fitness Evolution")
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.grid(True)
    plt.legend()
    plt.savefig("fitness_plot.png")

# ==== FONT-BASED INITIAL CHROMOSOME ====
def generate_from_font(name, font_path=FONT_PATH, font_size=100):
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font not found: {font_path}")

    font = TTFont(font_path)
    glyph_set = font.getGlyphSet()
    recording_pen = RecordingPen()

    x_cursor = 0
    letters = []

    for char in name:
        glyph_name = font.getBestCmap().get(ord(char))
        if not glyph_name:
            continue

        glyph = glyph_set[glyph_name]
        recording_pen.value = []
        glyph.draw(recording_pen)

        points = []
        for cmd, pts in recording_pen.value:
            for pt in pts:
                x = pt[0] * (font_size / 1000.0) + x_cursor
                y = -pt[1] * (font_size / 1000.0) + font_size
                points.append((x, y))

        if points:
            letters.append(points)
            x_cursor += font_size * 0.6

    return letters

# ==== FITNESS EVALUATION ====
def calculate_fitness(chromosome):
    def stroke_fluidity():
        """Measures how fluid the strokes appear"""
        angles = []
        for letter in chromosome:
            for i in range(len(letter) - 2):
                a, b, c = letter[i], letter[i+1], letter[i+2]
                v1 = np.subtract(b, a)
                v2 = np.subtract(c, b)
                mag1 = np.linalg.norm(v1)
                mag2 = np.linalg.norm(v2)
                if mag1 > 1e-6 and mag2 > 1e-6:
                    angle = math.acos(np.clip(np.dot(v1, v2) / (mag1 * mag2), -1, 1))
                    angles.append(angle)
        return 1.0 - (np.mean(angles)/math.pi if angles else 0.5)
    
    def stroke_consistency():
        """Measures consistency of stroke widths and spacing"""
        if len(chromosome) < 2:
            return 0.5
            
        letter_sizes = []
        for letter in chromosome:
            if len(letter) < 2:
                continue
            xs = [p[0] for p in letter]
            ys = [p[1] for p in letter]
            width = max(xs) - min(xs)
            height = max(ys) - min(ys)
            letter_sizes.append((width, height))
        
        if not letter_sizes:
            return 0.5
            
        avg_width = np.mean([w for w, h in letter_sizes])
        avg_height = np.mean([h for w, h in letter_sizes])
        width_std = np.std([w/avg_width for w, h in letter_sizes]) if avg_width > 0 else 1
        height_std = np.std([h/avg_height for w, h in letter_sizes]) if avg_height > 0 else 1
        
        return 1.0 - (width_std + height_std)/2
    
    def signature_balance():
        """Measures overall visual balance of the signature"""
        all_points = [point for letter in chromosome for point in letter]
        if not all_points:
            return 0.5
            
        center_x = sum(p[0] for p in all_points)/len(all_points)
        center_y = sum(p[1] for p in all_points)/len(all_points)
        
        distance_from_center = math.sqrt((center_x-250)**2 + (center_y-100)**2)
        normalized_distance = min(distance_from_center/100, 1.0)
        
        return 1.0 - normalized_distance
    
    def continuity_score():
        """Measures how continuous the strokes are"""
        continuity = 0
        for letter in chromosome:
            if len(letter) < 2:
                continue
            for i in range(len(letter) - 1):
                p1, p2 = letter[i], letter[i + 1]
                continuity += np.linalg.norm(np.subtract(p2, p1))
        return min(continuity / (len(chromosome) * 100), 1.0)
    
    return (
        0.4 * stroke_fluidity() +
        0.3 * stroke_consistency() +
        0.2 * signature_balance() +
        0.1 * continuity_score()
    )

# ==== ROBOFLOW LEGIBILITY CHECK ====
client = InferenceHTTPClient(api_url="https://serverless.roboflow.com", api_key=API_KEY)

def is_legible(svg, name):
    image = svg_to_image(svg)
    image_path = save_temp_image(image)
    try:
        result = client.infer(image_path, model_id=MODEL_ID)
        preds = result.get("predictions", [])
        recognized = {p.get("class", "").lower() for p in preds}
        name_letters = set(name.lower())
        return len(name_letters & recognized) >= max(1, len(name)//3), image
    except Exception as e:
        print(f"[ERROR] Legibility check failed: {e}")
        return False, image

# ==== EVOLUTIONARY GENERATOR ====
class SignatureGenerator:
    def __init__(self, name):
        self.name = name
        self.population_size = 60
        self.generations = 5
        self.mutation_rate = 0.5
        self.fitness_history = []
        self.population = []
        self.best_chrom = None
        self.best_fit = -float('inf')
        self.base_chromosome = generate_from_font(self.name)
        self.tournament_k = 3


    def mutate(self, chrom):
        mutated = []
        slant_angle = random.gauss(0, 0.12)  # radians, subtle slant
        baseline_shift = random.gauss(0, 2.5)
        for letter in chrom:
            new_letter = []
            for i, (x, y) in enumerate(letter):
                mutation_factor = 1 - (i / len(letter))
                # Smooth noise for more natural curves
                dx = random.gauss(0, 0.7) * mutation_factor * 1.2
                dy = random.gauss(0, 0.7) * mutation_factor * 1.2
                # Apply slant and baseline
                nx = x + dx + (y * math.tan(slant_angle))
                ny = y + dy + baseline_shift
                new_letter.append((nx, ny))
            mutated.append(new_letter)
        return mutated
    
    def tournament_selection(self, k=3):
        participants = random.sample(list(zip(self.population, [calculate_fitness(ind) for ind in self.population])), k)
        winner = max(participants, key=lambda x: x[1])
        return winner[0]


    def crossover(self, p1, p2):
        if len(p1) < 2 or len(p2) < 2:
            return p1
        cut = random.randint(1, min(len(p1), len(p2)) - 1)
        return p1[:cut] + p2[cut:]

    def evolve(self, additional_generations=None):
        if not self.population:
            self.population = [self.mutate(self.base_chromosome) for _ in range(self.population_size)]
        
        gens = additional_generations if additional_generations is not None else self.generations
        for gen in range(gens):
            gen_num = len(self.fitness_history)
            self.mutation_rate = max(0.05, 0.2 * (1 - gen_num / (self.generations + 100)))  # Dynamic adjustment

            scores = [calculate_fitness(ind) for ind in self.population]
            avg_fit = sum(scores) / len(scores)
            self.fitness_history.append(avg_fit)

            elite_size = max(1, int(self.population_size * 0.1))
            elite_indices = np.argsort(scores)[-elite_size:]
            new_pop = [self.population[i] for i in elite_indices]

            while len(new_pop) < self.population_size:
                p1 = self.tournament_selection(k=self.tournament_k)
                p2 = self.tournament_selection(k=self.tournament_k)
                child = self.crossover(p1, p2)
                if random.random() < self.mutation_rate:
                    child = self.mutate(child)
                new_pop.append(child)

            self.population = new_pop
            current_best = max(zip(self.population, scores), key=lambda x: x[1])
            if current_best[1] > self.best_fit:
                self.best_chrom, self.best_fit = current_best

            print(f"Gen {gen_num:03} | Best Fit: {self.best_fit:.4f} | Avg: {avg_fit:.4f} | Mut Rate: {self.mutation_rate:.2f}")

        svg = self.chromosome_to_svg(self.best_chrom)
        return svg, self.best_chrom


    def chromosome_to_svg(self, chromosome):
        svg = ET.Element('svg', xmlns="http://www.w3.org/2000/svg", 
                        width="500", height="200", viewBox="0 0 500 200")
        ET.SubElement(svg, 'rect', x="0", y="0", width="500", height="200", 
                    fill="#f8f8f8", rx="5")
        g = ET.SubElement(svg, 'g', stroke="#222", 
                        **{"stroke-width": "3.5", 
                            "fill": "none", 
                            "stroke-linecap": "round", 
                            "stroke-linejoin": "round"})
        
        for letter in chromosome:
            if len(letter) < 4:
                continue
            path = ET.SubElement(g, 'path')
            d = [f"M {letter[0][0]:.2f},{letter[0][1]:.2f}"]
            for c1, c2, end in catmull_rom_to_bezier(letter):
                d.append(f"C {c1[0]:.2f},{c1[1]:.2f} {c2[0]:.2f},{c2[1]:.2f} {end[0]:.2f},{end[1]:.2f}")
            path.set('d', ' '.join(d))
            # Add subtle shadow effect
            path.set('filter', 'url(#shadow)')
        
        # Add SVG filter for subtle shadow
        defs = ET.SubElement(svg, 'defs')
        shadow = ET.SubElement(defs, 'filter', id="shadow", x="-20%", y="-20%", width="140%", height="140%")
        ET.SubElement(shadow, 'feGaussianBlur', stdDeviation="2")
        
        return minidom.parseString(ET.tostring(svg)).toprettyxml()

def catmull_rom_to_bezier(points):
    bezier_points = []
    n = len(points)
    for i in range(n - 1):
        p0 = points[i - 1] if i - 1 >= 0 else points[i]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[i + 2] if i + 2 < n else points[i + 1]

        c1 = (
            p1[0] + (p2[0] - p0[0]) / 6.0,
            p1[1] + (p2[1] - p0[1]) / 6.0
        )
        c2 = (
            p2[0] - (p3[0] - p1[0]) / 6.0,
            p2[1] - (p3[1] - p1[1]) / 6.0
        )
        bezier_points.append((c1, c2, p2))
    return bezier_points

# ==== MAIN ====
if __name__ == "__main__":
    name = input("Enter a name to generate a signature for: ").strip()
    gen = SignatureGenerator(name)

    for attempt in range(10):
        print(f"\n🧬 Attempt {attempt+1}...")
        svg, chrom = gen.evolve(additional_generations=30)
        valid, img = is_legible(svg, name)

        if valid:
            with open("signature.svg", "w", encoding="utf-8") as f:
                f.write(svg)
            plot_fitness(gen.fitness_history)
            print("✅ Signature is legible and saved as 'signature.svg'")
            break
        else:
            img.save(f"debug_signature_{attempt+1}.png")
            print("❌ Not legible, evolving further...")
    else:
        print("❗ Failed to evolve a legible signature after 10 attempts.")
