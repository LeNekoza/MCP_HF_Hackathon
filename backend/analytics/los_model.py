"""
Length of Stay (LOS) prediction module.
Provides ML-based LOS predictions and summary statistics.
"""
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pickle
import os
from ..db_utils import db


class LOSPredictor:
    """Machine learning model for predicting length of stay."""
    
    def __init__(self):
        self.model = None
        self.model_path = "models/los_model.pkl"
        self.is_trained = False
        
    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for training/prediction."""
        # Calculate LOS for completed stays
        completed_stays = df.dropna(subset=["discharged_at"]).copy()
        completed_stays["los_days"] = (
            completed_stays["discharged_at"] - completed_stays["assigned_at"]
        ).dt.total_seconds() / 86400
        
        # Filter reasonable LOS values (0-365 days)
        completed_stays = completed_stays[
            completed_stays["los_days"].between(0, 365)
        ]
        
        # Add room type information
        rooms = db.get_rooms()
        room_type_map = rooms.set_index("id")["room_type"].to_dict()
        completed_stays["room_type"] = completed_stays["room_id"].map(room_type_map)
        
        # Classify admission type based on time
        completed_stays["admission_hour"] = completed_stays["assigned_at"].dt.hour
        completed_stays["admission_type"] = np.where(
            completed_stays["admission_hour"].between(8, 17),
            "Elective",
            "Emergency"
        )
        
        # Clean age data
        completed_stays["age_at_adm"] = completed_stays["age_at_adm"].fillna(
            completed_stays["age_at_adm"].median()
        ).clip(lower=0, upper=120)
        
        # Clean gender data
        completed_stays["gender"] = completed_stays["gender"].fillna("Unknown")
        
        return completed_stays
    
    def train(self) -> dict:
        """Train the LOS prediction model."""
        # Get occupancy data
        occupancy = db.get_occupancy(days_back=365)  # Get more data for training
        
        if occupancy.empty:
            return {"error": "No occupancy data available for training"}
        
        # Prepare features
        df = self._prepare_features(occupancy)
        
        if len(df) < 10:
            return {"error": "Insufficient data for training (need at least 10 completed stays)"}
        
        # Feature columns
        feature_cols = ["admission_type", "room_type", "gender", "age_at_adm"]
        
        # Check if all required columns exist
        missing_cols = [col for col in feature_cols if col not in df.columns]
        if missing_cols:
            return {"error": f"Missing columns: {missing_cols}"}
        
        X = df[feature_cols]
        y = df["los_days"]
        
        # Create preprocessing pipeline
        categorical_features = ["admission_type", "room_type", "gender"]
        numerical_features = ["age_at_adm"]
        
        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
                ("num", "passthrough", numerical_features)
            ]
        )
        
        # Create full pipeline
        self.model = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))
        ])
        
        # Train model
        try:
            self.model.fit(X, y)
            self.is_trained = True
            
            # Save model
            os.makedirs("models", exist_ok=True)
            with open(self.model_path, "wb") as f:
                pickle.dump(self.model, f)
            
            # Calculate training metrics
            train_score = self.model.score(X, y)
            
            return {
                "success": True,
                "training_samples": len(df),
                "r2_score": round(train_score, 3),
                "message": "Model trained successfully"
            }
            
        except Exception as e:
            return {"error": f"Training failed: {str(e)}"}
    
    def load_model(self):
        """Load pre-trained model from disk."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    self.model = pickle.load(f)
                self.is_trained = True
                return True
            except Exception:
                return False
        return False
    
    def predict(self, features: dict) -> dict:
        """
        Predict LOS for given patient features.
        
        Args:
            features: Dict with keys: admission_type, room_type, gender, age_at_adm
            
        Returns:
            Dictionary with prediction results.
        """
        if not self.is_trained:
            if not self.load_model():
                # Try to train model if no pre-trained model exists
                train_result = self.train()
                if "error" in train_result:
                    return train_result
        
        try:
            # Convert features to DataFrame
            feature_df = pd.DataFrame([features])
            
            # Make prediction
            prediction = self.model.predict(feature_df)[0]
            
            return {
                "predicted_los_days": round(prediction, 1),
                "confidence": "medium",  # Could add confidence intervals later
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}


def los_summary() -> dict:
    """
    Get LOS summary statistics by ward.
    
    Returns:
        Dictionary with LOS statistics for chart rendering.
    """
    # Get occupancy data
    occupancy = db.get_occupancy(days_back=90)
    
    if occupancy.empty:
        return {
            "data": [],
            "error": "No occupancy data available"
        }
    
    # Prepare LOS data
    los_df = occupancy.dropna(subset=["discharged_at"]).copy()
    los_df["los_days"] = (
        los_df["discharged_at"] - los_df["assigned_at"]
    ).dt.total_seconds() / 86400
    
    # Filter reasonable LOS values
    los_df = los_df[los_df["los_days"].between(0, 365)]
    
    if los_df.empty:
        return {
            "data": [],
            "error": "No completed stays with valid LOS data"
        }
    
    # Add room type information
    rooms = db.get_rooms()
    room_type_map = rooms.set_index("id")["room_type"].to_dict()
    los_df["room_type"] = los_df["room_id"].map(room_type_map)
    
    # Calculate statistics by ward
    ward_stats = los_df.groupby("room_type")["los_days"].agg([
        "mean", "median", "std", "min", "max", "count"
    ]).round(2)
    
    # Format for chart rendering
    data = []
    for ward, stats in ward_stats.iterrows():
        data.append({
            "ward": ward,
            "average_los": float(stats["mean"]),
            "median_los": float(stats["median"]),
            "std_los": float(stats["std"]) if not pd.isna(stats["std"]) else 0,
            "min_los": float(stats["min"]),
            "max_los": float(stats["max"]),
            "patient_count": int(stats["count"])
        })
    
    # Overall statistics
    overall_stats = {
        "total_patients": int(los_df.shape[0]),
        "average_los": round(los_df["los_days"].mean(), 2),
        "median_los": round(los_df["los_days"].median(), 2),
        "analysis_period": "90 days"
    }
    
    return {
        "data": data,
        "overall": overall_stats,
        "timestamp": datetime.now().isoformat()
    }


# Global predictor instance
predictor = LOSPredictor() 