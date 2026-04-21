"""Utility script to train and save ML models for FarmersConnect.

Place your training datasets in the `data/` directory and run this script
from the project root. It will produce `models/crop_model.pkl` and
`models/fertilizer_model.pkl`.  A simple example dataset format is shown
below; you should replace it with your own agricultural data.

Crop dataset (CSV):
    nitrogen,phosphorus,potassium,temperature,humidity,ph,rainfall,crop
    90,42,43,20,80,6.5,200,rice
    45,30,27,15,60,7.0,100,wheat

Fertilizer dataset (CSV):
    soil,crop,nitrogen,phosphorus,potassium,fertilizer
    loamy,rice,20,30,40,npk_10_10_10
    sandy,wheat,10,15,20,npk_15_15_15

The script uses scikit-learn RandomForestClassifier by default.
"""

import os
import pickle
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from ml_utils import train_disease_model
# paths
ROOT = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(ROOT, 'models')
DATA_DIR = os.path.join(ROOT, 'data')
DISEASE_DATASET = os.path.join(ROOT, 'DATA_DIR')

os.makedirs(MODELS_DIR, exist_ok=True)


def train_crop_model(csv_path: str, output_path: str):
    df = pd.read_csv(csv_path)
    # features and target must match the columns listed in README above
    X = df[['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = df['crop']
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    with open(output_path, 'wb') as f:
        pickle.dump(clf, f)
    print(f"Saved crop model to {output_path}")


def train_fertilizer_model(csv_path: str, output_path: str):
    df = pd.read_csv(csv_path)
    # encode soil and crop into integers before training
    soil_mapping = {v: i for i, v in enumerate(sorted(df['soil'].unique()))}
    crop_mapping = {v: i for i, v in enumerate(sorted(df['crop'].unique()))}
    df['soil_code'] = df['soil'].map(soil_mapping)
    df['crop_code'] = df['crop'].map(crop_mapping)
    X = df[['soil_code', 'crop_code', 'nitrogen', 'phosphorus', 'potassium']]
    y = df['fertilizer']
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    with open(output_path, 'wb') as f:
        pickle.dump(clf, f)
    print(f"Saved fertilizer model to {output_path}")


if __name__ == "__main__":

    crop_csv = os.path.join(DATA_DIR, "crop_training.csv")
    fert_csv = os.path.join(DATA_DIR, "fertilizer_training.csv")

    plant_model_path = os.path.join(MODELS_DIR, "plant_disease_model.pt")

    train_crop_model(crop_csv, os.path.join(MODELS_DIR, "crop_model.pkl"))
    train_fertilizer_model(fert_csv, os.path.join(MODELS_DIR, "fertilizer_model.pkl"))
    print("Starting disease model training...")
    train_disease_model(DISEASE_DATASET, plant_model_path, epochs=1, batch_size=4)
    print("Disease model training completed.")