from fastapi import UploadFile, File, HTTPException,APIRouter
from fastapi.responses import JSONResponse
import os
import wave
import pyaudio
import logging
import time
import numpy as np
import speech_recognition as sr
from bson import ObjectId  # Import ObjectId
from datetime import datetime
from pymongo import MongoClient
from pydantic import BaseModel
router=APIRouter()
# MongoDB setup
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["interview_db"]
responses_collection = db["responses"]
questions_collection = db["questions"]
# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# Function to record audio
def record_audio(filename="output.wav", silence_threshold=500, silence_duration=5, channels=1, rate=44100, chunk=1024):
    audio = pyaudio.PyAudio()
    input_device_index = None

    # Find an input device
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info["maxInputChannels"] > 0:
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
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b"".join(frames))

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
        logging.error(f"Google Speech Recognition service error: {e}")
        return f"Error: {e}"

# API Models
class AudioResponse(BaseModel):
    question_id: int
    audio_file: str
    text_response: str
    timestamp: datetime

# API to process uploaded audio: save, transcribe, and store in MongoDB
@router.post("/process-audio/")
def process_audio(question_id: str, file: UploadFile = File(...)):
    try:
        # Convert the string question_id to ObjectId
        try:
            question_object_id = ObjectId(question_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid ObjectId format.")

        # Validate question ID (now as an ObjectId)
        question_exists = questions_collection.find_one({"_id": question_object_id})
        if not question_exists:
            raise HTTPException(status_code=404, detail="Question ID not found in database.")

        # Save uploaded audio file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_file = f"responses/{question_id}_{timestamp}.wav"
        os.makedirs("responses", exist_ok=True)

        with open(audio_file, "wb") as f:
            f.write(file.file.read())

        # Convert audio to text
        text_response = convert_to_text(audio_file)

        # Convert ObjectId to string when returning
        response_data = {
            "question_id": str(question_exists["_id"]),  # Convert ObjectId to string
            "audio_file": audio_file,
            "text_response": text_response,
            "timestamp": datetime.utcnow().isoformat()  # Convert datetime to string format
        }

        # Store in MongoDB with ISO formatted timestamp
        responses_collection.insert_one(response_data)

        return JSONResponse(
            status_code=200,
            content={
                "message": "Audio processed and stored successfully.",
                "data": response_data
            }
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Error processing audio: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})