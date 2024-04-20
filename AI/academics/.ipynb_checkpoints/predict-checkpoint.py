from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch
import json 
# Load the trained model and tokenizer
model_directory = "./model"
model = DistilBertForSequenceClassification.from_pretrained(model_directory)
tokenizer = DistilBertTokenizer.from_pretrained(model_directory)


while True:
# Prepare the text for prediction
    text_to_predict = input("Enter text : ")
    tokenized_text = tokenizer(text_to_predict, return_tensors="pt", truncation=True, max_length=512)
    
    # Make a prediction
    with torch.no_grad():
        outputs = model(**tokenized_text)
        predictions = torch.argmax(outputs.logits, dim=-1)
        
    label_map_path = './model/label_map.json'    
    # To load the label map later for prediction or evaluation
    with open(label_map_path, 'r', encoding='utf-8') as f:
        loaded_label_map = json.load(f)

    # # Invert the label map to map integers to labels
    # inverse_label_map = {v: k for k, v in loaded_label_map.items()}
    
    # Use the prediction integer to get the label
    predicted_label = loaded_label_map.get(str(predictions.item()))
    

    
    print(loaded_label_map, predictions.item())

    
    print("prediction : ", predicted_label)

