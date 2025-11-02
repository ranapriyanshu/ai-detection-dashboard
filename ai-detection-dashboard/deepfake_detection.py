
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import cv2
import numpy as np
from datetime import datetime
import os

class DeepfakeDetector:
    def __init__(self, model_path=None, device=None):
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._load_model(model_path)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def _load_model(self, model_path):
        """Load pre-trained deepfake detection model"""
        # For demo purposes, using a simple CNN architecture
        # In production, use a more sophisticated model like ResNeXt + LSTM
        model = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(64, 2),  # Real vs Fake
            nn.Softmax(dim=1)
        )

        if model_path and os.path.exists(model_path):
            model.load_state_dict(torch.load(model_path, map_location=self.device))

        model.to(self.device)
        model.eval()
        return model

    def detect(self, file_path):
        """Detect if media is deepfake or real"""
        try:
            if file_path.lower().endswith(('.mp4', '.avi', '.mov')):
                return self._detect_video(file_path)
            else:
                return self._detect_image(file_path)
        except Exception as e:
            return {
                'error': str(e),
                'confidence': 0.0,
                'prediction': 'error',
                'timestamp': datetime.now().isoformat()
            }

    def _detect_image(self, image_path):
        """Detect deepfake in image"""
        image = Image.open(image_path).convert('RGB')
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(input_tensor)
            confidence = float(torch.max(output, 1)[0])
            prediction = 'fake' if torch.argmax(output, 1).item() == 1 else 'real'

        return {
            'prediction': prediction,
            'confidence': confidence,
            'type': 'image',
            'file_path': image_path,
            'timestamp': datetime.now().isoformat(),
            'metadata': {
                'model_version': '1.0',
                'detection_method': 'CNN_classification'
            }
        }

    def _detect_video(self, video_path):
        """Detect deepfake in video by analyzing frames"""
        cap = cv2.VideoCapture(video_path)
        frame_predictions = []
        frame_count = 0

        while cap.read()[0]:
            frame_count += 1

        cap.release()
        cap = cv2.VideoCapture(video_path)

        # Sample frames for analysis
        sample_interval = max(1, frame_count // 30)  # Sample ~30 frames
        current_frame = 0

        while cap.read()[0]:
            ret, frame = cap.read()
            if not ret:
                break

            if current_frame % sample_interval == 0:
                # Convert frame to PIL Image
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)

                # Detect on frame
                input_tensor = self.transform(pil_image).unsqueeze(0).to(self.device)
                with torch.no_grad():
                    output = self.model(input_tensor)
                    confidence = float(torch.max(output, 1)[0])
                    prediction = 'fake' if torch.argmax(output, 1).item() == 1 else 'real'
                    frame_predictions.append((prediction, confidence))

            current_frame += 1

        cap.release()

        # Aggregate results
        fake_predictions = [p for p in frame_predictions if p[0] == 'fake']
        avg_confidence = sum([p[1] for p in frame_predictions]) / len(frame_predictions) if frame_predictions else 0.0
        overall_prediction = 'fake' if len(fake_predictions) > len(frame_predictions) / 2 else 'real'

        return {
            'prediction': overall_prediction,
            'confidence': avg_confidence,
            'type': 'video',
            'file_path': video_path,
            'timestamp': datetime.now().isoformat(),
            'metadata': {
                'total_frames': frame_count,
                'analyzed_frames': len(frame_predictions),
                'fake_frame_ratio': len(fake_predictions) / len(frame_predictions) if frame_predictions else 0,
                'model_version': '1.0',
                'detection_method': 'frame_sampling_CNN'
            }
        }
