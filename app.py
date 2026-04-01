import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
import os
from PyPDF2 import PdfReader

app = Flask(__name__, template_folder='.')
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variable for simplicity (in a production app, use Redis/Session)
pdf_content = ""

# Configure Gemini API
API_KEY = "AIzaSyAXsZmsQmDoERm3e8y-b6yGcLyaMV2Uojg"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global pdf_content
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.endswith('.pdf'):
        try:
            reader = PdfReader(file)
            extracted_text = ""
            for page in reader.pages:
                extracted_text += page.extract_text() + "\n"
            pdf_content = extracted_text
            return jsonify({'success': 'File uploaded and processed', 'filename': file.filename})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Invalid file type. Only PDF allowed.'}), 400

@app.route('/chat', methods=['POST'])
def chat():
    global pdf_content
    data = request.json
    user_query = data.get('query', '')
    
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400
        
    try:
        # Simple RAG: Prepend PDF context if available
        prompt = user_query
        if pdf_content:
            prompt = f"Use the following context from the uploaded PDF to answer the query:\n\nContext:\n{pdf_content}\n\nQuery: {user_query}"
        
        response = model.generate_content(prompt)
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
