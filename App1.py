import os
from flask import Flask, jsonify
import random

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Flask API hosted on Render!"

@app.route('/get-random-data', methods=['GET'])
def get_random_data():
    data = {
        "number": random.randint(1, 100),
        "message": "Here is your random number"
    }
    return jsonify(data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
