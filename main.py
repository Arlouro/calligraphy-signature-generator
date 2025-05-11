from scripts.synthesize_dataset import synthesize_dataset
from scripts.SVG_to_token import convert_svg_folder_to_dataset

if __name__ == "__main__":
    sample_names = [
        "John Doe", "Alice Smith", "Bob Marley",
        "Jane Austen", "Michael Jordan", "Serena Williams"
    ]
    #synthesize_dataset(sample_names)
    convert_svg_folder_to_dataset("data/signatures", "data/tokenized_signatures.json")
