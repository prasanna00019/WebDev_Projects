from fastapi import  HTTPException,APIRouter,Body
from pymongo import MongoClient
from typing import List
import csv
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime
# Initialize FastAPI app
router = APIRouter()
# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["interview_db"]
questions_collection = db["questions"]
sessions_collection = db["sessions"]
# Pydantic Models
class Question(BaseModel):
    question: str
    answer: str
    difficulty: str
class Session(BaseModel):
    session_id: str
    questions: List[Question]
# Function to load the dataset into MongoDB (one-time operation)
def clean_mongo_object(doc):
    """Recursively clean MongoDB objects by converting ObjectId to string."""
    if isinstance(doc, list):
        return [clean_mongo_object(item) for item in doc]
    if isinstance(doc, dict):
        return {key: clean_mongo_object(value) for key, value in doc.items()}
    if isinstance(doc, ObjectId):
        return str(doc)
    return doc
@router.post('/load-dataset-first-time/')
def load_dataset_to_mongodb(filename="dataset.csv"):
    questions = []
    with open(filename, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            question = {
                "question": row["Question"],
                "answer": row["Answer"],
                "difficulty": row["Difficulty"]
            }
            questions.append(question)
    # Insert into MongoDB
    questions_collection.insert_many(questions)
    print("Dataset loaded into MongoDB.")

# API for the interviewer to select questions
@router.post("/select-questions/")
def select_questions(request: dict = Body(...)):
    num_questions = request.get("num_questions")
    if not num_questions or num_questions <= 0:
        raise HTTPException(status_code=400, detail="Number of questions must be greater than 0.")

    total_questions = questions_collection.count_documents({})
    if num_questions > total_questions:
        raise HTTPException(status_code=400, detail=f"Only {total_questions} questions available.")

    selected_questions = list(questions_collection.aggregate([{"$sample": {"size": num_questions}}]))
    session_id = f"session_{int(datetime.utcnow().timestamp())}"
    
    session_data = {
        "session_id": session_id,
        "questions": selected_questions,
        "created_at": datetime.utcnow()
    }
    sessions_collection.insert_one(session_data)

    # Clean data for JSON response
    response = {
        "session_id": session_id,
        "questions": clean_mongo_object(selected_questions)
    }
    return response
# API for candidates to fetch their questions
@router.get("/get-questions/{session_id}/")
def get_questions(session_id: str):
    session = sessions_collection.find_one({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    questions = session.get("questions", [])
    response_data = {
        "session_id": session_id,
        "questions": clean_mongo_object(questions)
    }
    return response_data

# API for debugging or to list all questions (optional)
@router.get("/list-questions/")
def list_questions():
    questions = list(questions_collection.find({}, {"_id": 0}))
    return {"questions": questions}
