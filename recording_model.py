#!/usr/bin/env python
# coding: utf-8

# In[3]:


#new code that i am working on 
# COMBINED CODE
import pyaudio
import wave
import speech_recognition as sr
import sqlite3
from datetime import datetime
import pyttsx3
import csv
import random
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
import json
import cv2
import time
import threading
import os
import pandas as pd
from transformers import pipeline, RobertaTokenizer, RobertaForSequenceClassification
from sentence_transformers import SentenceTransformer, util
import time

#def initialize_models():
#    """Initialize all required models and pipelines."""
#    models = {
#        'roberta_model': RobertaForSequenceClassification.from_pretrained('/content/drive/MyDrive/fine_tuned_model/fine_tuned_model'),
#        'roberta_tokenizer': RobertaTokenizer.from_pretrained('/content/drive/MyDrive/fine_tuned_model/fine_tuned_model')
#    }
#    return models


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom JSON Encoder to handle numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.generic):  # Check if the object is a numpy type
            return obj.item()  # Convert to native Python type (e.g., float32 -> float)
        return super(NumpyEncoder, self).default(obj)

# Load BERT model and tokenizer for paraphrase detection
class ParaphraseDetector:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def get_embeddings(self, sentences):
        inputs = self.tokenizer(sentences, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy()

    def detect_paraphrase(self, reference_answers, user_answer):
        embeddings_ref = self.get_embeddings(reference_answers)
        embedding_user = self.get_embeddings([user_answer])[0]
        similarities = cosine_similarity(embeddings_ref, [embedding_user])
        max_similarity = np.max(similarities)
        return float(max_similarity)  # Ensure it returns a float value

# Anti-cheating detection function with adjusted gaze deviation sensitivity
def detect_anti_cheating(video_duration=30, face_cascade_path="haarcascade_frontalface_default.xml", eye_cascade_path="haarcascade_eye.xml"):
    # Initialize variables
    cheating_detected = False
    cheating_reason = ""

    # Load Haar cascades for face and eye detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + face_cascade_path)
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + eye_cascade_path)

    # Initialize video capture
    cap = cv2.VideoCapture(0)  # 0 is the default camera index
    start_time = time.time()
    no_face_count = 0  # Count of consecutive frames with no face detected
    no_gaze_count = 0  # Count of consecutive frames with improper gaze detected

    logging.info("Starting video anti-cheating detection...")

    while time.time() - start_time < video_duration:
        ret, frame = cap.read()
        if not ret:
            logging.warning("Failed to capture video frame.")
            break

        # Convert frame to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Analyze face detection results
        if len(faces) == 0:
            no_face_count += 1
        else:
            no_face_count = 0  # Reset if a face is detected

        # If multiple faces are detected, flag as cheating
        if len(faces) > 1 and not cheating_detected:
            cheating_detected = True
            cheating_reason = "Multiple faces detected."
            log_cheating(cheating_reason)
            logging.warning(cheating_reason)
            break

        gaze_deviation_detected = False  # Flag for gaze deviation detection

        # Proceed with gaze checking only if exactly one face is detected
        if len(faces) == 1:
            for (x, y, w, h) in faces:
                roi_gray = gray[y:y + h, x:x + w]
                roi_color = frame[y:y + h, x:x + w]
                eyes = eye_cascade.detectMultiScale(roi_gray)

                # Detect gaze direction based on eye position
                if len(eyes) >= 2:  # Ensure at least two eyes are detected
                    eye_centers = []
                    for (ex, ey, ew, eh) in eyes[:2]:  # Process up to two eyes
                        eye_center_x = x + ex + ew // 2
                        eye_centers.append(eye_center_x)

                    # Check if gaze is within the frame center (adjusted threshold for deviation)
                    frame_center_x = frame.shape[1] // 2
                    if any(abs(center - frame_center_x) > 150 for center in eye_centers):  # Increased threshold for gaze deviation
                        no_gaze_count += 1
                        gaze_deviation_detected = True
                    else:
                        no_gaze_count = 0  # Reset if proper gaze is detected

        # If no face detected for an extended period
        if no_face_count > 50 and not cheating_detected:  # Approximately 2 seconds at 25 fps
            cheating_detected = True
            cheating_reason = "No face detected for extended period."
            log_cheating(cheating_reason)
            logging.warning(cheating_reason)
            break

        # If gaze is deviating from the screen for an extended period
        if gaze_deviation_detected:
            no_gaze_count += 1  # Increase the count for gaze deviation
        else:
            no_gaze_count = 0  # Reset if gaze is within the center

        if no_gaze_count > 50 and not cheating_detected:  # Approximately 2 seconds at 25 fps
            cheating_detected = True
            cheating_reason = "Gaze deviated from the screen for extended period."
            log_cheating(cheating_reason)
            logging.warning(cheating_reason)
            break

        # Display the video feed with detections
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.imshow("Anti-Cheating Detection", frame)

        # Press 'q' to exit early
        if cv2.waitKey(1) & 0xFF == ord('q'):
            logging.info("Video anti-cheating detection ended by user.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if cheating_detected:
        logging.error("Cheating detected during the interview.")
        speak(f"Cheating behavior detected. Reason: {cheating_reason}")
    else:
        logging.info("No cheating detected.")
        speak("Anti-cheating detection completed successfully.")

    return cheating_detected, cheating_reason


# Function to create the database and table (only creates if it doesn't exist)
def create_db():
    conn = sqlite3.connect('interviewBot.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS responses (
                        id INTEGER PRIMARY KEY,
                        filename TEXT,
                        question TEXT,
                        timestamp TEXT,
                        transcription TEXT,
                        similarity_score REAL,
                        conciseness_score REAL,
                        engagement_score REAL,
                        technical_depth_score REAL,
                        analytical_skills_score REAL,
                        soft_skills_score REAL,
                        learning_potential_score REAL,
                        relevance_score REAL,
                        accuracy_score REAL,
                        confidence_score REAL,
                        clarity_score REAL,
                        adaptability_score REAL,
                        grammar_score REAL,
                        overall_score REAL,
                        feedback TEXT,
                        cheating_detected TEXT,
                        cheating_reason TEXT)''')
    conn.commit()
    conn.close()

def update_table_schema():
    conn = sqlite3.connect('interviewBot.db')
    cursor = conn.cursor()

    # Add missing columns if they do not exist
    columns_to_add = [
        ("conciseness_score", "REAL"),
        ("engagement_score", "REAL"),
        ("technical_depth_score", "REAL"),
        ("analytical_skills_score", "REAL"),
        ("soft_skills_score", "REAL"),
        ("learning_potential_score", "REAL"),
        ("relevance_score", "REAL"),
        ("accuracy_score", "REAL"),
        ("confidence_score", "REAL"),
        ("clarity_score", "REAL"),
        ("adaptability_score", "REAL"),
        ("grammar_score", "REAL"),
        ("overall_score", "REAL"),
        ("cheating_detected", "TEXT"),  # New column for cheating detection
        ("cheating_reason", "TEXT")     # New column for cheating reason
    ]

    for column_name, column_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE responses ADD COLUMN {column_name} {column_type}")
            logging.info(f"Column '{column_name}' added successfully.")
        except sqlite3.OperationalError:
            logging.warning(f"Column '{column_name}' already exists.")

    conn.commit()
    conn.close()

# Call the function to update the schema
update_table_schema()

# Function to save metadata, including cheating detection information
def save_metadata(filename, question, transcription, evaluation_scores, feedback, cheating_detected, cheating_reason):
    conn = sqlite3.connect('interviewBot.db')
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Serialize feedback to a JSON string before saving it
    feedback_json = json.dumps(feedback, cls=NumpyEncoder)

    cursor.execute('''INSERT INTO responses (filename, question, timestamp, transcription, similarity_score,
                      conciseness_score, engagement_score, technical_depth_score,
                      analytical_skills_score, soft_skills_score, learning_potential_score, relevance_score, 
                      accuracy_score, confidence_score, clarity_score, adaptability_score, 
                      grammar_score, overall_score, feedback, cheating_detected, cheating_reason)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (filename, question, timestamp, transcription, evaluation_scores['similarity_score'],
                    evaluation_scores['conciseness_score'], evaluation_scores['engagement_score'],
                    evaluation_scores['technical_depth_score'],
                    evaluation_scores['analytical_skills_score'], evaluation_scores['soft_skills_score'],
                    evaluation_scores['learning_potential_score'], evaluation_scores['relevance_score'],
                    evaluation_scores['accuracy_score'], evaluation_scores['confidence_score'], 
                    evaluation_scores['clarity_score'], evaluation_scores['adaptability_score'], 
                    evaluation_scores['grammar_score'], evaluation_scores['overall_score'],
                    feedback_json, "False" if not cheating_detected else "True", cheating_reason))
    conn.commit()
    conn.close()

