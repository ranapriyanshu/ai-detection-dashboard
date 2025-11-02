from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import json
import uuid
from datetime import datetime, timezone
from deepfake_detection import DeepfakeDetector
from object_detection import ObjectDetector
from fraud_detection import FraudDetector
from evidence_report_generator import EvidenceReportGenerator
from database_models import User, DetectionResult, EvidenceReport,db
import numpy as np
import torch

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)


# Initialize detection models
deepfake_detector = DeepfakeDetector()
object_detector = ObjectDetector()
fraud_detector = FraudDetector()
evidence_generator = EvidenceReportGenerator()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.template_filter('from_json')
def from_json_filter(s):
    try:
        return json.loads(s)
    except Exception:
        return {}

@app.route('/dashboard')
def dashboard():
    # Fake user_id for demo purposes
    user_id = 1
    recent_detections = DetectionResult.query.filter_by(user_id=user_id).order_by(
        DetectionResult.timestamp.desc()).limit(10).all()
    return render_template('dashboard.html', detections=recent_detections)

def convert_tensor_to_native(obj):
    """Recursively convert tensors and numpy arrays to native Python types."""
    try:
        if torch.is_tensor(obj):
            return obj.detach().cpu().tolist()
    except ImportError:
        pass
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: convert_tensor_to_native(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_tensor_to_native(i) for i in obj]
    return obj

@app.route('/detection', methods=['GET', 'POST'])
def detection():
    user_id = 1  # Demo user ID

    if request.method == 'POST':
        try:
            detection_type = request.form.get('detection_type')
            file = request.files.get('file')

            if not file:
                return jsonify({'success': False, 'error': 'No file uploaded'}), 400

            if not allowed_file(file.filename):
                return jsonify({'success': False, 'error': 'Invalid file type'}), 400

            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(file_path)

            result = perform_detection(detection_type, file_path)
            result = convert_tensor_to_native(result)  # <-- Add this line

            detection_result = DetectionResult(
                user_id=user_id,
                file_path=file_path,
                detection_type=detection_type,
                result=json.dumps(result),
                confidence=result.get('confidence', 0.0),
                timestamp=datetime.now(timezone.utc)  # Use UTC with timezone info
            )
            db.session.add(detection_result)
            db.session.commit()

            return jsonify({
                'success': True,
                'result': result,
                'detection_id': detection_result.id
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # For GET request: render HTML
    return render_template('detection.html')
    user_id = 1  # Demo user ID

    if request.method == 'POST':
        try:
            detection_type = request.form.get('detection_type')
            file = request.files.get('file')

            if not file:
                return jsonify({'success': False, 'error': 'No file uploaded'}), 400

            if not allowed_file(file.filename):
                return jsonify({'success': False, 'error': 'Invalid file type'}), 400

            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)

            result = perform_detection(detection_type, file_path)

            detection_result = DetectionResult(
                user_id=user_id,
                file_path=file_path,
                detection_type=detection_type,
                result=json.dumps(result),
                confidence=result.get('confidence', 0.0),
                timestamp=datetime.now(timezone.utc)  # Use UTC with timezone info
            )
            db.session.add(detection_result)
            db.session.commit()

            return jsonify({
                'success': True,
                'result': result,
                'detection_id': detection_result.id
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # For GET request: render HTML
    return render_template('detection.html')

    user_id = 1  # Fake user ID for testing
    if request.method == 'POST':
        detection_type = request.form.get('detection_type')
        file = request.files.get('file')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)

            result = perform_detection(detection_type, file_path)

            detection_result = DetectionResult(
                user_id=user_id,
                file_path=file_path,
                detection_type=detection_type,
                result=json.dumps(result),
                confidence=result.get('confidence', 0.0),
                timestamp=datetime.utcnow()
            )
            db.session.add(detection_result)
            db.session.commit()

            return jsonify({
                'success': True,
                'result': result,
                'detection_id': detection_result.id
            })

    return render_template('detection.html')

@app.route('/generate_report/<int:detection_id>')
def generate_report(detection_id):
    user_id = 1
    detection = DetectionResult.query.get_or_404(detection_id)

    if detection.user_id != user_id:
        flash('Unauthorized access to detection result', 'error')
        return redirect(url_for('dashboard'))

    report_data = evidence_generator.generate_court_report(detection)

    evidence_report = EvidenceReport(
        detection_id=detection_id,
        report_content=json.dumps(report_data),
        generated_at=datetime.now(timezone.utc),  # Use UTC with timezone info
        report_hash=evidence_generator.generate_hash(report_data)
    )
    db.session.add(evidence_report)
    db.session.commit()

    pdf_path = evidence_generator.create_pdf_report(report_data, evidence_report.id)
    abs_pdf_path = os.path.abspath(pdf_path)
    return send_file(abs_pdf_path, as_attachment=True,
                     download_name=f"Evidence_Report_{evidence_report.id}.pdf")

@app.route('/reports')
def reports():
    user_id = 1
    user_detections = DetectionResult.query.filter_by(user_id=user_id).all()
    detection_ids = [d.id for d in user_detections]
    reports = EvidenceReport.query.filter(EvidenceReport.detection_id.in_(detection_ids)).all()
    return render_template('reports.html', reports=reports)

@app.route('/api/detection_stats')
def detection_stats():
    user_id = 1
    stats = {
        'total_detections': DetectionResult.query.filter_by(user_id=user_id).count(),
        'deepfake_detections': DetectionResult.query.filter_by(
            user_id=user_id, detection_type='deepfake').count(),
        'object_detections': DetectionResult.query.filter_by(
            user_id=user_id, detection_type='object').count(),
        'fraud_detections': DetectionResult.query.filter_by(
            user_id=user_id, detection_type='fraud').count(),
        'reports_generated': EvidenceReport.query.join(DetectionResult).filter(
            DetectionResult.user_id == user_id).count()
    }
    return jsonify(stats)

def perform_detection(detection_type, file_path):
    try:
        if detection_type == 'deepfake':
            return deepfake_detector.detect(file_path)
        elif detection_type == 'object':
            return object_detector.detect(file_path)
        elif detection_type == 'fraud':
            return fraud_detector.detect(file_path)
        else:
            return {'error': 'Unknown detection type'}
    except Exception as e:
        return {'error': str(e)}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
