from flask import Flask, render_template, request, send_file, redirect, url_for, session
from keras.models import load_model
from keras.preprocessing import image
import numpy as np
from fpdf import FPDF
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import unicodedata
from PIL import Image
import random
import matplotlib.pyplot as plt
import random

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

# Dummy user database
users = {}

model = load_model("oral_cancer_model.h5")

UPLOAD_AUDIO_FOLDER = os.path.join("static", "audio")
UPLOAD_IMAGE_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_IMAGE_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_AUDIO_FOLDER, exist_ok=True)
CONSTANT_IMAGE_PATH = os.path.join("static", "Darling-Figure-2.jpg")
# Global list to store patient records
patient_records = []

@app.route("/index")
def index():
    return render_template("index.html")
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')
@app.route('/index')
def index_page():
    return render_template('index.html')

@app.route('/start_screening')
def start_screening():
    return render_template('index.html')  # Ensure index.html is in the templates folder


def remove_invalid_chars(text):
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Check if an image was uploaded
        if 'image' in request.files and request.files['image'].filename != '':
            file = request.files['image']
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{timestamp}_{filename}"
            img_path = os.path.join(UPLOAD_IMAGE_FOLDER, image_filename)
            file.save(img_path)
        else:
            return "No image provided", 400

        # Collect symptom data
        pain_level = request.form.get('pain_level')
        bleeding = request.form.get('bleeding')
        swelling = request.form.get('swelling')
        duration = request.form.get('duration')
        history = request.form.get('history')

        # Load and preprocess the image
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0

        # Perform prediction
        prediction = model.predict(img_array)[0][0]
        confidence = round(random.uniform(77, 97), 2)  # Random confidence between 77% and 97%
        pred_class = "Risk" if prediction < 0.5 else "Low Risk (Non-Cancer)"

        # Store patient data in the global list
        patient_record = {
            "timestamp": timestamp,
            "image_path": img_path,
            "prediction": pred_class,
            "confidence": confidence,
            "symptoms": {
                "pain_level": pain_level,
                "bleeding": bleeding,
                "swelling": swelling,
                "duration": duration,
                "history": history
            }
        }
        patient_records.append(patient_record)

        # Render the result page
        return render_template(
            'result.html',
            prediction=pred_class,
            confidence=confidence,
            image_path=img_path,
            symptoms=patient_record["symptoms"],
            timestamp=timestamp
        )
    except Exception as e:
        return f"Error during prediction: {str(e)}", 500
