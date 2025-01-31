from fastapi import  HTTPException, APIRouter
from pydantic import BaseModel
from pymongo import MongoClient
import numpy as np
import torch
from bson import ObjectId
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
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

# Multidimensional evaluation function
def multidimensional_evaluation(transcription, reference_answers):
    # Use your detailed evaluation logic provided
    if transcription == "Speech not recognized." or not transcription.strip():
        evaluation_scores = {
            "similarity_score": 0.0, "conciseness_score": 0.0, "engagement_score": 0.0,
            "technical_depth_score": 0.0, "analytical_skills_score": 0.0, "soft_skills_score": 0.0,
            "learning_potential_score": 0.0, "relevance_score": 0.0, "accuracy_score": 0.0,
            "confidence_score": 0.0, "clarity_score": 0.0, "adaptability_score": 0.0,
            "grammar_score": 0.0, "overall_score": 0.0
        }
        feedback = {key: {"score": 0.0, "feedback": "No response provided."} for key in evaluation_scores}
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


# FastAPI app initialization
router=APIRouter()

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client["interview_database"]
responses_collection = db["responses"]

# Request model for evaluation API
class EvaluationRequest(BaseModel):
    question_id: str
    reference_answer: str

# API endpoint for evaluation

@router.post("/evaluate-answer/")
def evaluate_answer(request: EvaluationRequest):
    """
    API to evaluate a recorded answer based on the transcription and reference answer.

    Args:
        request (EvaluationRequest): The request containing question_id and reference_answer.

    Returns:
        dict: Evaluation scores and feedback.
    """
    try:
        # If question_id is a string, convert it to ObjectId
        try:
            question_id = ObjectId(request.question_id)  # Convert to ObjectId if it's a string
        except Exception:
            question_id = request.question_id  # It's already a string, no conversion needed
        print(question_id, request.reference_answer)
        # Fetch the response from the database using the correct question_id (either string or ObjectId)
        response = responses_collection.find_one({"question_id": question_id})
        
        if not response:
            raise HTTPException(status_code=404, detail="Answer not found for the given question ID.")
        
        transcription = response.get("text_response")
        
        if not transcription:
            raise HTTPException(status_code=404, detail="No transcription available for evaluation.")

        # Evaluate the transcription
        evaluation_scores, feedback = multidimensional_evaluation(transcription, [request.reference_answer])

        return {
            "question_id": request.question_id,  # Return the original question_id (as string)
            "text_response": transcription,
            "evaluation_scores": evaluation_scores,
            "feedback": feedback
        }

    except Exception as e:
        return {"error": str(e)}