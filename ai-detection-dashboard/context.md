# AI Detection & Evidence System - Project Context

## Overview

This project is a web-based dashboard for automated detection and digital forensics, supporting Deepfake, Object, and Fraud detection. It is built using Flask, SQLAlchemy, and Docker, and provides a secure platform for uploading files, running AI-powered analyses, and generating court-ready evidence reports.

---

## Main Features

- **Deepfake Detection:**  
  Detects manipulated images and videos using neural networks.

- **Object Detection:**  
  Uses YOLOv8 to identify and localize objects in images and videos.

- **Fraud Detection:**  
  Flags fraudulent transactions and document images using machine learning.

- **Evidence Report Generation:**  
  Generates PDF reports with chain of custody, technical analysis, and legal certification.

- **User Dashboard:**  
  Tracks recent detections, statistics, and reports.

- **Persistent Storage:**  
  Uses SQLite for storing users, detections, and reports.

---

## Core Components

- [`app.py`](ai-detection-dashboard/app.py):  
  Main Flask app, routes for dashboard, detection, report generation, and API endpoints.

- [`database_models.py`](ai-detection-dashboard/database_models.py):  
  SQLAlchemy models for users, detection results, evidence reports, audit logs, and system config.

- [`deepfake_detection.py`](ai-detection-dashboard/deepfake_detection.py):  
  Deepfake detection logic.

- [`object_detection.py`](ai-detection-dashboard/object_detection.py):  
  Object detection logic using YOLOv8.

- [`fraud_detection.py`](ai-detection-dashboard/fraud_detection.py):  
  Fraud detection for transactions and documents.

- [`evidence_report_generator.py`](ai-detection-dashboard/evidence_report_generator.py):  
  Generates structured evidence reports in PDF format.

- [`config.py`](ai-detection-dashboard/config.py):  
  Configuration for Flask, database, uploads, and model paths.

- [`templates/`](ai-detection-dashboard/templates/):  
  Jinja2 HTML templates for dashboard, detection, and reports.

- [`static/`](ai-detection-dashboard/static/):  
  CSS and JS for UI, including charting and report generation.

---

## Workflow

1. **File Upload:**  
   Users upload files (images, videos, JSON, CSV) via the detection interface.

2. **Detection:**  
   The backend selects the appropriate model (deepfake, object, fraud) and runs analysis.

3. **Result Storage:**  
   Detection results are stored in the database, including confidence and metadata.

4. **Report Generation:**  
   Users can generate evidence reports, which include chain of custody, technical details, and legal statements.

5. **Dashboard & Reports:**  
   Users view statistics, recent detections, and download reports.

---

## Evidence Report Structure

- **Report Identification:**  
  Unique report ID, case info, timestamps.

- **Chain of Custody:**  
  Actions and timestamps for file handling and analysis.

- **Technical Analysis:**  
  Model used, prediction, confidence, method, and version.

- **Legal Certification:**  
  Statements certifying the analysis and integrity.

- **Verification:**  
  File hash and integrity status.

- **Appendices:**  
  Technical details, system info, and methodology.

---

## Technologies Used

- **Backend:** Flask, SQLAlchemy, Python
- **AI Models:** PyTorch, YOLOv8, scikit-learn
- **Frontend:** Bootstrap, Chart.js, custom CSS/JS
- **PDF Generation:** ReportLab
- **Database:** SQLite
- **Containerization:** Docker

---

## Usage

- Run locally with Python or build/run with Docker.
- Access the dashboard at [http://localhost:5000](http://localhost:5000).
- Upload files, analyze, and generate/download evidence reports.

---

## Authors

- Akshat Jasrotia ([GitHub](https://github.com/akshatjasrotia85))
- Priyanshu Rana ([GitHub](https://github.com/priyanshurana))
- Shivong Sharma ([GitHub](https://github.com/shivongsharma))

---

## License

Licensed under CUJ, J&K.
