from fastapi import FastAPI, HTTPException
from recording_model import record_audio  # Import logic from recording_model.py
from modeltraining import evaluate_model  # Import logic from modeltraining.py

app = FastAPI()

@app.post("/record")
async def record(data: dict):
    """
    API to record answers to questions.
    """
    try:
        result = record_audio(data)  # Call the function from recording_model.py
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/evaluate")
async def evaluate(data: dict):
    """
    API to evaluate answers.
    """
    try:
        result = evaluate_model(data)  # Call the function from modeltraining.py
        return {"status": "success", "evaluation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
