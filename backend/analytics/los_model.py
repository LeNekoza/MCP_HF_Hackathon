"""
Length of Stay (LOS) prediction and analytics
"""
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from typing import Dict, Any, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
import warnings
from ..database import get_occupancy, get_rooms, get_patients
from ..storage import save_analysis_result, save_model_data

warnings.filterwarnings("ignore", category=FutureWarning)

# Model storage path
MODELS_DIR = Path(__file__).parent.parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True, parents=True)
LOS_MODEL_PATH = MODELS_DIR / "los_predictor.pkl"


class LOSPredictor:
    """Length of Stay prediction model"""
    
    def __init__(self):
        self.model = None
        self.feature_columns = ["admission_type", "room_type", "gender", "age_at_adm"]
        
    def _prepare_data(self) -> tuple:
        """Prepare training data from database"""
        # Load data
        occupancy = get_occupancy()
        rooms = get_rooms()
        patients = get_patients()
        
        # Clean data
        for df in (occupancy, rooms, patients):
            df.drop(columns=[c for c in df.columns if c.startswith("Unnamed")], 
                   inplace=True, errors="ignore")
        
        # Convert datetime columns to proper format
        if 'assigned_at' in occupancy.columns:
            occupancy['assigned_at'] = pd.to_datetime(occupancy['assigned_at'])
        if 'discharged_at' in occupancy.columns:
            occupancy['discharged_at'] = pd.to_datetime(occupancy['discharged_at'])
        
        # Calculate LOS for completed stays
        los_df = occupancy.dropna(subset=["discharged_at"]).copy()
        los_df["los_days"] = (
            los_df.discharged_at - los_df.assigned_at
        ).dt.total_seconds() / 86400
        
        # Add room type mapping
        room_type_map = rooms.set_index("id")["room_type"]
        los_df["room_type"] = los_df["room_id"].map(room_type_map)
        
        # Add admission type (business hours = elective)
        los_df["admission_type"] = np.where(
            los_df.assigned_at.dt.hour.between(8, 17),
            "Elective",
            "Emergency"
        )
        
        # Merge with patient data for demographics
        if 'patient_id' in los_df.columns and len(patients) > 0:
            los_df = los_df.merge(
                patients[['id', 'gender', 'date_of_birth']], 
                left_on='patient_id', 
                right_on='id', 
                how='left',
                suffixes=('', '_patient')
            )
            
            # Calculate age at admission
            if 'date_of_birth' in los_df.columns:
                los_df['age_at_adm'] = (
                    los_df.assigned_at - los_df.date_of_birth
                ).dt.days / 365.25
            else:
                los_df['age_at_adm'] = 50  # Default age
        else:
            # Add default demographics if patient data not available
            los_df['gender'] = np.random.choice(['M', 'F'], len(los_df))
            los_df['age_at_adm'] = np.random.normal(50, 20, len(los_df))
        
        # Filter realistic LOS values (0-365 days)
        los_df = los_df[los_df.los_days.between(0, 365)]
        los_df["age_at_adm"] = los_df["age_at_adm"].clip(lower=0)
        
        # Fill missing values
        los_df = los_df.dropna(subset=self.feature_columns + ["los_days"])
        
        if len(los_df) == 0:
            raise ValueError("No valid LOS data available for training")
        
        X = los_df[self.feature_columns]
        y = los_df["los_days"]
        
        return X, y, los_df
    
    def train(self) -> Dict[str, Any]:
        """Train the LOS prediction model"""
        try:
            X, y, los_df = self._prepare_data()
            
            # Create preprocessing pipeline
            categorical_features = ["admission_type", "room_type", "gender"]
            numerical_features = ["age_at_adm"]
            
            preprocessor = ColumnTransformer(
                transformers=[
                    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
                    ("num", "passthrough", numerical_features)
                ]
            )
            
            # Create model pipeline
            self.model = Pipeline([
                ("prep", preprocessor),
                ("regressor", RandomForestRegressor(
                    n_estimators=100, 
                    random_state=42, 
                    max_depth=10
                ))
            ])
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model
            self.model.fit(X_train, y_train)
            
            # Evaluate
            train_score = self.model.score(X_train, y_train)
            test_score = self.model.score(X_test, y_test)
            cv_scores = cross_val_score(self.model, X, y, cv=5)
            
            # Save model
            with open(LOS_MODEL_PATH, 'wb') as f:
                pickle.dump(self.model, f)
            
            # Extract feature importances from RandomForest
            rf_model = self.model.named_steps['regressor']
            feature_importances = rf_model.feature_importances_.tolist()
            
            # Get feature names after preprocessing
            feature_names = []
            cat_features = self.model.named_steps['prep'].named_transformers_['cat'].get_feature_names_out()
            feature_names.extend(cat_features.tolist())
            feature_names.extend(numerical_features)
            
            training_results = {
                "training_complete": True,
                "train_score": float(train_score),
                "test_score": float(test_score),
                "cv_score_mean": float(cv_scores.mean()),
                "cv_score_std": float(cv_scores.std()),
                "training_samples": len(X),
                "feature_columns": self.feature_columns,
                "feature_importances": dict(zip(feature_names, feature_importances)),
                "model_parameters": {
                    "n_estimators": 100,
                    "max_depth": 10,
                    "random_state": 42
                }
            }
            
            # Save model training results
            save_model_data("los_prediction_training", training_results)
            
            return training_results
            
        except Exception as e:
            error_result = {
                "training_complete": False,
                "error": str(e)
            }
            save_model_data("los_prediction_training", error_result)
            return error_result
    
    def load_model(self) -> bool:
        """Load trained model from disk"""
        try:
            if LOS_MODEL_PATH.exists():
                with open(LOS_MODEL_PATH, 'rb') as f:
                    self.model = pickle.load(f)
                return True
            return False
        except Exception:
            return False
    
    def predict(self, features: Dict[str, Any]) -> float:
        """Predict LOS for given features"""
        if self.model is None:
            if not self.load_model():
                # Train model if not available
                self.train()
        
        # Create DataFrame with features
        feature_df = pd.DataFrame([features])
        
        # Ensure all required columns exist with defaults
        for col in self.feature_columns:
            if col not in feature_df.columns:
                if col == "age_at_adm":
                    feature_df[col] = 50.0
                elif col == "gender":
                    feature_df[col] = "M"
                elif col == "admission_type":
                    feature_df[col] = "Emergency"
                elif col == "room_type":
                    feature_df[col] = "General"
        
        feature_df = feature_df[self.feature_columns]
        
        try:
            prediction = self.model.predict(feature_df)[0]
            return max(0.1, float(prediction))  # Ensure positive LOS
        except Exception:
            return 3.0  # Default LOS


