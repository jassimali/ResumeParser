from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid  # For generating unique filenames
from ai_model import extract_text_from_pdf, extract_details

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"pdf"}  # Restrict file uploads to PDF only

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only PDFs are allowed."}), 400

    try:
        # Generate a unique filename to avoid conflicts
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        file.save(file_path)

        print(f"✅ File uploaded successfully: {file_path}")

        # Extract text from the resume
        extracted_text = extract_text_from_pdf(file_path)

        if not extracted_text.strip():
            print("❌ Could not extract text from PDF.")
            return jsonify({"error": "Could not extract text from PDF"}), 500

        # Extract structured details
        extracted_details = extract_details(extracted_text)

        # Include extracted raw text in the response
        extracted_details["extracted_text"] = extracted_text

        print("✅ Successfully extracted resume details.")
        return jsonify(extracted_details), 200

    except Exception as e:
        print(f"❌ Server Error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    app.run(debug=True)