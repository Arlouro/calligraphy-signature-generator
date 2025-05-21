# Signature Generator with Evolutionary Algorithms

## Overview
This project generates stylized handwritten signatures from a given name using evolutionary algorithms. Instead of working with static images or fonts, it represents signatures as vector-based genotypes composed of graphical parameters such as curve points, angles, stroke thickness, and spatial transformations. The program evolves these representations over multiple generations to produce unique, coherent, and legible signatures.

##Features
- Vector-based signature representation for high flexibility and scalability
- Custom fitness function evaluating stroke fluidity, consistency, balance, and continuity

- Genetic algorithm operators: mutation, crossover, and tournament selection

- Integration with an external inference model for legibility verification

- SVG output of evolved signatures and fitness progress plotting

## Requirements
- Python 3.8+

- **Dependencies**:
  - numpy
  - matplotlib
  - pillow
  - fontTools
  - cairosvg
  - inference_sdk (for Roboflow API integration)

### Install dependencies via:

```bash
pip install numpy matplotlib pillow fonttools cairosvg inference_sdk
```

## Configuration
- `FONT_PATH`: Path to the TrueType font used for base chromosome generation.

- `MODEL_ID` and `API_KEY`: Credentials for the external legibility inference API.

- Genetic algorithm parameters (`POPULATION`, `GENERATIONS`, `MUTATION`, `TOURNAMENT`) can be adjusted in the source code.

## Usage
Run the program and input the desired name to generate a signature:

```bash
python signature_generator.py
```
The program will evolve signatures over multiple attempts, saving the best legible signature as `signature.svg`. Debug images are saved if legibility fails.

## Limitations
- Lack of real-world labeled datasets limits supervised training and evaluation.
- Legibility checks depend on an external model and may not be perfect.
- The connection between visual signature and input name remains implicit and could be improved.
