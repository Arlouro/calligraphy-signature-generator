from scripts.synthesize_dataset import synthesize_dataset
from scripts.SVG_to_token import convert_svg_folder_to_dataset

if __name__ == "__main__":
    sample_names = [
        "Alice Smith", "Bob Marley", "Charlie Brown", "David Bowie", "Eva Green",
        "Frida Kahlo", "George Washington", "Hannah Montana", "Isabel Allende", "Jackie Chan",
        "Kurt Cobain", "Leonardo da Vinci", "Maria Curie", "Nikola Tesla", "Oscar Wilde",
        "Paul McCartney", "Quincy Jones", "Rosa Parks", "Steve Jobs", "Tim Berners-Lee",
        "Ursula K. Le Guin", "Vincent van Gogh", "Walt Disney", "Xena Warrior Princess", "Yoko Ono",
        "Zadie Smith"
    ]
    synthesize_dataset(sample_names)
    convert_svg_folder_to_dataset("data/signatures", "data/tokenized_signatures.json")
