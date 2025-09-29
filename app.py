from flask import Flask, request, jsonify, render_template, send_file, url_for
from flask_cors import CORS
from model import crop_model
import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

# Correct template and static folder paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, '../frontend')
STATIC_DIR = os.path.join(TEMPLATE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
CORS(app)

# Initialize/load model
print("🌱 Initializing AI Crop Recommendation System...")
if not crop_model.model:
    print("🤖 Training new model...")
    crop_model.train_model()
else:
    print("✅ Model already loaded")

# ----------------- ROUTES -----------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommendation')
def recommendation():
    return render_template('recommendation.html')

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# ----------------- API: Predict Crop -----------------
@app.route('/api/recommend', methods=['POST'])
def recommend_crop():
    try:
        data = request.get_json()
        required_fields = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
            data[field] = int(data[field]) if field in ['N', 'P', 'K'] else float(data[field])

        validations = {
            'N': (0, 140), 'P': (5, 145), 'K': (5, 205),
            'temperature': (8, 44), 'humidity': (14, 100),
            'ph': (3.5, 10), 'rainfall': (20, 300)
        }
        for field, (min_val, max_val) in validations.items():
            if not (min_val <= data[field] <= max_val):
                return jsonify({'error': f'{field} must be between {min_val} and {max_val}'}), 400

        result = crop_model.predict(data)
        if result['crop'] == 'Unknown':
            return jsonify({'error': 'Prediction failed'}), 500

        crop_name = result['crop']
        result.update(crop_model.crop_info.get(crop_name, {
            'image': 'default.jpg',
            'season': 'Varies by region',
            'duration': '90-180 days',
            'water_requirement': 'Medium',
            'soil_type': 'Well-drained soil',
            'ideal_temp': '20-30°C',
            'ideal_rainfall': '100-200 cm',
            'tips': ['Consult local agricultural experts']
        }))
        result['input_parameters'] = data
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ----------------- API: Generate PDF -----------------
@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    try:
        data = request.get_json()
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, textColor=colors.darkgreen, spaceAfter=30)
        heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=12, textColor=colors.darkgreen, spaceAfter=12)

        story = [Paragraph("AI Crop Recommendation Report", title_style), Spacer(1,12)]
        story.append(Paragraph(f"Recommended Crop: <b>{data['crop']}</b>", heading_style))
        story.append(Paragraph(f"AI Confidence: {data['confidence']}%", styles['Normal']))
        story.append(Spacer(1,12))

        # Crop Details Table
        crop_details = [
            ["Season:", data.get('season','N/A')],
            ["Growth Duration:", data.get('duration','N/A')],
            ["Water Requirement:", data.get('water_requirement','N/A')],
            ["Soil Type:", data.get('soil_type','N/A')],
            ["Ideal Temperature:", data.get('ideal_temp','N/A')],
            ["Ideal Rainfall:", data.get('ideal_rainfall','N/A')]
        ]
        table = Table(crop_details, colWidths=[2*inch,3*inch])
        table.setStyle(TableStyle([('FONT',(0,0),(-1,-1),'Helvetica',10), ('BACKGROUND',(0,0),(0,-1),colors.lightgrey), ('ALIGN',(0,0),(-1,-1),'LEFT'), ('GRID',(0,0),(-1,-1),1,colors.black)]))
        story.append(table)
        story.append(Spacer(1,12))

        # Tips
        story.append(Paragraph("Growth Tips", heading_style))
        for tip in data.get('tips', []):
            story.append(Paragraph(f"• {tip}", styles['Normal']))
            story.append(Spacer(1,6))

        # Input parameters table
        story.append(Paragraph("Input Parameters", heading_style))
        input_params = [
            ["Parameter","Value"],
            ["Nitrogen (N)", f"{data['input_parameters']['N']} ppm"],
            ["Phosphorus (P)", f"{data['input_parameters']['P']} ppm"],
            ["Potassium (K)", f"{data['input_parameters']['K']} ppm"],
            ["Temperature", f"{data['input_parameters']['temperature']}°C"],
            ["Humidity", f"{data['input_parameters']['humidity']}%"],
            ["pH Level", f"{data['input_parameters']['ph']}"],
            ["Rainfall", f"{data['input_parameters']['rainfall']} mm"]
        ]
        param_table = Table(input_params, colWidths=[2*inch,2*inch])
        param_table.setStyle(TableStyle([
            ('FONT',(0,0),(-1,0),'Helvetica-Bold',10),
            ('BACKGROUND',(0,0),(-1,0),colors.darkgreen),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('GRID',(0,0),(-1,-1),1,colors.black),
            ('BACKGROUND',(0,1),(-1,-1),colors.beige)
        ]))
        story.append(param_table)

        doc.build(story)
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name=f"crop_recommendation_{data['crop']}.pdf", mimetype='application/pdf')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
