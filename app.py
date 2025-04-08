import os
import json
from flask import Flask, request, jsonify
import cv2
import easyocr
import numpy as np
import io
from PIL import Image
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

app = Flask(__name__)

# Retrieve Firebase credentials from environment variables.
firebase_service_account_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
firebase_database_url = os.environ.get('FIREBASE_DATABASE_URL')

if not firebase_service_account_json or not firebase_database_url:
    raise ValueError("Missing Firebase environment variables. Please set FIREBASE_SERVICE_ACCOUNT_JSON and FIREBASE_DATABASE_URL.")

# Parse the JSON string for the service account details.
service_account_info = json.loads(firebase_service_account_json)

cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred, {
    'databaseURL': firebase_database_url
})

# Define the Firebase database reference for ambulance flag.
firebase_ref = db.reference('/ambulance_flag_A')  # For example, change as needed

# Initialize EasyOCR Reader (using CPU)
reader = easyocr.Reader(['en'], gpu=False)

def process_image(image_data):
    """
    Process the input image data using EasyOCR to extract text.
    Returns the extracted text in lowercase.
    """
    try:
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    except Exception as e:
        raise ValueError(f"Invalid image data: {e}")
    
    results = reader.readtext(image_cv, detail=0)
    extracted_text = " ".join(results).lower()
    return extracted_text

@app.route('/detect', methods=['POST'])
def detect():
    """
    Accepts a POST request with:
      - an image file (key 'image')
      - a 'road' parameter (e.g., 'A' or 'B')
    
    Processes the image via OCR, checks for the word "ambulance", and updates the 
    corresponding Firebase node (e.g., '/ambulance_flag_A').
    Returns a JSON response with the extracted text and the flag status.
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    road = request.form.get('road')
    if road is None or road.upper() not in ["A", "B"]:
        return jsonify({'error': "Missing or invalid 'road' parameter. Use 'A' or 'B'."}), 400

    file = request.files['image']
    image_data = file.read()

    try:
        text = process_image(image_data)
    except Exception as e:
        return jsonify({'error': f"OCR processing failed: {str(e)}"}), 500

    ambulance_detected = "ambulance" in text
    a_flag = "0"

    if(ambulance_detected):
        a_flag = "1"


    # Update the Firebase node based on the road parameter.
    firebase_ref = db.reference(f'/ambulance_flag_{road.upper()}')
    firebase_ref.set({
        "fa": a_flag,
    })

    return jsonify({
        "extracted_text": text,
        "ambulance_detected": ambulance_detected,
        "road": road.upper()
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT env variable
    app.run(host="0.0.0.0", port=port)

