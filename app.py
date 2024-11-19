# pip install google-generativeai
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configure Google Gemini API
genai.configure(api_key="AIzaSyDT7bvq6tWlQsf9-3-uwGxWYCO9VHGAGQI")  # Replace with your actual Gemini API key

def use_gemini_api(prompt, text):
    """
    Helper function to send a prompt and content to Gemini API.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-001")
        chat = model.start_chat()
        response = chat.send_message(f"{prompt}\n{text}")
        return response.text
    except Exception as e:
        raise ValueError(f"Error using Gemini API: {str(e)}")
        
def get_gemini_summary(text):
    """
    This function takes text as input and returns the Gemini summary.
    """
    try:
        # Create a GenerativeModel object
        model = genai.GenerativeModel("gemini-1.5-flash-001")  # Adjust model name based on your needs

        # Start a chat session
        chat = model.start_chat()

        # Send the prompt and content for summarization
        prompt = "Summarize the following text:"
        response = chat.send_message(prompt + "\n" + text)

        # Return the generated summary
        return response.text

    except Exception as e:
        raise ValueError(f"Error during summarization: {str(e)}")


@app.route('/summarize', methods=['POST'])
def summarize():
    """
    API endpoint to receive text and return the summary.
    """
    try:
        # Get the text data from the request body
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Invalid input. "text" field is required.'}), 400

        text = data['text']

        # Get the summary using the helper function
        summary = get_gemini_summary(text)

        return jsonify({'summary': summary})

    except Exception as e:
        return jsonify({'error': str(e)}), 400  # Return error with a 400 Bad Request status

@app.route('/optimize', methods=['POST'])
def optimize_code():
    """
    Route to optimize the given code.
    """
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({'error': 'Invalid input. "code" field is required.'}), 400

        code = data['code']
        prompt = "Optimize the following code:"
        optimized_code = use_gemini_api(prompt, code)

        return jsonify({'optimized_code': optimized_code})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/error-correct', methods=['POST'])
def correct_code_errors():
    """
    Route to correct errors in the given code.
    """
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({'error': 'Invalid input. "code" field is required.'}), 400

        code = data['code']
        prompt = "Correct errors in the following code:"
        corrected_code = use_gemini_api(prompt, code)

        return jsonify({'corrected_code': corrected_code})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/code-summary', methods=['POST'])
def summarize_code():
    """
    Route to provide a summary of the given code.
    """
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({'error': 'Invalid input. "code" field is required.'}), 400

        code = data['code']
        prompt = "Summarize the following code. Explain what it does:"
        summary = use_gemini_api(prompt, code)

        return jsonify({'code_summary': summary})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/translate-code', methods=['POST'])
def translate_code():
    """
    Route to translate the given code to another programming language.
    """
    try:
        data = request.get_json()
        if not data or 'code' not in data or 'language' not in data:
            return jsonify({'error': 'Invalid input. Both "code" and "language" fields are required.'}), 400

        code = data['code']
        language = data['language']
        prompt = f"Translate the following code into {language}:"
        translated_code = use_gemini_api(prompt, code)

        return jsonify({'translated_code': translated_code})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/project-questions', methods=['POST'])
def answer_project_questions():
    """
    Route to answer project-related questions.
    """
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({'error': 'Invalid input. "question" field is required.'}), 400

        question = data['question']
        prompt = "Answer the following project-related question:"
        answer = use_gemini_api(prompt, question)

        return jsonify({'answer': answer})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
