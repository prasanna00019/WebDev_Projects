from flask import Flask, request, jsonify
import difflib

app = Flask(__name__)

def get_code_diff(file1_content, file2_content):
    """Generate the differences between two code files."""
    diff = difflib.unified_diff(
        file1_content.splitlines(keepends=True),
        file2_content.splitlines(keepends=True),
        fromfile='File1',
        tofile='File2',
        lineterm=''
    )
    return ''.join(diff)

@app.route('/diff', methods=['POST'])
def diff():
    """
    Compare two code files and return the differences.
    Expected JSON input format:
    {
        "file1": "Content of the first file...",
        "file2": "Content of the second file..."
    }
    """
    data = request.json
    file1_content = data.get('file1')
    file2_content = data.get('file2')

    if file1_content is None or file2_content is None:
        return jsonify({"error": "Both 'file1' and 'file2' contents must be provided"}), 400

    # Get the code difference
    diff_result = get_code_diff(file1_content, file2_content)
    
    return jsonify({"diff": diff_result})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
