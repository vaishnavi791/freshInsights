# backend.py
from flask import Flask, request, jsonify
from app import get_prediction
from PIL import Image

app = Flask(__name__)

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
