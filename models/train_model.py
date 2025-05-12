import torch
from torch import nn, optim
from torch.utils.data import DataLoader
from models.vae_model import VAE
from scripts.signature_dataset import SignatureDataset

def loss_function(recon_x, x, mu, logvar):
    BCE = nn.functional.mse_loss(recon_x, x, reduction='sum')
    KLD = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    return BCE + KLD

def train():
    dataset = SignatureDataset('data/tokenized_signatures.json')
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

    input_dim = dataset[0][0].shape[0]
    model = VAE(input_dim=input_dim, latent_dim=64)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    epochs = 50

    for epoch in range(epochs):
        model.train()
        train_loss = 0
        for x, _ in dataloader:
            x = x.to(device)
            optimizer.zero_grad()
            recon_x, mu, logvar = model(x)
            loss = loss_function(recon_x, x, mu, logvar)
            loss.backward()
            train_loss += loss.item()
            optimizer.step()
        print(f"Epoch {epoch+1}/{epochs}, Loss: {train_loss / len(dataset):.4f}")

    torch.save(model.state_dict(), 'models/vae.pth')
    print("[✓] Modelo treinado e guardado em: models/vae.pth")

if __name__ == "__main__":
    train()
