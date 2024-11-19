from flask import Flask, request, jsonify
import google.generativeai as genai
!pip install google-generativeai

app = Flask(__name__)

# Configure Google Gemini API
genai.configure(api_key="AIzaSyDT7bvq6tWlQsf9-3-uwGxWYCO9VHGAGQI")  # Replace with your actual Gemini API key

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


if __name__ == '__main__':
    app.run(debug=True)