# Function to export data to CSV with accurate 'cheating_detected' and 'cheating_reason' mapping
def export_to_csv(csv_filename="EvaluatedResponses.csv"):
    conn = sqlite3.connect('interviewBot.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, filename, question, timestamp, transcription, similarity_score, "
                   "conciseness_score, engagement_score, technical_depth_score, "
                   "analytical_skills_score, soft_skills_score, learning_potential_score, relevance_score, "
                   "accuracy_score, confidence_score, clarity_score, adaptability_score, "
                   "grammar_score, overall_score, feedback, "
                   "cheating_detected, cheating_reason FROM responses")
    rows = cursor.fetchall()

    headers = ["ID", "Filename", "Question", "Timestamp", "Transcription", "Similarity Score",
               "Conciseness Score", "Engagement Score", "Technical Depth Score",
               "Analytical Skills Score", "Soft Skills Score", "Learning Potential Score", "Relevance Score",
               "Accuracy Score", "Confidence Score", "Clarity Score", "Adaptability Score",
               "Grammar Score", "Overall Score", "Feedback", "Cheating Detected", "Cheating Reason"]

    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for row in rows:
            row_with_feedback = list(row)
            feedback_json = row_with_feedback[-3]  # The feedback column is now the 3rd to last column

            try:
                feedback_dict = json.loads(feedback_json)
                row_with_feedback[-3] = feedback_dict
            except (json.JSONDecodeError, TypeError):
                row_with_feedback[-3] = {}

            # Correctly handle the cheating information
            cheating_detected = row_with_feedback[-2]  # Directly use the saved value
            cheating_reason = row_with_feedback[-1] if row_with_feedback[-1] else ""

            # Update only the relevant fields in CSV
            row_with_feedback.extend([cheating_detected, cheating_reason])
            writer.writerow(row_with_feedback)

    conn.close()
    logging.info(f"Data successfully exported to {csv_filename}.")


def record_audio(filename="output.wav", silence_threshold=500, silence_duration=5, channels=1, rate=44100, chunk=1024):
    """
    Records audio until silence is detected for a specified duration.

    Parameters:
    - filename: Output WAV file name.
    - silence_threshold: Volume threshold to consider as silence (int, typical range: 100-1000).
    - silence_duration: Time in seconds of continuous silence to stop recording.
    - channels: Number of audio channels (1 for mono, 2 for stereo).
    - rate: Sampling rate (default is 44100 Hz).
    - chunk: Size of audio chunks (default is 1024).

    Returns:
    - The name of the saved audio file, or None if no audio device is found.
    """
    audio = pyaudio.PyAudio()
    input_device_index = None

    # Find an input device
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            input_device_index = i
            break

    if input_device_index is None:
        logging.error("No input audio devices found.")
        return None

    stream = audio.open(format=pyaudio.paInt16, channels=channels, rate=rate, input=True, frames_per_buffer=chunk,
                        input_device_index=input_device_index)
    logging.info("Recording...")
    frames = []
    silence_start = None

    while True:
        data = stream.read(chunk)
        frames.append(data)

        # Convert audio data to numpy array and calculate volume
        audio_data = np.frombuffer(data, dtype=np.int16)
        volume = np.abs(audio_data).mean()

        # Check for silence
        if volume < silence_threshold:
            if silence_start is None:
                silence_start = time.time()  # Mark the start of silence
            elif time.time() - silence_start >= silence_duration:
                logging.info("Silence detected. Stopping recording.")
                break  # Stop recording after 5 seconds of silence
        else:
            silence_start = None  # Reset silence timer if non-silent audio is detected

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded audio to a WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))

    logging.info(f"Audio saved to {filename}")
    return filename


# Function to convert speech to text
def convert_to_text(audio_file):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file) as source:
            logging.info("Converting audio to text...")
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        logging.info("Conversion complete.")
        return text

    except sr.UnknownValueError:
        logging.warning("Speech not recognized.")
        return "Speech not recognized."
    except sr.RequestError as e:
        logging.error(f"Could not request results from Google Speech Recognition service; {e}")
        return f"Error: {e}"

