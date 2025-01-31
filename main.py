from fastapi import FastAPI, UploadFile,HTTPException
from fastapi.middleware.cors import CORSMiddleware
import wave
from datetime import datetime
import logging
from pymongo import MongoClient
import speech_recognition as sr
import os
logging.basicConfig(level=logging.INFO)
from recording_response import router as recording_router
from asking_question import router as asking_router 
from evaluating_response import router as evaluating_router
app = FastAPI()
# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(recording_router,prefix="/recording",tags=["recording"])
app.include_router(asking_router,prefix="/asking",tags=["asking"])
app.include_router(evaluating_router,prefix="/evaluating",tags=["evaluating"])
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Interviewer API!"}
client = MongoClient("mongodb://localhost:27017/")
db = client["interview_db"]
questions_collection = db["questions"]
sessions_collection = db["sessions"]

# Ensure 'uploads' directory exists
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Convert audio to text
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

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile):
    file_location = f"uploads/{file.filename}"

    # Save the uploaded file
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Validate the WAV file
    try:
        with wave.open(file_location, "rb") as wf:
            wf.getparams()  # Ensure it's a valid WAV file
    except wave.Error as e:
        return {"error": f"Invalid WAV file: {e}"}

    # Convert the audio to text
    transcription = convert_to_text(file_location)
    return {"transcription": transcription}

