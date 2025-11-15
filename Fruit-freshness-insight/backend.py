# backend.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from app import get_prediction
from PIL import Image
import os

# Get the absolute path to the frontend folder
frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')

app = Flask(__name__, 
            template_folder=frontend_path,
            static_folder=frontend_path,
            static_url_path='')  # This makes static files accessible from root

CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/preview.html')
def preview():
    return render_template('preview.html')

@app.route('/result.html')
def result():
    return render_template('result.html')

@app.route('/predict', methods=['POST'])
def predict():
    print("FILES RECEIVED:", request.files)
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    img = Image.open(file.stream)
    result = get_prediction(img)
    
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