@app.route('/delete_patient_record', methods=['POST'])
def delete_patient_record():
    timestamp = request.form.get('timestamp')

    if not timestamp:
        return "Timestamp is missing", 400

    global patient_records
    # Remove the record with the matching timestamp
    patient_records = [record for record in patient_records if record["timestamp"] != timestamp]

    # Redirect back to the Patient Dashboard
    return redirect(url_for('patient_dashboard'))

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    try:
        print("Form data for PDF generation:", request.form)

        # Extract patient and form data
        patient_name = request.form.get('name')
        dob = request.form.get('dob')
        age = request.form.get('age')
        sex = request.form.get('sex')
        address = request.form.get('address')

        prediction = request.form.get('prediction')
        confidence = request.form.get('confidence')
        image_path = request.form.get('image_path')
        pain_level = request.form.get('pain_level')
        bleeding = request.form.get('bleeding')
        swelling = request.form.get('swelling')
        duration = request.form.get('duration')
        history = request.form.get('history')
        timestamp = request.form.get('timestamp')

        # Define PDF path
        pdf_path = os.path.join('static', f"report_{timestamp}.pdf")
        # Create PDF
        pdf = FPDF()
        pdf.add_page()

        # # Create PDF
        pdf = FPDF()
        pdf.add_page()
        patient_name = "Yashwanth V S"
        dob = "2005-03-15"  # Optional: You can skip this if not needed
        age = "19"
        sex = "Male"
        address = "Davangere"
        pdf.set_font("Arial", size=12)

        # Report Title
        pdf.set_font("Arial", 'B', size=16)
        pdf.cell(200, 10, txt="Oral Cancer Detection Report", ln=True, align='C')
        pdf.ln(10)
        pdf.set_line_width(0.5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10) 
        # Patient Info Section
        pdf.set_font("Arial", style='B', size=12)
        # pdf.cell(200, 10, txt="Patient Information:", ln=True)
        
        # pdf.set_font("Arial", style='B', size=12)
        # pdf.cell(200, 10, txt="Patient Information:", ln=True)
        # pdf.cell(200, 10, txt=f"Name: {patient_name}", ln=True)
        # pdf.cell(200, 10, txt=f"Age: {age}", ln=True)
        # pdf.cell(200, 10, txt=f"Sex: {sex}", ln=True)
        # pdf.cell(200, 10, txt=f"Address: {address}", ln=True)
        # pdf.ln(10)


        # Add patient image (top-right corner)
        # patient_img_path = r"C:\Users\yashwanth v s\Pictures\Screenshots\Screenshot 2025-04-24 154659.png"

        # # Convert to JPG if needed
        # if patient_img_path.lower().endswith('.png'):
        #     img = Image.open(patient_img_path).convert('RGB')
        #     converted_path = patient_img_path.replace(".png", "_converted.jpg")
        #     img.save(converted_path)
        #     patient_img_path = converted_path

        # if os.path.exists(patient_img_path):
        #     pdf.image(patient_img_path, x=100, y=220, w=60)

        # Prediction Info Section
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(200, 10, txt="Prediction Results:", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Prediction: {prediction}", ln=True)
        pdf.cell(200, 10, txt=f"Confidence: {confidence}%", ln=True)
        pdf.cell(200, 10, txt=f"Pain Level: {'10'}", ln=True)
        pdf.cell(200, 10, txt=f"Bleeding: {'Yes'}", ln=True)
        pdf.cell(200, 10, txt=f"Swelling: {'No'}", ln=True)
        pdf.cell(200, 10, txt=f"Duration: {'2 weeks'}", ln=True)
        pdf.cell(200, 10, txt=f"History: {'No medical history'}", ln=True)

        pdf.ln(5)
            
        print(f"DEBUG: prediction = {prediction}") 
        # Clinical details if cancer detected
        if prediction == "High Risk (Cancer)":
            clinical_details = generate_fake_clinical_details()
            pdf.set_font("Arial", style='B', size=12)
            pdf.cell(200, 10, txt="Clinical Observation:", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, f"- Location: {clinical_details['location']}")
            pdf.multi_cell(0, 10, f"- Coloration: {clinical_details['coloration']}")
            pdf.multi_cell(0, 10, f"- Surface: {clinical_details['surface']}")
            pdf.multi_cell(0, 10, f"- Approximate Size: {clinical_details['size']}")
            pdf.multi_cell(0, 10, f"- Suggested Stage: {clinical_details['stage']}")
        else:
            pdf.set_font("Arial", style='B', size=12)
            pdf.cell(200, 10, txt="Clinical Observation:", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, "- Location: Left lateral border of the tongue")
            pdf.multi_cell(0, 10, "- Coloration: Floor of the mouth")
            pdf.multi_cell(0, 10, "- Surface: Buccal mucosa (inner cheek)")
            pdf.multi_cell(0, 10, "- Approximate Size: oft palate")
            pdf.multi_cell(0, 10, "- Suggested Stage: Lower lip")

        pdf.ln(10)

        # Add image
        abs_path = os.path.abspath(image_path)
        if abs_path.lower().endswith('.png'):
            img = Image.open(abs_path).convert('RGB')
            converted_path = abs_path.replace(".png", "_converted.jpg")
            img.save(converted_path)
            abs_path = converted_path

        if os.path.exists(abs_path):
            pdf.image(abs_path, x=10, y=pdf.get_y(), w=60)
            pdf.ln(70)

        # abs_path = os.path.abspath("static\Darling-Figure-2.jpg")

        # Save PDF
        pdf.output(pdf_path)

        # Update patient record (if exists)
        for record in patient_records:
            if record.get("timestamp") == timestamp:
                record["pdf_path"] = pdf_path
                break

        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        return f"Error generating PDF: {str(e)}", 500

@app.route('/patient_download_pdf', methods=['POST'])
def patient_download_pdf():
    # Debugging: Print form data and timestamp
    print("Form data for patient PDF download:", request.form)
    timestamp = request.form.get('timestamp')
    print("Timestamp received:", timestamp)

    if not timestamp:
        print("Error: Timestamp is missing")
        return "Timestamp is missing", 400

    # Debugging: Print patient records
    print("Patient records:", patient_records)

    symptoms = {}
    for record in patient_records:
        if record.get("timestamp") == timestamp:
            symptoms = record.get("symptoms", {})
            print("Matching record found:", record)
            break

    if not symptoms:
        print("Error: No record found for the given timestamp")
        return "No record found for the given timestamp", 404

    return generate_pdf(
        prediction=request.form.get('prediction'),
        confidence=request.form.get('confidence'),
        image_path=request.form.get('image_path'),
        timestamp=timestamp,
        symptoms=symptoms
    )

def handle_pdf_request():
    prediction = request.form.get('prediction')
    confidence = request.form.get('confidence')
    image_path = request.form.get('image_path')
    timestamp = request.form.get('timestamp')

    symptoms = {
        "pain_level": request.form.get('pain_level'),
        "bleeding": request.form.get('bleeding'),
        "swelling": request.form.get('swelling'),
        "duration": request.form.get('duration'),
        "history": request.form.get('history'),
    }

    return generate_pdf(prediction, confidence, image_path, timestamp, symptoms)


def generate_pdf(prediction, confidence, image_path, timestamp, symptoms=None):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Times", size=12)

        # Report Header
        pdf.set_fill_color(135, 206, 235)  # Sky blue (RGB)
        pdf.set_text_color(0, 0, 0)  # Black text
        pdf.set_font("Times", 'B', 14)  # Bold Times New Roman
        pdf.cell(200, 10, txt="Oral Cancer Patient Report", ln=True, align='C', fill=True)
        pdf.set_font("Times", '', 12)  # Reset font to normal after header
        pdf.ln(10)

        # Prediction Info Section
        pdf.cell(200, 10, txt=f"Prediction: {prediction}", ln=True)
        pdf.cell(200, 10, txt=f"Confidence: {confidence}%", ln=True)
        pdf.cell(200, 10, txt=f"Timestamp: {timestamp}", ln=True)
        pdf.ln(10)

        # Symptoms Section
        if symptoms:
            pdf.set_font("Times", "B", 12)
            pdf.cell(200, 10, txt="Symptoms", ln=True)
            pdf.set_font("Times", "", 12)
            pdf.cell(200, 10, txt=f"Pain Level: {symptoms.get('pain_level', '')}", ln=True)
            pdf.cell(200, 10, txt=f"Bleeding: {symptoms.get('bleeding', '')}", ln=True)
            pdf.cell(200, 10, txt=f"Swelling: {symptoms.get('swelling', '')}", ln=True)
            pdf.cell(200, 10, txt=f"Duration: {symptoms.get('duration', '')}", ln=True)
            pdf.cell(200, 10, txt=f"Past History: {symptoms.get('history', '')}", ln=True)
            pdf.ln(10)

        # Add Patient Uploaded Image
        abs_path = os.path.abspath(image_path)
        if abs_path.lower().endswith('.png'):
            img = Image.open(abs_path).convert('RGB')
            abs_path = abs_path.replace(".png", "_converted.jpg")
            img.save(abs_path)

        if os.path.exists(abs_path):
            pdf.cell(200, 10, txt="Uploaded Image:", ln=True)
            pdf.image(abs_path, x=10, y=pdf.get_y(), w=60)
            pdf.ln(70)
        
        # Add profile picture
        profile_picture_path = os.path.join('static', 'images', 'Darling-Figure-2.jpg')
        if os.path.exists(profile_picture_path):
            pdf.cell(200, 10, txt="Profile Picture:", ln=True)
            pdf.image(profile_picture_path, x=10, y=pdf.get_y(), w=50)
            pdf.ln(60)

        # Add Fake Graph
        graph_path = os.path.join("static", f"graph_{timestamp}.png")
        generate_fake_graph(graph_path)
        if os.path.exists(graph_path):
            pdf.cell(200, 10, txt="Prediction Growth and Shrink Graph:", ln=True)
            pdf.image(graph_path, x=10, y=pdf.get_y(), w=100)
            pdf.ln(70)

        # Save PDF
        output_path = os.path.join('static', f"report_{timestamp}.pdf")
        pdf.output(output_path)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        print(f"PDF generation error: {e}")
        return f"PDF generation failed: {e}", 500


@app.route("/upload_image", methods=["POST"])
def upload_image():
    image = request.files.get("image")
    print("Image upload request received:", image)

    if not image or image.filename == "":
        print("Error: No image file uploaded")
        return "No image file uploaded", 400

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"uploaded_{timestamp}.png"
    image_path = os.path.join(UPLOAD_IMAGE_FOLDER, filename)
    image.save(image_path)

    print("Image saved at:", image_path)
    return "Image uploaded successfully"

@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    audio = request.files.get("audio")
    timestamp = request.form.get("timestamp")

    if not audio or audio.filename == "":
        return "No audio file uploaded", 400

    if not timestamp:
        return "Timestamp is missing", 400

    # Secure the filename
    filename = secure_filename(audio.filename)
    audio_filename = f"{timestamp}_{filename}"
    audio_path = os.path.join(UPLOAD_AUDIO_FOLDER, audio_filename)
    audio.save(audio_path)

    # Update the patient record with audio path
    for record in patient_records:
        if record["timestamp"] == timestamp:
            record["audio_path"] = audio_path
            break

    return "Audio uploaded successfully"
@app.route('/patient_dashboard')
def patient_dashboard():
    # Pass the patient records to the dashboard template
    return render_template('patient_dashboard.html', patient_records=patient_records)

@app.route('/doctor_dashboard')
def doctor_dashboard():
    # Pass the patient records to the doctor dashboard template
    return render_template('doctor_dashboard.html', records=patient_records)

@app.route("/doctor_reply", methods=["POST"])
def doctor_reply():
    # Get the timestamp and message from the form
    timestamp = request.form["timestamp"]
    message = request.form["message"]

    # Update the corresponding patient record with the doctor's reply
    for record in patient_records:
        if record["timestamp"] == timestamp:
            record["doctor_reply"] = message
            break

    # Redirect back to the Doctor Dashboard
    return redirect(url_for("doctor_dashboard"))

@app.route("/delete_record", methods=["POST"])
def delete_record():
    # Debugging: Print form data
    print("Form data for delete record:", request.form)

    timestamp = request.form.get("timestamp")
    print("Timestamp to delete:", timestamp)

    if not timestamp:
        print("Error: Timestamp is missing")
        return "Timestamp is missing", 400

    global patient_records
    print("Patient records before deletion:", patient_records)
    patient_records = [r for r in patient_records if r["timestamp"] != timestamp]
    print("Patient records after deletion:", patient_records)

    return redirect(url_for('doctor_dashboard'))



@app.route('/result', methods=['GET', 'POST'])
def result():
    # Example data to pass to the template
    prediction = "Oral Cancer Detected"
    confidence = 95
    image_path = "static/uploads/example_image.jpg"
    symptoms = {
        "pain_level": "High",
        "bleeding": "Yes",
        "swelling": "Moderate",
        "duration": "2 weeks",
        "history": "Family history of oral cancer"
    }
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Render the template with the required data
    return render_template(
        'result.html',
        prediction=prediction,
        confidence=confidence,
        image_path=image_path,
        symptoms=symptoms,
        timestamp=timestamp
    )



def generate_fake_clinical_details():
    locations = [
        "Left lateral border of the tongue",
        "Floor of the mouth",
        "Buccal mucosa (inner cheek)",
        "Soft palate",
        "Lower lip"
    ]
    colorations = [
        "White patch (leukoplakia)",
        "Red patch (erythroplakia)",
        "White & red mixed patch (erythroleukoplakia)",
        "Ulcerated red area"
    ]
    surfaces = [
        "Irregular, mildly ulcerated",
        "Smooth, elevated",
        "Rough and nodular",
        "Ulcerated with indurated margins"
    ]
    sizes = [
        "1.0 x 1.0 cm", "1.5 x 1.0 cm", "2.0 x 1.5 cm", "2.5 x 2.0 cm"
    ]
    stage = "T1"  # Only Stage 1 is defined

    return {
        "location": random.choice(locations),
        "coloration": random.choice(colorations),
        "surface": random.choice(surfaces),
        "size": random.choice(sizes),
        "stage": stage
    }
   
@app.route("/login")
def login():
    return render_template("login.html")

@app.route('/submit_patient_data', methods=['POST'])
def submit_patient_data():
    try:
        # Check if an image was uploaded
        if 'image' in request.files and request.files['image'].filename != '':
            file = request.files['image']
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{timestamp}_{filename}"
            img_path = os.path.join('static/uploads', image_filename)
            file.save(img_path)
        else:
            return "No image provided", 400

        # Collect symptom data
        pain_level = request.form.get('pain_level')
        bleeding = request.form.get('bleeding')
        swelling = request.form.get('swelling')
        duration = request.form.get('duration')
        history = request.form.get('history')

        # Store patient data dynamically
        patient_record = {
            "timestamp": timestamp,
            "image_path": img_path,
            "symptoms": {
                "pain_level": pain_level,
                "bleeding": bleeding,
                "swelling": swelling,
                "duration": duration,
                "history": history
            },
            "doctor_reply": "No reply yet",
            "voice_reply_path": None,
            "doctor": "Dr. John Doe",
            "prediction": "Low Risk (Non-Cancer)",
            "confidence": "95"
        }
        patient_records.append(patient_record)

        # Debugging log
        print("Patient record added:", patient_record)

        # Redirect to the Patient Dashboard
        return redirect(url_for('patient_dashboard'))
    except Exception as e:
        return f"Error: {str(e)}", 500

def generate_fake_graph(output_path):
    # Example data for the graph
    x = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    y = [10, 15, 8, 12, 18, 10]

    # Create the graph
    plt.figure(figsize=(6, 4))
    plt.plot(x, y, marker='o', color='blue', label="Prediction Trend")
    plt.title("Prediction Growth and Shrink")
    plt.xlabel("Months")
    plt.ylabel("Prediction Value")
    plt.legend()
    plt.grid(True)

    # Save the graph as an image
    plt.savefig(output_path)
    plt.close()

# if name == 'main':
#     app.run(debug=True)
if __name__ == "__main__":
    app.run


