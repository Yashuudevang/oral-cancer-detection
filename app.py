from flask import Flask, render_template, request, send_file, redirect, url_for
from keras.models import load_model
from keras.preprocessing import image
import numpy as np
from fpdf import FPDF
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import unicodedata
from PIL import Image

app = Flask(__name__)
model = load_model("oral_cancer_model.h5")

UPLOAD_AUDIO_FOLDER = os.path.join("static", "audio")
UPLOAD_IMAGE_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_IMAGE_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_AUDIO_FOLDER, exist_ok=True)

patient_records = []

@app.route('/')
def home():
    return render_template('index.html')

def remove_invalid_chars(text):
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn')

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['image']
    if file:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"{timestamp}_{filename}"
        img_path = os.path.join(UPLOAD_IMAGE_FOLDER, image_filename)
        file.save(img_path)

        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0

        prediction = model.predict(img_array)[0][0]
        confidence = round(prediction * 100, 2)
        pred_class = "High Risk (Cancer)" if prediction < 0.5 else "Low Risk (Non-Cancer)"

        symptoms = {
            "pain_level": request.form.get("pain_level"),
            "bleeding": request.form.get("bleeding"),
            "swelling": request.form.get("swelling"),
            "duration": request.form.get("duration"),
            "history": request.form.get("history")
        }

        patient_records.append({
            "image_path": img_path,
            "prediction": pred_class,
            "confidence": confidence,
            "timestamp": timestamp,
            "symptoms": symptoms,
            "audio_path": None,
            "doctor_message": "",
            "doctor_voice_reply": ""
        })
        print("Saved Record:", patient_records[-1])

        return render_template('result.html', prediction=pred_class, confidence=confidence, image_path=img_path, timestamp=timestamp)

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    return handle_pdf_request()

@app.route('/patient_download_pdf', methods=['POST'])
def patient_download_pdf():
    prediction = request.form.get('prediction')
    confidence = request.form.get('confidence')
    image_path = request.form.get('image_path')
    timestamp = request.form.get('timestamp')

    print("Received timestamp:", timestamp)  # Debug

    symptoms = {}
    for record in patient_records:
        print("Comparing with record:", record["timestamp"])  # Debug
        if record["timestamp"] == timestamp:
            symptoms = record.get("symptoms", {})
            print("Found symptoms:", symptoms)  # Debug
            break

    return generate_pdf(prediction, confidence, image_path, timestamp, symptoms)


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

        pdf.set_fill_color(135, 206, 235)  # Sky blue (RGB)
        pdf.set_text_color(0, 0, 0)  # Black text
        pdf.set_font("Times", 'B', 14)  # Bold Times New Roman
        pdf.cell(200, 10, txt="Oral Cancer patient report", ln=True, align='C', fill=True)
        pdf.set_font("Times", '', 12)  # Reset font to normal after header
        pdf.ln(10)

        
        
        pdf.cell(200, 10, txt=f"Prediction: {prediction}", ln=True)
        pdf.cell(200, 10, txt=f"Confidence: {confidence}%", ln=True)
        pdf.cell(200, 10, txt=f"Timestamp: {timestamp}", ln=True)
        current_y = pdf.get_y() + 5  # small space below last symptom
        pdf.set_draw_color(0, 0, 0)  # black line
        pdf.line(10, current_y, 200, current_y)
        pdf.ln(10)  # move cursor down for spacing after the line

        if symptoms:
            pdf.set_font("Times", "B", 12)
            pdf.cell(200, 10, txt="Symptoms", ln=True)
            pdf.set_font("Times", "", 12)
            pdf.cell(200, 10, txt=f"Pain Level: {symptoms.get('pain_level', '')}", ln=True)
            pdf.cell(200, 10, txt=f"Bleeding: {symptoms.get('bleeding', '')}", ln=True)
            pdf.cell(200, 10, txt=f"Swelling: {symptoms.get('swelling', '')}", ln=True)
            pdf.cell(200, 10, txt=f"Duration: {symptoms.get('duration', '')}", ln=True)
            pdf.cell(200, 10, txt=f"Past History: {symptoms.get('history', '')}", ln=True)
            # Draw a straight horizontal line after symptoms
            current_y = pdf.get_y() + 5  # small space below last symptom
            pdf.set_draw_color(0, 0, 0)  # black line
            pdf.line(10, current_y, 200, current_y)
            pdf.ln(10)  # move cursor down for spacing after the line

            pdf.set_font("Times", "B", 12)
            pdf.cell(200, 10, txt="Patient Uploaded Images", ln=True)

        abs_path = os.path.abspath(image_path)
        if abs_path.lower().endswith('.png'):
            img = Image.open(abs_path).convert('RGB')
            abs_path = abs_path.replace(".png", "_converted.jpg")
            img.save(abs_path)

        pdf.image(abs_path, x=10, y=pdf.get_y(), w=60)
        pdf.ln(70)

        output_path = os.path.join('static', f"report_{timestamp}.pdf")
        pdf.output(output_path)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        print(f"PDF generation error: {e}")
        return f"PDF generation failed: {e}", 500

@app.route("/upload_image", methods=["POST"])
def upload_image():
    image = request.files.get("image")
    if not image or image.filename == "":
        return "No image file uploaded", 400

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"uploaded_{timestamp}.png"
    image_path = os.path.join(UPLOAD_IMAGE_FOLDER, filename)
    image.save(image_path)

    return "Image uploaded successfully"

@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    audio = request.files.get("audio")
    if not audio or audio.filename == "":
        return "No audio file uploaded", 400

    timestamp = request.form.get("timestamp")
    filename = f"audio_{timestamp}.wav"
    audio_path = os.path.join(UPLOAD_AUDIO_FOLDER, filename)
    audio.save(audio_path)

    for record in patient_records:
        if record["timestamp"] == timestamp:
            record["audio_path"] = f"audio/{filename}"
            break

    return "Audio uploaded successfully"

@app.route('/doctor_dashboard')
def doctor_dashboard():
    return render_template('doctor_dashboard.html', records=patient_records)

@app.route("/doctor_reply", methods=["POST"])
def doctor_reply():
    timestamp = request.form["timestamp"]
    message = request.form["message"]
    voice_file = request.files.get("voice_reply")

    voice_reply_path = ""
    if voice_file and voice_file.filename:
        filename = f"doctor_reply_{timestamp}.wav"
        voice_reply_path = os.path.join(UPLOAD_AUDIO_FOLDER, filename)
        voice_file.save(voice_reply_path)

    for record in patient_records:
        if record["timestamp"] == timestamp:
            record["doctor_message"] = message
            record["doctor_voice_reply"] = f"audio/{filename}"
            break

    return "Reply submitted. <a href='/doctor_dashboard'>Go back</a>"

@app.route("/delete_record", methods=["POST"])
def delete_record():
    timestamp = request.form["timestamp"]
    global patient_records
    patient_records = [r for r in patient_records if r["timestamp"] != timestamp]
    return redirect(url_for('doctor_dashboard'))

if __name__ == '__main__':
    # app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))  # use Railway's port or default 5000
    app.run(host="0.0.0.0", port=port)
# if __name__ == "__main__":


