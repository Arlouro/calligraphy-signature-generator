import json
import torch
from torch.utils.data import Dataset

class SignatureDataset(Dataset):
    def __init__(self, json_path):
        with open(json_path, 'r') as f:
            raw_data = json.load(f)

        self.samples = []
        self.max_len = 0
        self.fonts = set()

        for item in raw_data:
            font = item["font"]
            tokens = item["tokens"]
            self.fonts.add(font)
            flattened = []
            for token in tokens:
                flattened.extend(token[1:])
            self.samples.append((flattened, font))
            self.max_len = max(self.max_len, len(flattened))

        self.fonts = sorted(list(self.fonts))
        self.font_to_index = {font: idx for idx, font in enumerate(self.fonts)}
        self.num_fonts = len(self.fonts)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        tokens, font = self.samples[idx]
        # Padding
        padded = tokens + [0.0] * (self.max_len - len(tokens))
        x = torch.tensor(padded, dtype=torch.float32)
        c = torch.nn.functional.one_hot(
            torch.tensor(self.font_to_index[font]), num_classes=self.num_fonts
        ).float()
        return x, c
