from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch

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
    
    # Assuming you have a mapping of indices to labels
    label_map = {0: 'Math', 1: 'AI'}  # Update this according to your actual labels
    predicted_label = label_map[predictions.item()]
    
    print("prediction : ",predicted_label)
