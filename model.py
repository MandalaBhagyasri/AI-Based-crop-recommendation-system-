import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

class CropModel:
    def __init__(self):
        self.model = None
        self.features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        
        # Crop information database (expanded)
        self.crop_info = {
            'Rice': {
                'image': 'rice.jpg',
                'season': 'Kharif (June-September)',
                'duration': '90-150 days',
                'water_requirement': 'High',
                'soil_type': 'Clayey loam',
                'ideal_temp': '20-35°C',
                'ideal_rainfall': '150-300 cm',
                'tips': [
                    'Maintain proper water level (2-5 cm) during vegetative phase',
                    'Use balanced NPK fertilizer in ratio 4:2:1',
                    'Control weeds regularly with proper herbicides',
                    'Ensure proper drainage to prevent waterlogging'
                ]
            },
            'Maize': {
                'image': 'maize.jpg',
                'season': 'Kharif (June-July)',
                'duration': '80-110 days',
                'water_requirement': 'Medium',
                'soil_type': 'Well-drained loamy soil',
                'ideal_temp': '18-27°C',
                'ideal_rainfall': '60-110 cm',
                'tips': [
                    'Plant in rows with 60-75 cm spacing',
                    'Apply nitrogen in split doses',
                    'Ensure good drainage system',
                    'Use hybrid seeds for better yield'
                ]
            },
            'Chickpea': {
                'image': 'chickpea.jpg',
                'season': 'Rabi (October-November)',
                'duration': '90-120 days',
                'water_requirement': 'Low',
                'soil_type': 'Well-drained sandy loam',
                'ideal_temp': '20-25°C',
                'ideal_rainfall': '40-60 cm',
                'tips': [
                    'Sow in well-drained fields',
                    'Treat seeds with rhizobium culture',
                    'Avoid waterlogging conditions',
                    'Harvest when leaves turn yellow'
                ]
            },
            'Kidneybeans': {
                'image': 'kidneybeans.jpg',
                'season': 'Kharif (June-July)',
                'duration': '90-120 days',
                'water_requirement': 'Medium',
                'soil_type': 'Loamy soil',
                'ideal_temp': '15-25°C',
                'ideal_rainfall': '50-75 cm',
                'tips': [
                    'Provide support for climbing varieties',
                    'Maintain soil pH around 6.0-7.5',
                    'Use organic manure for better growth',
                    'Control bean beetles regularly'
                ]
            },
            'Banana': {
                'image': 'banana.jpg',
                'season': 'Year-round',
                'duration': '12-15 months',
                'water_requirement': 'High',
                'soil_type': 'Deep, well-drained loamy soil',
                'ideal_temp': '15-35°C',
                'ideal_rainfall': '150-200 cm',
                'tips': [
                    'Plant suckers from disease-free plants',
                    'Maintain proper irrigation during dry spells',
                    'Use mulch to conserve moisture',
                    'Remove excess suckers regularly'
                ]
            },
            'Cotton': {
                'image': 'cotton.jpg',
                'season': 'Kharif (April-May)',
                'duration': '150-180 days',
                'water_requirement': 'Medium',
                'soil_type': 'Black cotton soil',
                'ideal_temp': '21-30°C',
                'ideal_rainfall': '50-100 cm',
                'tips': [
                    'Use certified seeds for planting',
                    'Control bollworms effectively',
                    'Practice crop rotation',
                    'Harvest when bolls fully open'
                ]
            },
            'Wheat': {
                'image': 'wheat.jpg',
                'season': 'Rabi (October-November)',
                'duration': '120-150 days',
                'water_requirement': 'Medium',
                'soil_type': 'Well-drained loamy soil',
                'ideal_temp': '10-25°C',
                'ideal_rainfall': '50-100 cm',
                'tips': [
                    'Sow at proper time to avoid heat stress',
                    'Use certified seeds for better yield',
                    'Apply irrigation at critical growth stages',
                    'Control rust diseases effectively'
                ]
            },
            'Sugarcane': {
                'image': 'sugarcane.jpg',
                'season': 'Year-round',
                'duration': '12-18 months',
                'water_requirement': 'High',
                'soil_type': 'Deep, well-drained soil',
                'ideal_temp': '20-35°C',
                'ideal_rainfall': '150-200 cm',
                'tips': [
                    'Plant disease-free setts',
                    'Maintain adequate moisture',
                    'Apply balanced fertilizers',
                    'Control pests and diseases regularly'
                ]
            }
        }
        
        # Create crop labels from crop_info keys
        crops_list = list(self.crop_info.keys())
        self.crop_labels = {i: crop for i, crop in enumerate(crops_list)}
        print(f"🌾 Loaded {len(self.crop_labels)} crops: {', '.join(crops_list)}")

    def generate_sample_data(self):
        """Generate realistic crop recommendation dataset"""
        np.random.seed(42)
        n_samples = 2000
        
        # Define parameter ranges for different crops
        crop_params = {
            'Rice': {'N': (50, 120), 'P': (30, 80), 'K': (30, 100), 'temp': (22, 32), 'humidity': (60, 90), 'ph': (5, 7), 'rainfall': (150, 300)},
            'Maize': {'N': (50, 100), 'P': (30, 70), 'K': (30, 90), 'temp': (18, 27), 'humidity': (50, 80), 'ph': (5.5, 7.5), 'rainfall': (60, 110)},
            'Chickpea': {'N': (20, 60), 'P': (20, 50), 'K': (20, 60), 'temp': (15, 25), 'humidity': (40, 70), 'ph': (6, 8), 'rainfall': (40, 60)},
            'Kidneybeans': {'N': (30, 70), 'P': (25, 60), 'K': (30, 70), 'temp': (15, 25), 'humidity': (50, 75), 'ph': (6, 7.5), 'rainfall': (50, 75)},
            'Banana': {'N': (80, 120), 'P': (40, 80), 'K': (80, 120), 'temp': (15, 35), 'humidity': (60, 85), 'ph': (5.5, 7.5), 'rainfall': (150, 200)},
            'Cotton': {'N': (60, 100), 'P': (30, 70), 'K': (40, 90), 'temp': (21, 30), 'humidity': (45, 75), 'ph': (6, 8.5), 'rainfall': (50, 100)},
            'Wheat': {'N': (40, 80), 'P': (20, 60), 'K': (30, 70), 'temp': (10, 25), 'humidity': (40, 75), 'ph': (6, 7.5), 'rainfall': (50, 100)},
            'Sugarcane': {'N': (80, 130), 'P': (40, 90), 'K': (60, 110), 'temp': (20, 35), 'humidity': (50, 85), 'ph': (6, 8), 'rainfall': (150, 250)}
        }
        
        data = []
        crops_list = list(crop_params.keys())
        
        for crop_idx, crop_name in enumerate(crops_list):
            if crop_name not in crop_params:
                continue
                
            params = crop_params[crop_name]
            samples_per_crop = n_samples // len(crop_params)
            
            for _ in range(samples_per_crop):
                data.append({
                    'N': np.random.randint(params['N'][0], params['N'][1]),
                    'P': np.random.randint(params['P'][0], params['P'][1]),
                    'K': np.random.randint(params['K'][0], params['K'][1]),
                    'temperature': np.random.uniform(params['temp'][0], params['temp'][1]),
                    'humidity': np.random.uniform(params['humidity'][0], params['humidity'][1]),
                    'ph': np.random.uniform(params['ph'][0], params['ph'][1]),
                    'rainfall': np.random.uniform(params['rainfall'][0], params['rainfall'][1]),
                    'label': crop_idx
                })
        
        df = pd.DataFrame(data)
        df.to_csv('crop_data.csv', index=False)
        print(f"📊 Generated sample data with {len(df)} records")
        return df

    def train_model(self):
        """Train the Random Forest model"""
        try:
            if os.path.exists('crop_data.csv'):
                df = pd.read_csv('crop_data.csv')
                print("📁 Loaded existing dataset")
            else:
                print("📝 Generating new dataset...")
                df = self.generate_sample_data()
            
            # Ensure we have data
            if df.empty:
                raise ValueError("Generated dataset is empty")
            
            X = df[self.features]
            y = df['label']
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            print("🤖 Training Random Forest model...")
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
            
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            print(f"✅ Model trained successfully! Accuracy: {accuracy:.4f}")
            
            # Save the model
            joblib.dump(self.model, 'crop_model.pkl')
            print("💾 Model saved as crop_model.pkl")
            
            return accuracy
            
        except Exception as e:
            print(f"❌ Error training model: {e}")
            raise

    def load_model(self):
        """Load model safely, retrain if corrupted"""
        try:
            if os.path.exists("crop_model.pkl") and os.path.getsize("crop_model.pkl") > 1000:  # Check file size
                self.model = joblib.load("crop_model.pkl")
                print("✅ Model loaded successfully from crop_model.pkl")
                return True
            else:
                print("⚠️ No valid model found → Training new model...")
                self.train_model()
                return True
        except Exception as e:
            print(f"⚠️ Error loading model: {e} → Retraining...")
            self.train_model()
            return True

    def predict(self, input_data):
        """Predict best crop with probabilities"""
        if self.model is None:
            print("🔄 Model not loaded, loading now...")
            self.load_model()
        
        try:
            # Prepare features in correct order
            features = np.array([[
                input_data['N'],
                input_data['P'], 
                input_data['K'],
                input_data['temperature'],
                input_data['humidity'],
                input_data['ph'],
                input_data['rainfall']
            ]])
            
            prediction = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]
            confidence = np.max(probabilities)
            
            crop_name = self.crop_labels.get(prediction, "Unknown")
            
            return {
                "crop": crop_name,
                "confidence": round(confidence * 100, 2),
                "probability": float(confidence),
                "all_probabilities": {
                    self.crop_labels[i]: float(prob) 
                    for i, prob in enumerate(probabilities) 
                    if i in self.crop_labels and prob > 0.01
                }
            }
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            # Return a default prediction based on conditions
            return self.get_fallback_prediction(input_data)

    def get_fallback_prediction(self, input_data):
        """Fallback prediction when model fails"""
        # Simple rule-based fallback
        temp = input_data['temperature']
        rainfall = input_data['rainfall']
        ph = input_data['ph']
        
        if temp > 30 and rainfall > 200:
            crop = 'Rice'
        elif temp > 25 and rainfall > 100:
            crop = 'Banana' 
        elif temp > 20 and rainfall > 50:
            crop = 'Cotton'
        elif temp > 15:
            crop = 'Wheat'
        else:
            crop = 'Wheat'
            
        return {
            "crop": crop,
            "confidence": 75.0,
            "probability": 0.75,
            "all_probabilities": {crop: 0.75}
        }

# Initialize the model once
crop_model = CropModel()