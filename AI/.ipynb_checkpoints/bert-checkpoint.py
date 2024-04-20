from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset
import torch

# Step 1: Prepare the Dataset
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

def load_text(file_name, word_limit=10):
    with open(file_name, 'r', encoding='utf-8') as file:
        text = file.read()
        words = text.split()
        # Group words into chunks of `word_limit`
        chunks = [' '.join(words[i:i + word_limit]) for i in range(0, len(words), word_limit)]
        return chunks       

texts = load_text('maths.txt') + load_text('AI.txt')
labels = [0] * len(load_text('maths.txt')) + [1] * len(load_text('AI.txt'))  # 0 for maths, 1 for AI

# Step 2: Tokenization
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
# print(tokenizer, '-----------' , len(load_text('maths.txt')), len(load_text('AI.txt')), '-----------------', labels)
dataset = TextDataset(tokenizer, texts, labels)

# Step 3: Model Training
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)
training_args = TrainingArguments(output_dir='./results', num_train_epochs=3, per_device_train_batch_size=8)
trainer = Trainer(model=model, args=training_args, train_dataset=dataset)

trainer.train()

# Check the device where the model is loaded
device = model.device


# Step 4: Prediction
new_texts = ["supervised learning", "calculus"]
tokenized_new_text = tokenizer(new_texts, return_tensors="pt", padding=True, truncation=True, max_length=512)
tokenized_new_text = tokenized_new_text.to(device)


label_map = {0: 'Math', 1: 'AI'}  # Update this map according to your labels

with torch.no_grad():
    outputs = model(**tokenized_new_text)
    predictions = torch.argmax(outputs.logits, dim=-1)
    predicted_labels = [label_map[pred.item()] for pred in predictions]

print(predicted_labels)

save_directory = "./model"
model.save_pretrained(save_directory)
tokenizer.save_pretrained(save_directory)

