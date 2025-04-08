# OCR Service for Ambulance Detection

This is a Flask-based OCR service that uses EasyOCR to extract text from images and updates a Firebase Realtime Database flag based on whether the word "ambulance" is present in the image.

## Folder Structure

ocr-service/
├── app.py
├── requirements.txt
└── README.md


## Setup

1. **Firebase Credentials:**
   - Create a Firebase service account and download the JSON file.
   - In Render, set the following environment variables:
     - `FIREBASE_SERVICE_ACCOUNT_JSON`: Paste the entire JSON string of your service account.
     - `FIREBASE_DATABASE_URL`: Your Firebase Realtime Database URL.

2. **Deployment:**
   - Push this repository to GitHub.
   - In Render, create a new Web Service.
   - Connect your GitHub repository.
   - For the build command, use:
     ```
     pip install -r requirements.txt
     ```
   - For the start command, use:
     ```
     gunicorn app:app --bind 0.0.0.0:$PORT
     ```
   - Render will use the environment variable `PORT` for the service.

## Testing

You can test the service locally by running:

