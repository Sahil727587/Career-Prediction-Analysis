# Import necessary libraries
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from imblearn.over_sampling import RandomOverSampler
import warnings
import joblib 
import sys 
import os # NEW: Import os for path manipulation

# Suppress warnings for cleaner deployment logs
warnings.filterwarnings("ignore")

# --- EXECUTION CHECK ---
print("--- STARTING MODEL TRAINING FOR RENDER DEPLOYMENT ---")

# --- DATA LOADING AND CLEANING (THE FINAL FIX) ---

# Construct a robust, absolute path to the data file
# This ensures the script finds the data regardless of the server's execution path.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "dataset.csv")

try:
    # Load dataset using the determined absolute path
    df = pd.read_csv(DATA_PATH) 
    print(f"Dataset successfully loaded from: {DATA_PATH}")
except FileNotFoundError:
    # This block executes if the file is not found, preventing a crash
    print(f"FATAL ERROR: dataset.csv not found at expected path ({DATA_PATH}).")
    sys.exit(1) 

# Define columns to exclude (as per original logic)
columns_to_exclude = [
    "Logical quotient rating", "talenttests taken?", "olympiads",
    "Taken inputs from seniors or elders", "interested in games",
    "Interested Type of Books", "Salary Range Expected", "In a Realtionship?",
    "Salary/work", "Gentle or Tuff behaviour?",
]

# Exclude the specified columns from the dataset
df = df.drop(columns=columns_to_exclude, errors='ignore')

# --- FEATURE ENGINEERING (Must match the app.py logic exactly) ---
df['Knowledge Engineering'] = (df['percentage in Algorithms'] + df['Percentage in Mathematics']) / 2
df['System Engineering'] = (df['Acedamic percentage in Operating Systems'] +
                              df['Percentage in Computer Architecture'] +
                              df['Percentage in Electronics Subjects']) / 3
df['Networks and Security'] = (df['Percentage in Computer Networks'] +
                                 df['Percentage in Communication skills']) / 2
df['Software Development'] = (df['Percentage in Programming Concepts'] +
                                 df['Percentage in Software Engineering']) / 2
df['Professional Development'] = (df['Percentage in Communication skills'] +
                                     df['Percentage in Mathematics']) / 2

# Drop the old, individual percentage columns after new features are created
df = df.drop(columns=[
    'percentage in Algorithms', 'Percentage in Mathematics', 
    'Acedamic percentage in Operating Systems', 'Percentage in Computer Architecture',
    'Percentage in Electronics Subjects', 'Percentage in Computer Networks',
    'Percentage in Programming Concepts', 'Percentage in Software Engineering',
    'Percentage in Communication skills'
], errors='ignore')


# --- PRE-PROCESSING AND ENCODING ---
TARGET_COL = "Suggested Job Role"

# Encode the target labels (LabelEncoder must be saved)
le = LabelEncoder()
df[TARGET_COL] = le.fit_transform(df[TARGET_COL])

# Separate features and target
X = df.drop(TARGET_COL, axis=1)
y = df[TARGET_COL]

# One-hot encode categorical features
X = pd.get_dummies(X)

# Scale features (Scaler must be saved)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Balance the dataset 
ros = RandomOverSampler(random_state=42)
X_resampled, y_resampled = ros.fit_resample(X_scaled, y)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X_resampled, y_resampled, test_size=0.2, random_state=42
)

# --- MODEL TRAINING ---
model = RandomForestClassifier(n_estimators=25, random_state=42)
model.fit(X_train, y_train)

# --- EVALUATION (For deployment logs) ---
test_preds = model.predict(X_test)
test_acc = accuracy_score(y_test, test_preds)
print(f"✅ Model Training Complete. Testing Accuracy: {test_acc:.2f}")
print("-------------------------------------------------------")

# --- ASSET SAVING (CRUCIAL FOR DEPLOYMENT) ---
joblib.dump(model, 'model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(X.columns.tolist(), 'columns.pkl')
joblib.dump(le, 'le.pkl')

print("💾 All 4 assets (model.pkl, scaler.pkl, columns.pkl, le.pkl) saved successfully.")
print("--- TRAINING SCRIPT FINISHED ---")