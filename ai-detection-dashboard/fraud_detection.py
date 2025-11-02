
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import json
from datetime import datetime
import os

class FraudDetector:
    def __init__(self, model_path=None):
        self.model = self._load_model(model_path)
        self.scaler = StandardScaler()
        self.feature_columns = [
            'amount', 'transaction_hour', 'merchant_risk_score',
            'user_history_score', 'location_risk', 'device_fingerprint'
        ]

    def _load_model(self, model_path):
        """Load pre-trained fraud detection model"""
        if model_path and os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                return pickle.load(f)
        else:
            # Create a demo model
            return RandomForestClassifier(n_estimators=100, random_state=42)

    def detect(self, file_path):
        """Detect fraud in transaction data"""
        try:
            if file_path.lower().endswith('.json'):
                return self._detect_transaction_json(file_path)
            elif file_path.lower().endswith('.csv'):
                return self._detect_batch_csv(file_path)
            else:
                return self._detect_image_document(file_path)
        except Exception as e:
            return {
                'error': str(e),
                'confidence': 0.0,
                'prediction': 'error',
                'timestamp': datetime.now().isoformat()
            }

    def _detect_transaction_json(self, json_path):
        """Detect fraud in single transaction JSON"""
        with open(json_path, 'r') as f:
            transaction_data = json.load(f)

        # Extract features
        features = self._extract_features(transaction_data)

        # Mock prediction (in production, use trained model)
        risk_score = self._calculate_risk_score(features)
        prediction = 'fraudulent' if risk_score > 0.7 else 'legitimate'
        confidence = risk_score if prediction == 'fraudulent' else 1 - risk_score

        return {
            'prediction': prediction,
            'confidence': confidence,
            'risk_score': risk_score,
            'type': 'transaction',
            'file_path': json_path,
            'timestamp': datetime.now().isoformat(),
            'features_analyzed': features,
            'metadata': {
                'model_version': '1.0',
                'detection_method': 'machine_learning_classification'
            }
        }

    def _detect_batch_csv(self, csv_path):
        """Detect fraud in batch of transactions"""
        df = pd.read_csv(csv_path)
        results = []

        for index, row in df.iterrows():
            features = self._extract_features(row.to_dict())
            risk_score = self._calculate_risk_score(features)
            prediction = 'fraudulent' if risk_score > 0.7 else 'legitimate'

            results.append({
                'transaction_id': row.get('transaction_id', index),
                'prediction': prediction,
                'risk_score': risk_score
            })

        fraud_count = sum(1 for r in results if r['prediction'] == 'fraudulent')
        avg_risk_score = sum(r['risk_score'] for r in results) / len(results)

        return {
            'prediction': 'batch_analyzed',
            'confidence': avg_risk_score,
            'type': 'batch',
            'file_path': csv_path,
            'timestamp': datetime.now().isoformat(),
            'total_transactions': len(results),
            'fraudulent_transactions': fraud_count,
            'fraud_rate': fraud_count / len(results),
            'detailed_results': results,
            'metadata': {
                'model_version': '1.0',
                'detection_method': 'batch_ml_classification'
            }
        }

    def _detect_image_document(self, image_path):
        """Detect fraud in document images (e.g., fake IDs, altered documents)"""
        # This would use OCR + image analysis in production
        # For demo, return mock analysis

        import cv2
        image = cv2.imread(image_path)
        height, width = image.shape[:2]

        # Mock document analysis
        authenticity_score = np.random.uniform(0.3, 0.9)
        prediction = 'authentic' if authenticity_score > 0.6 else 'fraudulent'

        return {
            'prediction': prediction,
            'confidence': authenticity_score,
            'type': 'document',
            'file_path': image_path,
            'timestamp': datetime.now().isoformat(),
            'analysis': {
                'image_dimensions': [width, height],
                'authenticity_score': authenticity_score,
                'suspicious_elements': self._detect_suspicious_elements(image)
            },
            'metadata': {
                'model_version': '1.0',
                'detection_method': 'document_image_analysis'
            }
        }

    def _extract_features(self, data):
        """Extract features from transaction data"""
        return {
            'amount': data.get('amount', 0),
            'transaction_hour': data.get('hour', 12),
            'merchant_risk_score': data.get('merchant_risk', 0.5),
            'user_history_score': data.get('user_score', 0.7),
            'location_risk': data.get('location_risk', 0.3),
            'device_fingerprint': hash(str(data.get('device_id', 'unknown'))) % 1000 / 1000
        }

    def _calculate_risk_score(self, features):
        """Calculate risk score based on features"""
        # Mock risk calculation
        score = 0
        score += min(features['amount'] / 10000, 0.3)  # Amount factor
        score += 0.2 if features['transaction_hour'] < 6 or features['transaction_hour'] > 22 else 0
        score += features['merchant_risk_score'] * 0.25
        score += (1 - features['user_history_score']) * 0.15
        score += features['location_risk'] * 0.1

        return min(score, 1.0)

    def _detect_suspicious_elements(self, image):
        """Detect suspicious elements in document image"""
        return [
            'text_inconsistency' if np.random.random() > 0.7 else None,
            'image_tampering' if np.random.random() > 0.8 else None,
            'font_mismatch' if np.random.random() > 0.9 else None
        ]
