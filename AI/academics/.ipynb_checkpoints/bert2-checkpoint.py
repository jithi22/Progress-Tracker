import os
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, TrainingArguments, Trainer
from torch.utils.data import Dataset
import json

def load_texts_and_labels(directory, word_limit=10):
    texts, labels = [], []
    label_map = {}

    for filename in os.listdir(directory)[:3]:
        if filename.endswith('.txt'):
            label = filename.rsplit('.', 1)[0]  # Get the filename without the extension as label
            if label not in label_map:
                label_map[label] = len(label_map)
            label_id = label_map[label]

            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                words = text.split()
                for i in range(0, len(words), word_limit):
                    chunk = ' '.join(words[i:i + word_limit])
                    texts.append(chunk)
                    labels.append(label_id)

    return texts, labels, label_map

class TextDataset(Dataset):
    def __init__(self, tokenizer, texts, labels):
        self.tokenizer = tokenizer
        self.texts = texts
        self.labels = labels

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        tokenized_text = self.tokenizer(self.texts[idx], padding='max_length', truncation=True, max_length=512)
        return {**tokenized_text, 'labels': torch.tensor(self.labels[idx])}

# Assuming the 'store' directory contains your text files
texts, labels, label_map = load_texts_and_labels('store')
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
dataset = TextDataset(tokenizer, texts, labels)

model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=len(label_map))
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=8
)
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset
)

trainer.train()


# Check the device where the model is loaded
device = model.device

# Save the model and tokenizer
model.save_pretrained('./model')
tokenizer.save_pretrained('./model')

# Example of making a prediction
new_text = "testing"
tokenized_new_text = tokenizer(new_text, return_tensors="pt", padding=True, truncation=True, max_length=512)
tokenized_new_text = tokenized_new_text.to(device)

inverse_label_map = {v: k for k, v in label_map.items()}

label_map_path = './model/label_map.json'
with open(label_map_path, 'w', encoding='utf-8') as f:
    json.dump(inverse_label_map, f, ensure_ascii=False, indent=4)
    
with torch.no_grad():
    outputs = model(**tokenized_new_text)
    predictions = torch.argmax(outputs.logits, dim=-1)


predicted_label = inverse_label_map[predictions.item()]

print(predicted_label)