# Function to make the bot speak
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Function to load the dataset (CSV file)
def load_dataset(filename="dataset.csv"):
    questions = []
    with open(filename, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            questions.append({
                "question": row["Question"],
                "answer": row["Answer"],
                "difficulty": row["Difficulty"]
            })
    return questions

# Function to ask how many questions to ask and return the selected number
def get_number_of_questions():
    try:
        num_questions = int(input("How many questions would you like to be asked? "))
        return num_questions
    except ValueError:
        logging.error("Invalid input. Please enter a number.")
        return get_number_of_questions()

def log_cheating(reason):
    """Logs the cheating reason to a CSV file."""
    with open("EvaluatedResponses.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Cheating detected", reason])

# Function to evaluate responses based on similarity, feedback, and completeness
def evaluate_response(transcription, reference_answer):
    if not transcription.strip():  # Check if transcription is empty or just spaces
        return {"similarity_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    similarity_score = ParaphraseDetector().detect_paraphrase([reference_answer], transcription)
    feedback = {"similarity_score": similarity_score,
                "feedback": "Good answer!" if similarity_score > 0.7 else "The answer could be more precise."}
    return feedback

# Additional evaluation functions for multi-dimensional skills
def evaluate_conciseness(transcription):
    if not transcription.strip():  # Check if transcription is empty or just spaces
        return {"conciseness_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    word_count = len(transcription.split())
    if word_count < 5:
        return {"conciseness_score": 1.0, "feedback": "The response is very concise, but might lack detail."}
    elif word_count < 20:
        return {"conciseness_score": 0.8, "feedback": "The response is concise and to the point."}
    else:
        return {"conciseness_score": 0.5, "feedback": "The response is verbose. Try to make it more concise."}

def evaluate_engagement(transcription):
    if not transcription.strip():  # Check if transcription is empty or just spaces
        return {"engagement_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    # Sentiment analysis approach
    engagement_keywords = ["excited", "happy", "passionate", "enthusiastic"]
    if any(word in transcription.lower() for word in engagement_keywords):
        return {"engagement_score": 0.9, "feedback": "The response is engaging and enthusiastic."}

    return {"engagement_score": 0.6, "feedback": "The response could be more engaging with positive tone or structured flow."}

def evaluate_technical_depth(transcription, reference_answers):
    if not transcription.strip():  # Check if transcription is empty or just spaces
        return {"technical_depth_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    similarity_score = ParaphraseDetector().detect_paraphrase(reference_answers, transcription)
    if similarity_score > 0.8:
        return {"technical_depth_score": 1.0, "feedback": "Excellent technical depth."}
    elif similarity_score > 0.6:
        return {"technical_depth_score": 0.7, "feedback": "Good technical depth but could be more precise."}
    else:
        return {"technical_depth_score": 0.4, "feedback": "The response lacks sufficient technical depth."}

def evaluate_analytical_skills(transcription):
    if not transcription.strip():  # Check if transcription is empty or just spaces
        return {"analytical_skills_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    # Check for logical words
    analytical_keywords = ["therefore", "because", "hence", "consequently"]
    if any(word in transcription.lower() for word in analytical_keywords):
        return {"analytical_skills_score": 0.8, "feedback": "Good analytical reasoning."}

    return {"analytical_skills_score": 0.5, "feedback": "The response could benefit from more analytical reasoning."}

def evaluate_soft_skills(transcription):
    if not transcription.strip():  # Check if transcription is empty or just spaces
        return {"soft_skills_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    soft_skills_keywords = ["team", "collaborate", "leadership", "conflict", "empathy"]
    if any(word in transcription.lower() for word in soft_skills_keywords):
        return {"soft_skills_score": 0.9, "feedback": "Strong demonstration of soft skills."}

    return {"soft_skills_score": 0.6, "feedback": "Consider including more examples of teamwork, leadership, or empathy."}

def evaluate_learning_potential(transcription):
    if not transcription.strip():  # Check if transcription is empty or just spaces
        return {"learning_potential_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    learning_keywords = ["growth", "learn", "improve", "adapt"]
    if any(word in transcription.lower() for word in learning_keywords):
        return {"learning_potential_score": 0.8, "feedback": "Good indication of learning potential."}

    return {"learning_potential_score": 0.5, "feedback": "The response could highlight more learning potential."}
    
def evaluate_relevance(transcription, reference_answers):
    if not transcription.strip():
        return {"relevance_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    similarity_score = ParaphraseDetector().detect_paraphrase(reference_answers, transcription)
    return {"relevance_score": similarity_score, "feedback": "Highly relevant response." if similarity_score > 0.7 else "Response could be more relevant."}

def evaluate_accuracy(transcription, reference_answers):
    if not transcription.strip():
        return {"accuracy_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    similarity_score = ParaphraseDetector().detect_paraphrase(reference_answers, transcription)
    return {"accuracy_score": similarity_score, "feedback": "Accurate response." if similarity_score > 0.7 else "The response contains inaccuracies."}

def evaluate_confidence(transcription):
    if not transcription.strip():
        return {"confidence_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    if transcription[-1] in ["!", "."]:
        return {"confidence_score": 0.9, "feedback": "Confidently expressed response."}
    return {"confidence_score": 0.6, "feedback": "The response could be more confidently expressed."}

def evaluate_clarity(transcription):
    if not transcription.strip():
        return {"clarity_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    if len(transcription.split()) / len(transcription) > 0.1:
        return {"clarity_score": 0.9, "feedback": "Clear and well-articulated response."}
    return {"clarity_score": 0.6, "feedback": "The response could be clearer."}

def evaluate_adaptability(transcription):
    if not transcription.strip():
        return {"adaptability_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    adaptability_keywords = ["adapt", "flexible", "adjust", "change"]
    if any(word in transcription.lower() for word in adaptability_keywords):
        return {"adaptability_score": 0.8, "feedback": "Shows adaptability."}

    return {"adaptability_score": 0.5, "feedback": "The response could demonstrate more adaptability."}

def evaluate_grammar(transcription):
    if not transcription.strip():
        return {"grammar_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    if transcription.lower() == transcription.capitalize():  # Simplified check for grammar correctness
        return {"grammar_score": 0.9, "feedback": "Good grammar."}
    return {"grammar_score": 0.6, "feedback": "Consider improving grammar."}

def preprocess_text(transcription):
    """Preprocess the input text by normalizing whitespace and converting to lowercase."""
    return " ".join(transcription.strip().split()).lower()

"""def detect_ai_generated_text(transcription, models):
    Detect if a response is AI-generated using a fine-tuned Roberta model.
    response = preprocess_text(transcription)
    inputs = models['roberta_tokenizer'](transcription, padding=True, truncation=True, return_tensors="pt", max_length=512)
    models['roberta_model'].eval()
    with torch.no_grad():
        outputs = models['roberta_model'](**inputs)
        logits = outputs.logits
        prediction = torch.argmax(logits, dim=-1).item()
    return prediction == 1  # Return True if AI-generated, otherwise False
"""
# Function to handle the multidimensional evaluation of responses
def multidimensional_evaluation(transcription, reference_answers):
    if transcription == "Speech not recognized." or not transcription.strip():
        evaluation_scores = {
            "similarity_score": 0.0, "conciseness_score": 0.0, "engagement_score": 0.0,
            "technical_depth_score": 0.0, "analytical_skills_score": 0.0, "soft_skills_score": 0.0,
            "learning_potential_score": 0.0, "relevance_score": 0.0, "accuracy_score": 0.0,
            "confidence_score": 0.0, "clarity_score": 0.0, "adaptability_score": 0.0,
            "grammar_score": 0.0, "overall_score": 0.0
        }
        feedback = {
            "conciseness": {"conciseness_score": 0.0, "feedback": "No response provided."},
            "engagement": {"engagement_score": 0.0, "feedback": "No response provided."},
            "technical_depth": {"technical_depth_score": 0.0, "feedback": "No response provided."},
            "analytical_skills": {"analytical_skills_score": 0.0, "feedback": "No response provided."},
            "soft_skills": {"soft_skills_score": 0.0, "feedback": "No response provided."},
            "learning_potential": {"learning_potential_score": 0.0, "feedback": "No response provided."},
            "relevance": {"relevance_score": 0.0, "feedback": "No response provided."},
            "accuracy": {"accuracy_score": 0.0, "feedback": "No response provided."},
            "confidence": {"confidence_score": 0.0, "feedback": "No response provided."},
            "clarity": {"clarity_score": 0.0, "feedback": "No response provided."},
            "adaptability": {"adaptability_score": 0.0, "feedback": "No response provided."},
            "grammar": {"grammar_score": 0.0, "feedback": "No response provided."}
        }
        return evaluation_scores, feedback

    similarity_score = ParaphraseDetector().detect_paraphrase(reference_answers, transcription)
    conciseness = evaluate_conciseness(transcription)
    engagement = evaluate_engagement(transcription)
    technical_depth = evaluate_technical_depth(transcription, reference_answers)
    analytical_skills = evaluate_analytical_skills(transcription)
    soft_skills = evaluate_soft_skills(transcription)
    learning_potential = evaluate_learning_potential(transcription)
    relevance = evaluate_relevance(transcription, reference_answers)
    accuracy = evaluate_accuracy(transcription, reference_answers)
    confidence = evaluate_confidence(transcription)
    clarity = evaluate_clarity(transcription)
    adaptability = evaluate_adaptability(transcription)
    grammar = evaluate_grammar(transcription)

    # Create feedback dictionary
    feedback = {
        "conciseness": conciseness,
        "engagement": engagement,
        "technical_depth": technical_depth,
        "analytical_skills": analytical_skills,
        "soft_skills": soft_skills,
        "learning_potential": learning_potential,
        "relevance": relevance,
        "accuracy": accuracy,
        "confidence": confidence,
        "clarity": clarity,
        "adaptability": adaptability,
        "grammar": grammar
    }

    # Calculate overall_score as the mean of all individual scores
    overall_score = np.mean([
        similarity_score,
        conciseness["conciseness_score"],
        engagement["engagement_score"],
        technical_depth["technical_depth_score"],
        analytical_skills["analytical_skills_score"],
        soft_skills["soft_skills_score"],
        learning_potential["learning_potential_score"],
        relevance["relevance_score"],
        accuracy["accuracy_score"],
        confidence["confidence_score"],
        clarity["clarity_score"],
        adaptability["adaptability_score"],
        grammar["grammar_score"]
    ])

    # Add overall score to feedback
    feedback["overall_score"] = overall_score

    # Create evaluation_scores dictionary
    evaluation_scores = {
        "similarity_score": similarity_score,
        "conciseness_score": conciseness["conciseness_score"],
        "engagement_score": engagement["engagement_score"],
        "technical_depth_score": technical_depth["technical_depth_score"],
        "analytical_skills_score": analytical_skills["analytical_skills_score"],
        "soft_skills_score": soft_skills["soft_skills_score"],
        "learning_potential_score": learning_potential["learning_potential_score"],
        "relevance_score": relevance["relevance_score"],
        "accuracy_score": accuracy["accuracy_score"],
        "confidence_score": confidence["confidence_score"],
        "clarity_score": clarity["clarity_score"],
        "adaptability_score": adaptability["adaptability_score"],
        "grammar_score": grammar["grammar_score"],
        "overall_score": overall_score
    }

    return evaluation_scores, feedback
    
def clear_previous_responses():
    conn = sqlite3.connect('interviewBot.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM responses")  # Clear all data from the responses table
    conn.commit()
    conn.close()
    logging.info("Previous responses cleared from the database.")


# Start Interview Process
if __name__ == "__main__":
    create_db()
    clear_previous_responses()  # Clear old data

    # Run anti-cheating detection before starting the interview
    cheating_detected, cheating_reason = detect_anti_cheating()

    # If cheating is detected, exit the process
    if cheating_detected:
        logging.error(f"Interview cannot proceed due to cheating: {cheating_reason}")
        speak(f"Cheating detected: {cheating_reason}. The interview has been terminated.")
        exit(1)  # Exit the program if cheating is detected

    questions = load_dataset()
    num_questions = get_number_of_questions()

    if num_questions > len(questions):
        logging.info(f"Sorry, there are only {len(questions)} questions available. I will ask all of them.")
        num_questions = len(questions)

    selected_questions = random.sample(questions, num_questions)

    for i, item in enumerate(selected_questions):
        question = item["question"]
        reference_answers = [item["answer"]]
        logging.info(f"Question {i+1}: {question}")
        speak(question)

        saved_file = record_audio()
        if saved_file:
            logging.info(f"Audio saved to {saved_file}")
            transcription = convert_to_text(saved_file)
            evaluation_scores, feedback = multidimensional_evaluation(transcription, reference_answers)

            # Only pass cheating_detected and cheating_reason once, before the interview starts
            save_metadata(saved_file, question, transcription, evaluation_scores, feedback, cheating_detected, cheating_reason)

        logging.info(f"End of Question {i+1}")
        speak(f"End of Question {i+1}")

    export_to_csv()
    logging.info("Interview process completed.")
    speak("The interview process is completed successfully.")


# In[ ]:


#original code
# COMBINED CODE
import pyaudio
import wave
import speech_recognition as sr
import sqlite3
from datetime import datetime
import pyttsx3
import csv
import random
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
import json
import cv2
import time
import threading
import os
import pandas as pd
from transformers import pipeline, RobertaTokenizer, RobertaForSequenceClassification
from sentence_transformers import SentenceTransformer, util

def initialize_models():
    """Initialize all required models and pipelines."""
    models = {
        'roberta_model': RobertaForSequenceClassification.from_pretrained('/content/drive/MyDrive/fine_tuned_model/fine_tuned_model'),
        'roberta_tokenizer': RobertaTokenizer.from_pretrained('/content/drive/MyDrive/fine_tuned_model/fine_tuned_model')
    }
    return models


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom JSON Encoder to handle numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.generic):  # Check if the object is a numpy type
            return obj.item()  # Convert to native Python type (e.g., float32 -> float)
        return super(NumpyEncoder, self).default(obj)

# Load BERT model and tokenizer for paraphrase detection
class ParaphraseDetector:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def get_embeddings(self, sentences):
        inputs = self.tokenizer(sentences, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy()

    def detect_paraphrase(self, reference_answers, user_answer):
        embeddings_ref = self.get_embeddings(reference_answers)
        embedding_user = self.get_embeddings([user_answer])[0]
        similarities = cosine_similarity(embeddings_ref, [embedding_user])
        max_similarity = np.max(similarities)
        return float(max_similarity)  # Ensure it returns a float value

# Anti-cheating detection function with adjusted gaze deviation sensitivity
def detect_anti_cheating(video_duration=30, face_cascade_path="haarcascade_frontalface_default.xml", eye_cascade_path="haarcascade_eye.xml"):
    # Initialize variables
    cheating_detected = False
    cheating_reason = ""

    # Load Haar cascades for face and eye detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + face_cascade_path)
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + eye_cascade_path)

    # Initialize video capture
    cap = cv2.VideoCapture(0)  # 0 is the default camera index
    start_time = time.time()
    no_face_count = 0  # Count of consecutive frames with no face detected
    no_gaze_count = 0  # Count of consecutive frames with improper gaze detected

    logging.info("Starting video anti-cheating detection...")

    while time.time() - start_time < video_duration:
        ret, frame = cap.read()
        if not ret:
            logging.warning("Failed to capture video frame.")
            break

        # Convert frame to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Analyze face detection results
        if len(faces) == 0:
            no_face_count += 1
        else:
            no_face_count = 0  # Reset if a face is detected

        # If multiple faces are detected, flag as cheating
        if len(faces) > 1 and not cheating_detected:
            cheating_detected = True
            cheating_reason = "Multiple faces detected."
            log_cheating(cheating_reason)
            logging.warning(cheating_reason)
            break

        gaze_deviation_detected = False  # Flag for gaze deviation detection

        # Proceed with gaze checking only if exactly one face is detected
        if len(faces) == 1:
            for (x, y, w, h) in faces:
                roi_gray = gray[y:y + h, x:x + w]
                roi_color = frame[y:y + h, x:x + w]
                eyes = eye_cascade.detectMultiScale(roi_gray)

                # Detect gaze direction based on eye position
                if len(eyes) >= 2:  # Ensure at least two eyes are detected
                    eye_centers = []
                    for (ex, ey, ew, eh) in eyes[:2]:  # Process up to two eyes
                        eye_center_x = x + ex + ew // 2
                        eye_centers.append(eye_center_x)

                    # Check if gaze is within the frame center (adjusted threshold for deviation)
                    frame_center_x = frame.shape[1] // 2
                    if any(abs(center - frame_center_x) > 150 for center in eye_centers):  # Increased threshold for gaze deviation
                        no_gaze_count += 1
                        gaze_deviation_detected = True
                    else:
                        no_gaze_count = 0  # Reset if proper gaze is detected

        # If no face detected for an extended period
        if no_face_count > 50 and not cheating_detected:  # Approximately 2 seconds at 25 fps
            cheating_detected = True
            cheating_reason = "No face detected for extended period."
            log_cheating(cheating_reason)
            logging.warning(cheating_reason)
            break

        # If gaze is deviating from the screen for an extended period
        if gaze_deviation_detected:
            no_gaze_count += 1  # Increase the count for gaze deviation
        else:
            no_gaze_count = 0  # Reset if gaze is within the center

        if no_gaze_count > 50 and not cheating_detected:  # Approximately 2 seconds at 25 fps
            cheating_detected = True
            cheating_reason = "Gaze deviated from the screen for extended period."
            log_cheating(cheating_reason)
            logging.warning(cheating_reason)
            break

        # Display the video feed with detections
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.imshow("Anti-Cheating Detection", frame)

        # Press 'q' to exit early
        if cv2.waitKey(1) & 0xFF == ord('q'):
            logging.info("Video anti-cheating detection ended by user.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if cheating_detected:
        logging.error("Cheating detected during the interview.")
        speak(f"Cheating behavior detected. Reason: {cheating_reason}")
    else:
        logging.info("No cheating detected.")
        speak("Anti-cheating detection completed successfully.")

    return cheating_detected, cheating_reason


# Function to create the database and table (only creates if it doesn't exist)
def create_db():
    conn = sqlite3.connect('interviewBot.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS responses (
                        id INTEGER PRIMARY KEY,
                        filename TEXT,
                        question TEXT,
                        timestamp TEXT,
                        transcription TEXT,
                        similarity_score REAL,
                        conciseness_score REAL,
                        engagement_score REAL,
                        technical_depth_score REAL,
                        analytical_skills_score REAL,
                        soft_skills_score REAL,
                        learning_potential_score REAL,
                        relevance_score REAL,
                        accuracy_score REAL,
                        logical_reasoning_score REAL,
                        confidence_score REAL,
                        clarity_score REAL,
                        adaptability_score REAL,
                        grammar_score REAL,
                        ai_detection_score REAL,
                        overall_score REAL,
                        feedback TEXT,
                        cheating_detected TEXT,
                        cheating_reason TEXT)''')
    conn.commit()
    conn.close()

def update_table_schema():
    conn = sqlite3.connect('interviewBot.db')
    cursor = conn.cursor()

    # Add missing columns if they do not exist
    columns_to_add = [
        ("conciseness_score", "REAL"),
        ("engagement_score", "REAL"),
        ("technical_depth_score", "REAL"),
        ("analytical_skills_score", "REAL"),
        ("soft_skills_score", "REAL"),
        ("learning_potential_score", "REAL"),
        ("relevance_score", "REAL"),
        ("accuracy_score", "REAL"),
        ("logical_reasoning_score", "REAL"),
        ("confidence_score", "REAL"),
        ("clarity_score", "REAL"),
        ("adaptability_score", "REAL"),
        ("grammar_score", "REAL"),
        ("ai_detection_score", "REAL"),
        ("overall_score", "REAL"),
        ("cheating_detected", "TEXT"),  # New column for cheating detection
        ("cheating_reason", "TEXT")     # New column for cheating reason
    ]

    for column_name, column_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE responses ADD COLUMN {column_name} {column_type}")
            logging.info(f"Column '{column_name}' added successfully.")
        except sqlite3.OperationalError:
            logging.warning(f"Column '{column_name}' already exists.")

    conn.commit()
    conn.close()

# Call the function to update the schema
update_table_schema()

# Function to save metadata, including cheating detection information
def save_metadata(filename, question, transcription, evaluation_scores, feedback, cheating_detected, cheating_reason):
    conn = sqlite3.connect('interviewBot.db')
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Serialize feedback to a JSON string before saving it
    feedback_json = json.dumps(feedback, cls=NumpyEncoder)

    cursor.execute('''INSERT INTO responses (filename, question, timestamp, transcription, similarity_score,
                      conciseness_score, engagement_score, technical_depth_score,
                      analytical_skills_score, soft_skills_score, learning_potential_score, relevance_score, 
                      accuracy_score, logical_reasoning_score, confidence_score, clarity_score, adaptability_score, 
                      grammar_score, ai_detection_score, overall_score, feedback, cheating_detected, cheating_reason)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (filename, question, timestamp, transcription, evaluation_scores['similarity_score'],
                    evaluation_scores['conciseness_score'], evaluation_scores['engagement_score'],
                    evaluation_scores['technical_depth_score'],
                    evaluation_scores['analytical_skills_score'], evaluation_scores['soft_skills_score'],
                    evaluation_scores['learning_potential_score'], evaluation_scores['relevance_score'],
                    evaluation_scores['accuracy_score'], evaluation_scores['logical_reasoning_score'],
                    evaluation_scores['confidence_score'], evaluation_scores['clarity_score'],
                    evaluation_scores['adaptability_score'], evaluation_scores['grammar_score'],
                    evaluation_scores['ai_detection_score'], evaluation_scores['overall_score'],
                    feedback_json, "False" if not cheating_detected else "True", cheating_reason))
    conn.commit()
    conn.close()

# Function to export data to CSV with accurate 'cheating_detected' and 'cheating_reason' mapping
def export_to_csv(csv_filename="EvaluatedResponses.csv"):
    conn = sqlite3.connect('interviewBot.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, filename, question, timestamp, transcription, similarity_score, "
                   "conciseness_score, engagement_score, technical_depth_score, "
                   "analytical_skills_score, soft_skills_score, learning_potential_score, relevance_score, "
                   "accuracy_score, logical_reasoning_score, confidence_score, clarity_score, adaptability_score, "
                   "grammar_score, ai_detection_score, overall_score, feedback, "
                   "cheating_detected, cheating_reason FROM responses")
    rows = cursor.fetchall()

    headers = ["ID", "Filename", "Question", "Timestamp", "Transcription", "Similarity Score",
               "Conciseness Score", "Engagement Score", "Technical Depth Score",
               "Analytical Skills Score", "Soft Skills Score", "Learning Potential Score", "Relevance Score",
               "Accuracy Score", "Logical Reasoning Score", "Confidence Score", "Clarity Score", "Adaptability Score",
               "Grammar Score", "AI Detection Score", "Overall Score",
               "Feedback", "Cheating Detected", "Cheating Reason"]

    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for row in rows:
            row_with_feedback = list(row)
            feedback_json = row_with_feedback[-3]  # The feedback column is now the 3rd to last column

            try:
                feedback_dict = json.loads(feedback_json)
                row_with_feedback[-3] = feedback_dict
            except (json.JSONDecodeError, TypeError):
                row_with_feedback[-3] = {}

            # Correctly handle the cheating information
            cheating_detected = row_with_feedback[-2]  # Directly use the saved value
            cheating_reason = row_with_feedback[-1] if row_with_feedback[-1] else ""

            # Update only the relevant fields in CSV
            row_with_feedback.extend([cheating_detected, cheating_reason])
            writer.writerow(row_with_feedback)

    conn.close()
    logging.info(f"Data successfully exported to {csv_filename}.")

# Function to record audio
def record_audio(filename="output.wav", record_seconds=10, channels=1, rate=44100, chunk=1024):
    audio = pyaudio.PyAudio()
    input_device_index = None

    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            input_device_index = i
            break

    if input_device_index is None:
        logging.error("No input audio devices found.")
        return None

    stream = audio.open(format=pyaudio.paInt16, channels=channels, rate=rate, input=True, frames_per_buffer=chunk,
                        input_device_index=input_device_index)
    logging.info("Recording...")
    frames = []

    for _ in range(0, int(rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)

    logging.info("Finished recording.")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))

    return filename

# Function to convert speech to text
def convert_to_text(audio_file):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file) as source:
            logging.info("Converting audio to text...")
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        logging.info("Conversion complete.")
        return text

    except sr.UnknownValueError:
        logging.warning("Speech not recognized.")
        return "Speech not recognized."
    except sr.RequestError as e:
        logging.error(f"Could not request results from Google Speech Recognition service; {e}")
        return f"Error: {e}"

# Function to make the bot speak
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Function to load the dataset (CSV file)
def load_dataset(filename="dataset.csv"):
    questions = []
    with open(filename, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            questions.append({
                "question": row["Question"],
                "answer": row["Answer"],
                "difficulty": row["Difficulty"]
            })
    return questions

# Function to ask how many questions to ask and return the selected number
def get_number_of_questions():
    try:
        num_questions = int(input("How many questions would you like to be asked? "))
        return num_questions
    except ValueError:
        logging.error("Invalid input. Please enter a number.")
        return get_number_of_questions()

def log_cheating(reason):
    """Logs the cheating reason to a CSV file."""
    with open("EvaluatedResponses.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Cheating detected", reason])

# Function to evaluate responses based on similarity, feedback, and completeness
def evaluate_response(transcription, reference_answer):
    if not transcription.strip():  # Check if transcription is empty or just spaces
        return {"similarity_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    similarity_score = ParaphraseDetector().detect_paraphrase([reference_answer], transcription)
    feedback = {"similarity_score": similarity_score,
                "feedback": "Good answer!" if similarity_score > 0.7 else "The answer could be more precise."}
    return feedback

# Additional evaluation functions for multi-dimensional skills
def evaluate_conciseness(transcription):
    if not transcription.strip():  # Check if transcription is empty or just spaces
        return {"conciseness_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    word_count = len(transcription.split())
    if word_count < 5:
        return {"conciseness_score": 1.0, "feedback": "The response is very concise, but might lack detail."}
    elif word_count < 20:
        return {"conciseness_score": 0.8, "feedback": "The response is concise and to the point."}
    else:
        return {"conciseness_score": 0.5, "feedback": "The response is verbose. Try to make it more concise."}

def evaluate_engagement(transcription):
    if not transcription.strip():  # Check if transcription is empty or just spaces
        return {"engagement_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    # Sentiment analysis approach
    engagement_keywords = ["excited", "happy", "passionate", "enthusiastic"]
    if any(word in transcription.lower() for word in engagement_keywords):
        return {"engagement_score": 0.9, "feedback": "The response is engaging and enthusiastic."}

    return {"engagement_score": 0.6, "feedback": "The response could be more engaging with positive tone or structured flow."}

def evaluate_technical_depth(transcription, reference_answers):
    if not transcription.strip():  # Check if transcription is empty or just spaces
        return {"technical_depth_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    similarity_score = ParaphraseDetector().detect_paraphrase(reference_answers, transcription)
    if similarity_score > 0.8:
        return {"technical_depth_score": 1.0, "feedback": "Excellent technical depth."}
    elif similarity_score > 0.6:
        return {"technical_depth_score": 0.7, "feedback": "Good technical depth but could be more precise."}
    else:
        return {"technical_depth_score": 0.4, "feedback": "The response lacks sufficient technical depth."}

def evaluate_analytical_skills(transcription):
    if not transcription.strip():  # Check if transcription is empty or just spaces
        return {"analytical_skills_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    # Check for logical words
    analytical_keywords = ["therefore", "because", "hence", "consequently"]
    if any(word in transcription.lower() for word in analytical_keywords):
        return {"analytical_skills_score": 0.8, "feedback": "Good analytical reasoning."}

    return {"analytical_skills_score": 0.5, "feedback": "The response could benefit from more analytical reasoning."}

def evaluate_soft_skills(transcription):
    if not transcription.strip():  # Check if transcription is empty or just spaces
        return {"soft_skills_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    soft_skills_keywords = ["team", "collaborate", "leadership", "conflict", "empathy"]
    if any(word in transcription.lower() for word in soft_skills_keywords):
        return {"soft_skills_score": 0.9, "feedback": "Strong demonstration of soft skills."}

    return {"soft_skills_score": 0.6, "feedback": "Consider including more examples of teamwork, leadership, or empathy."}

def evaluate_learning_potential(transcription):
    if not transcription.strip():  # Check if transcription is empty or just spaces
        return {"learning_potential_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    learning_keywords = ["growth", "learn", "improve", "adapt"]
    if any(word in transcription.lower() for word in learning_keywords):
        return {"learning_potential_score": 0.8, "feedback": "Good indication of learning potential."}

    return {"learning_potential_score": 0.5, "feedback": "The response could highlight more learning potential."}
    
def evaluate_relevance(transcription, reference_answers):
    if not transcription.strip():
        return {"relevance_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    similarity_score = ParaphraseDetector().detect_paraphrase(reference_answers, transcription)
    return {"relevance_score": similarity_score, "feedback": "Highly relevant response." if similarity_score > 0.7 else "Response could be more relevant."}

def evaluate_accuracy(transcription, reference_answers):
    if not transcription.strip():
        return {"accuracy_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    similarity_score = ParaphraseDetector().detect_paraphrase(reference_answers, transcription)
    return {"accuracy_score": similarity_score, "feedback": "Accurate response." if similarity_score > 0.7 else "The response contains inaccuracies."}

def evaluate_confidence(transcription):
    if not transcription.strip():
        return {"confidence_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    if transcription[-1] in ["!", "."]:
        return {"confidence_score": 0.9, "feedback": "Confidently expressed response."}
    return {"confidence_score": 0.6, "feedback": "The response could be more confidently expressed."}

def evaluate_clarity(transcription):
    if not transcription.strip():
        return {"clarity_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    if len(transcription.split()) / len(transcription) > 0.1:
        return {"clarity_score": 0.9, "feedback": "Clear and well-articulated response."}
    return {"clarity_score": 0.6, "feedback": "The response could be clearer."}

def evaluate_adaptability(transcription):
    if not transcription.strip():
        return {"adaptability_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    adaptability_keywords = ["adapt", "flexible", "adjust", "change"]
    if any(word in transcription.lower() for word in adaptability_keywords):
        return {"adaptability_score": 0.8, "feedback": "Shows adaptability."}

    return {"adaptability_score": 0.5, "feedback": "The response could demonstrate more adaptability."}

def evaluate_grammar(transcription):
    if not transcription.strip():
        return {"grammar_score": 0.0, "feedback": "No response provided. Please provide a valid response."}

    if transcription.lower() == transcription.capitalize():  # Simplified check for grammar correctness
        return {"grammar_score": 0.9, "feedback": "Good grammar."}
    return {"grammar_score": 0.6, "feedback": "Consider improving grammar."}

def preprocess_text(transcription):
    """Preprocess the input text by normalizing whitespace and converting to lowercase."""
    return " ".join(transcription.strip().split()).lower()

def detect_ai_generated_text(transcription, models):
    """Detect if a response is AI-generated using a fine-tuned Roberta model."""
    response = preprocess_text(transcription)
    inputs = models['roberta_tokenizer'](transcription, padding=True, truncation=True, return_tensors="pt", max_length=512)
    models['roberta_model'].eval()
    with torch.no_grad():
        outputs = models['roberta_model'](**inputs)
        logits = outputs.logits
        prediction = torch.argmax(logits, dim=-1).item()
    return prediction == 1  # Return True if AI-generated, otherwise False

# Function to handle the multidimensional evaluation of responses
def multidimensional_evaluation(transcription, reference_answers):
    if transcription == "Speech not recognized." or not transcription.strip():
        evaluation_scores = {
            "similarity_score": 0.0, "conciseness_score": 0.0, "engagement_score": 0.0,
            "technical_depth_score": 0.0, "analytical_skills_score": 0.0, "soft_skills_score": 0.0,
            "learning_potential_score": 0.0, "relevance_score": 0.0, "accuracy_score": 0.0,
            "confidence_score": 0.0, "clarity_score": 0.0, "adaptability_score": 0.0,
            "grammar_score": 0.0, "ai_detection_score": 0.0, "overall_score": 0.0
        }
        feedback = {
            "conciseness": {"conciseness_score": 0.0, "feedback": "No response provided."},
            "engagement": {"engagement_score": 0.0, "feedback": "No response provided."},
            "technical_depth": {"technical_depth_score": 0.0, "feedback": "No response provided."},
            "analytical_skills": {"analytical_skills_score": 0.0, "feedback": "No response provided."},
            "soft_skills": {"soft_skills_score": 0.0, "feedback": "No response provided."},
            "learning_potential": {"learning_potential_score": 0.0, "feedback": "No response provided."},
            "relevance": {"relevance_score": 0.0, "feedback": "No response provided."},
            "accuracy": {"accuracy_score": 0.0, "feedback": "No response provided."},
            "confidence": {"confidence_score": 0.0, "feedback": "No response provided."},
            "clarity": {"clarity_score": 0.0, "feedback": "No response provided."},
            "adaptability": {"adaptability_score": 0.0, "feedback": "No response provided."},
            "grammar": {"grammar_score": 0.0, "feedback": "No response provided."},
            "ai_detection": {"ai_detection_score": 0.0, "feedback": "No response provided."}
        }
        return evaluation_scores, feedback

    similarity_score = ParaphraseDetector().detect_paraphrase(reference_answers, transcription)
    conciseness = evaluate_conciseness(transcription)
    engagement = evaluate_engagement(transcription)
    technical_depth = evaluate_technical_depth(transcription, reference_answers)
    analytical_skills = evaluate_analytical_skills(transcription)
    soft_skills = evaluate_soft_skills(transcription)
    learning_potential = evaluate_learning_potential(transcription)
    relevance = evaluate_relevance(transcription, reference_answers)
    accuracy = evaluate_accuracy(transcription, reference_answers)
    confidence = evaluate_confidence(transcription)
    clarity = evaluate_clarity(transcription)
    adaptability = evaluate_adaptability(transcription)
    grammar = evaluate_grammar(transcription)
    ai_detection = detect_ai_generated_text(transcription, models)

    # Create feedback dictionary
    feedback = {
        "conciseness": conciseness,
        "engagement": engagement,
        "technical_depth": technical_depth,
        "analytical_skills": analytical_skills,
        "soft_skills": soft_skills,
        "learning_potential": learning_potential,
        "relevance": relevance,
        "accuracy": accuracy,
        "confidence": confidence,
        "clarity": clarity,
        "adaptability": adaptability,
        "grammar": grammar,
        "ai_detection": ai_detection
    }

    # Calculate overall_score as the mean of all individual scores
    overall_score = np.mean([
        similarity_score,
        conciseness["conciseness_score"],
        engagement["engagement_score"],
        technical_depth["technical_depth_score"],
        analytical_skills["analytical_skills_score"],
        soft_skills["soft_skills_score"],
        learning_potential["learning_potential_score"],
        relevance["relevance_score"],
        accuracy["accuracy_score"],
        confidence["confidence_score"],
        clarity["clarity_score"],
        adaptability["adaptability_score"],
        grammar["grammar_score"],
        ai_detection["ai_detection_score"]
    ])

    # Add overall score to feedback
    feedback["overall_score"] = overall_score

    # Create evaluation_scores dictionary
    evaluation_scores = {
        "similarity_score": similarity_score,
        "conciseness_score": conciseness["conciseness_score"],
        "engagement_score": engagement["engagement_score"],
        "technical_depth_score": technical_depth["technical_depth_score"],
        "analytical_skills_score": analytical_skills["analytical_skills_score"],
        "soft_skills_score": soft_skills["soft_skills_score"],
        "learning_potential_score": learning_potential["learning_potential_score"],
        "relevance_score": relevance["relevance_score"],
        "accuracy_score": accuracy["accuracy_score"],
        "confidence_score": confidence["confidence_score"],
        "clarity_score": clarity["clarity_score"],
        "adaptability_score": adaptability["adaptability_score"],
        "grammar_score": grammar["grammar_score"],
        "ai_detection_score": ai_detection["ai_detection_score"],
        "overall_score": overall_score
    }

    return evaluation_scores, feedback


# Start Interview Process
if __name__ == "__main__":
    create_db()

    # Run anti-cheating detection before starting the interview
    cheating_detected, cheating_reason = detect_anti_cheating()

    # If cheating is detected, exit the process
    if cheating_detected:
        logging.error(f"Interview cannot proceed due to cheating: {cheating_reason}")
        speak(f"Cheating detected: {cheating_reason}. The interview has been terminated.")
        exit(1)  # Exit the program if cheating is detected

    questions = load_dataset()
    num_questions = get_number_of_questions()

    if num_questions > len(questions):
        logging.info(f"Sorry, there are only {len(questions)} questions available. I will ask all of them.")
        num_questions = len(questions)

    selected_questions = random.sample(questions, num_questions)

    for i, item in enumerate(selected_questions):
        question = item["question"]
        reference_answers = [item["answer"]]
        logging.info(f"Question {i+1}: {question}")
        speak(question)

        saved_file = record_audio()
        if saved_file:
            logging.info(f"Audio saved to {saved_file}")
            transcription = convert_to_text(saved_file)
            evaluation_scores, feedback = multidimensional_evaluation(transcription, reference_answers)

            # Only pass cheating_detected and cheating_reason once, before the interview starts
            save_metadata(saved_file, question, transcription, evaluation_scores, feedback, cheating_detected, cheating_reason)

        logging.info(f"End of Question {i+1}")
        speak(f"End of Question {i+1}")

    export_to_csv()
    logging.info("Interview process completed.")
    speak("The interview process is completed successfully.")


# In[ ]:




