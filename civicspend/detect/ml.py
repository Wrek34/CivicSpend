"""ML anomaly detection using Isolation Forest."""
import joblib
import numpy as np
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from civicspend.features.engineer import FeatureEngineer

class MLDetector:
    """ML-based anomaly detection."""
    
    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        self.contamination = contamination
        self.random_state = random_state
        self.model = None
        self.scaler = None
        self.engineer = FeatureEngineer()
    
    def train(self, run_id: str, min_samples: int = 10):
        """Train Isolation Forest on historical data."""
        # Engineer features
        df = self.engineer.engineer_features(run_id)
        
        if len(df) < min_samples:
            raise ValueError(f"Need at least {min_samples} samples, got {len(df)}")
        
        # Get feature columns
        feature_cols = self.engineer.get_feature_columns()
        X = df[feature_cols].fillna(0).replace([np.inf, -np.inf], 0)
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model = IsolationForest(
            n_estimators=200,
            max_samples=min(256, len(X)),
            contamination=self.contamination,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.model.fit(X_scaled)
        
        return len(X)
    
    def predict(self, run_id: str):
        """Predict anomalies."""
        if self.model is None or self.scaler is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Engineer features
        df = self.engineer.engineer_features(run_id)
        
        if df.empty:
            return []
        
        # Get features
        feature_cols = self.engineer.get_feature_columns()
        X = df[feature_cols].fillna(0).replace([np.inf, -np.inf], 0)
        X_scaled = self.scaler.transform(X)
        
        # Predict
        predictions = self.model.predict(X_scaled)
        scores = self.model.score_samples(X_scaled)
        
        # Extract anomalies
        anomalies = []
        for idx, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:  # Anomaly
                row = df.iloc[idx]
                severity = self._get_severity(score)
                anomalies.append({
                    'vendor_id': row['vendor_id'],
                    'vendor_name': row['canonical_name'],
                    'year_month': row['year_month'],
                    'score': float(score),
                    'severity': severity,
                    'value': float(row['obligation_sum']),
                    'award_count': int(row['award_count'])
                })
        
        return anomalies
    
    def save_model(self, run_id: str):
        """Save trained model."""
        model_dir = Path(f"models/{run_id}")
        model_dir.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.model, model_dir / "isolation_forest.joblib")
        joblib.dump(self.scaler, model_dir / "scaler.joblib")
        
        return str(model_dir)
    
    def load_model(self, run_id: str):
        """Load trained model."""
        model_dir = Path(f"models/{run_id}")
        
        self.model = joblib.load(model_dir / "isolation_forest.joblib")
        self.scaler = joblib.load(model_dir / "scaler.joblib")
    
    def _get_severity(self, score: float) -> str:
        """Map anomaly score to severity."""
        if score < -0.5:
            return 'critical'
        elif score < -0.3:
            return 'high'
        elif score < -0.1:
            return 'medium'
        else:
            return 'low'
