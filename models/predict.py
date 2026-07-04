import joblib
import pandas as pd

# ===========================
# Load Saved Model
# ===========================
model = joblib.load("heart_model.pkl")

# ===========================
# Enter Patient Details
# ===========================
patient_data = {
    "age": 52,
    "sex": 1,
    "cp": 0,
    "trestbps": 125,
    "chol": 212,
    "fbs": 0,
    "restecg": 1,
    "thalach": 168,
    "exang": 0,
    "oldpeak": 1.0,
    "slope": 2,
    "ca": 0,
    "thal": 2
}

# Convert to DataFrame
input_data = pd.DataFrame([patient_data])

# ===========================
# Predict
# ===========================
prediction = model.predict(input_data)[0]

# Probability
probability = model.predict_proba(input_data)[0]

# ===========================
# Display Result
# ===========================
print("=" * 40)
print("Heart Disease Prediction")
print("=" * 40)

if prediction == 1:
    print("Prediction : HIGH RISK")
    print(f"Confidence: {probability[1] * 100:.2f}%")
else:
    print("Prediction : LOW RISK")
    print(f"Confidence: {probability[0] * 100:.2f}%")

print("=" * 40)