# model_predictor.py
import os
import json
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

def find_model_directory(base_path='.'):
    for root, dirs, files in os.walk(base_path):
        if 'config.json' in files and 'pytorch_model.bin' in files:
            return root
    raise FileNotFoundError("Model directory not found")

def find_category(predicted_label, json_file='academics_tuner.json'):
    # Load the JSON file
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Iterate over each key (which represents a list name) and its list of items
    for some_name, items in data.items():
        # Iterate over the items in the current list
        for item in items:
            # Check if the predicted label matches the title
            if predicted_label == item['title']:
                if some_name == 'default':
                    return predicted_label
                return some_name  # Return the name of the list where the match was found

    return "default"  # Return default message if no match is found

def predict_with_model(texts_to_predict, model_directory=None, tune=False):
    if model_directory is None:
        model_directory = find_model_directory()

    # Load the trained model and tokenizer only once
    model = DistilBertForSequenceClassification.from_pretrained(model_directory)
    tokenizer = DistilBertTokenizer.from_pretrained(model_directory)

    # Tokenize all texts in a batch
    tokenized_batch = tokenizer(texts_to_predict, padding=True, truncation=True, return_tensors="pt", max_length=512)

    # Make a batch prediction
    with torch.no_grad():
        outputs = model(**tokenized_batch)
        predictions = torch.argmax(outputs.logits, dim=-1)

    label_map_path = os.path.join(model_directory, 'label_map.json')    
    # Load the label map for prediction or evaluation
    with open(label_map_path, 'r', encoding='utf-8') as f:
        loaded_label_map = json.load(f)

    # Map prediction integers to labels
    predicted_labels = [loaded_label_map.get(str(prediction), "Label not found") for prediction in predictions.tolist()]

    # Apply tuning if required
    if tune:
        tuner_path = os.path.join(model_directory, 'academics_tuner.json')
        predicted_labels = [find_category(label, json_file=tuner_path) if label != "Label not found" else label for label in predicted_labels]

    return predicted_labels


# This allows you to run a quick test when this script is executed directly
if __name__ == '__main__':
    text = input("Enter text: ")
    print("Prediction:", predict_with_model(text))