def los_summary(save_results: bool = True) -> Dict[str, Any]:
    """Generate LOS summary statistics by ward"""
    try:
        # Load data
        occupancy = get_occupancy()
        rooms = get_rooms()
        
        # Clean data
        for df in (occupancy, rooms):
            df.drop(columns=[c for c in df.columns if c.startswith("Unnamed")], 
                   inplace=True, errors="ignore")
        
        # Convert datetime columns to proper format
        if 'assigned_at' in occupancy.columns:
            occupancy['assigned_at'] = pd.to_datetime(occupancy['assigned_at'])
        if 'discharged_at' in occupancy.columns:
            occupancy['discharged_at'] = pd.to_datetime(occupancy['discharged_at'])
        
        # Calculate LOS for completed stays
        los_df = occupancy.dropna(subset=["discharged_at"]).copy()
        los_df["los_days"] = (
            los_df.discharged_at - los_df.assigned_at
        ).dt.total_seconds() / 86400
        
        # Add room type
        room_type_map = rooms.set_index("id")["room_type"]
        los_df["room_type"] = los_df["room_id"].map(room_type_map)
        
        # Filter realistic values
        los_df = los_df[los_df.los_days.between(0, 365)]
        
        # Calculate statistics by ward
        ward_stats = los_df.groupby("room_type")["los_days"].agg([
            'mean', 'median', 'std', 'count', 'min', 'max'
        ]).round(2)
        
        # Convert to JSON format
        ward_data = []
        for ward, stats in ward_stats.iterrows():
            ward_data.append({
                "ward_type": ward,
                "avg_los_days": float(stats['mean']),
                "median_los_days": float(stats['median']),
                "std_los_days": float(stats['std']) if pd.notnull(stats['std']) else 0.0,
                "min_los_days": float(stats['min']),
                "max_los_days": float(stats['max']),
                "total_discharges": int(stats['count'])
            })
        
        # Overall statistics
        overall_stats = {
            "overall_avg_los": float(los_df['los_days'].mean()),
            "overall_median_los": float(los_df['los_days'].median()),
            "total_completed_stays": len(los_df),
            "analysis_period_days": (
                los_df.discharged_at.max() - los_df.assigned_at.min()
            ).days if len(los_df) > 0 else 0
        }
        
        result = {
            "ward_statistics": ward_data,
            "overall_statistics": overall_stats,
            "model_available": LOS_MODEL_PATH.exists()
        }
        
        # Save results and model data if requested
        if save_results:
            # Save the result data (JSON)
            save_analysis_result("los_prediction", result)
            
            # Force CSV generation
            save_analysis_result("los_prediction", result, format="csv")
            
            # Save model/analysis data
            model_data = {
                "analysis_type": "los_prediction",
                "statistics_by_ward": ward_data,
                "overall_metrics": overall_stats,
                "model_info": {
                    "model_available": LOS_MODEL_PATH.exists(),
                    "model_path": str(LOS_MODEL_PATH),
                    "feature_columns": ["admission_type", "room_type", "gender", "age_at_adm"]
                },
                "data_quality": {
                    "total_records_analyzed": len(los_df),
                    "valid_los_range": "0-365 days",
                    "analysis_completeness": len(los_df) > 0
                }
            }
            save_model_data("los_prediction", model_data)
        
        return result
        
    except Exception as e:
        error_result = {
            "ward_statistics": [],
            "overall_statistics": {
                "overall_avg_los": 0.0,
                "overall_median_los": 0.0,
                "total_completed_stays": 0,
                "analysis_period_days": 0
            },
            "model_available": False,
            "error": str(e)
        }
        
        if save_results:
            save_analysis_result("los_prediction", error_result)
            save_model_data("los_prediction", {"analysis_type": "los_prediction", "error": str(e)})
        
        return error_result 