# %%
# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Import necessary libraries
import pandas as pd
from transformers import RobertaForSequenceClassification, RobertaTokenizer
import torch

# Load the fine-tuned model and tokenizer
model_path = '/content/drive/MyDrive/fine_tuned_model/fine_tuned_model'  # Replace with the actual path
model = RobertaForSequenceClassification.from_pretrained(model_path)
tokenizer = RobertaTokenizer.from_pretrained(model_path)

# Load the CSV file with responses
file_path = '/content/EvaluatedResponses.csv'  # Replace with the actual path
df = pd.read_csv(file_path)

# Define a function to predict if an answer is AI-generated
def detect_ai(text):
    if not isinstance(text, str):  # Check if the input is a string
        return "Invalid input"  # Mark invalid entries
    # Tokenize the text
    inputs = tokenizer(text, return_tensors="pt", padding="max_length", truncation=True, max_length=512)
    inputs = {key: val.to(model.device) for key, val in inputs.items()}

    # Perform inference
    with torch.no_grad():
        outputs = model(**inputs)

    # Get predicted label
    logits = outputs.logits
    predicted_label = torch.argmax(logits, dim=1).item()
    return "AI-generated" if predicted_label == 1 else "Human-generated"

# Apply the detection function to the 'Transcription' column
df['AI detection'] = df['Transcription'].apply(detect_ai)  # Ensure column name matches your CSV

# Save the updated DataFrame to a new CSV file
output_file_path = '/content/drive/My Drive/EvaluatedResponses_with_AIDetection.csv'
df.to_csv(output_file_path, index=False)

print(f"Updated file saved at: {output_file_path}")



