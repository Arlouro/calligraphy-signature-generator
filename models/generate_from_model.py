import json
import torch
from models.vae_model import VAE
from scripts.signature_dataset import SignatureDataset
import os

def generate_signature(model_path="models/vae.pth", dataset_path="data/tokenized_signatures.json", output_path="output/generated_signature.json"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    dataset = SignatureDataset(dataset_path)
    input_dim = dataset[0][0].shape[0]

    model = VAE(input_dim=input_dim, latent_dim=64).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    with torch.no_grad():
        z = torch.randn(1, 64).to(device)
        output = model.decode(z).squeeze(0).cpu().numpy().tolist()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump({"tokens": output}, f, indent=2)

    print(f"[✓] Assinatura gerada e salva em: {output_path}")

if __name__ == "__main__":
    generate_signature()
