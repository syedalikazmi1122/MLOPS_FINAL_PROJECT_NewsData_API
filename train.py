#!/usr/bin/env python3
"""
Model Training Script with MLflow Tracking.

This script:
- Loads processed earthquake data
- Trains time-series prediction models
- Tracks experiments with MLflow (hyperparameters, metrics, models)
- Saves best model to MLflow Model Registry

Predictive Task: Predict next earthquake magnitude or time until next earthquake
(Time-series forecasting for earthquake prediction)

Usage:
    python train.py --data data/processed/earthquakes_processed.parquet
    python train.py --data data/processed/earthquakes_processed.parquet --experiment-name earthquake_prediction
"""

import argparse
import os
import pickle
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature


def load_data(data_path: str) -> pd.DataFrame:
    """Load processed earthquake data."""
    print(f"[train] Loading data from {data_path}...")
    df = pd.read_parquet(data_path)
    print(f"[train] Loaded {len(df)} rows, {len(df.columns)} columns")
    return df


def prepare_features(df: pd.DataFrame, target: str = 'magnitude', log_transform_target: bool = False) -> tuple:
    """
    Prepare features and target for training.
    
    Args:
        df: DataFrame with all features
        target: Target variable ('magnitude' or 'time_since_last')
        log_transform_target: Whether to apply log transformation to target
    
    Returns:
        X (features), y (target), feature_names, transform_info
    """
    print(f"[train] Preparing features for target: {target}")
    
    # Exclude non-feature columns
    exclude_cols = [
        'id', 'time', 'datetime', 'place', 'event_type', 'status',
        'mag_type', 'tsunami', 'significance', 'gap', 'dmin', 'rms', 'nst',
        'year', 'month', 'day', 'hour', 'day_of_week', 'day_of_year', 'week_of_year'  # Use cyclical encodings instead
    ]
    
    # If predicting magnitude, exclude magnitude-related lags that would cause leakage
    if target == 'magnitude':
        exclude_cols.extend(['magnitude', 'mag_lag1', 'mag_lag2', 'mag_lag3'])
        # Use time_since_last as feature (time since previous earthquake)
        # Use rolling statistics from previous earthquakes
    else:
        # For time prediction, we can use current magnitude
        # But exclude the current time_since_last (it's what we're predicting)
        exclude_cols.extend(['time_since_last'])
        # Keep time_since_last_lag features as they're historical
    
    # Select feature columns
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    # Remove any remaining non-numeric columns
    feature_cols = [col for col in feature_cols if df[col].dtype in ['int64', 'float64']]
    
    X = df[feature_cols].copy()
    y = df[target].copy()
    
    # Handle missing values
    X = X.fillna(X.median())
    y = y.fillna(y.median())
    
    # Apply log transformation if requested (useful for skewed targets)
    transform_info = {'log_transform': False, 'y_original_mean': y.mean()}
    if log_transform_target:
        # Ensure all values are positive
        y_min = y.min()
        if y_min <= 0:
            y = y - y_min + 0.001  # Shift to make all positive
        y = np.log1p(y)  # log(1+x) to handle zeros better
        transform_info['log_transform'] = True
        transform_info['y_shift'] = y_min - 0.001 if y_min <= 0 else 0
        print(f"[train] Applied log transformation to target")
    
    print(f"[train] Selected {len(feature_cols)} features")
    print(f"[train] Features: {feature_cols[:10]}..." if len(feature_cols) > 10 else f"[train] Features: {feature_cols}")
    print(f"[train] Target stats - Mean: {y.mean():.4f}, Std: {y.std():.4f}, Min: {y.min():.4f}, Max: {y.max():.4f}")
    
    return X, y, feature_cols, transform_info


def train_model(X_train, y_train, X_val, y_val, model_type: str = 'random_forest', transform_info: dict = None, **kwargs):
    """
    Train a model and return it with metrics.
    
    Args:
        X_train, y_train: Training data
        X_val, y_val: Validation data
        model_type: Type of model ('random_forest', 'gradient_boosting', 'linear')
        transform_info: Dictionary with transformation info (for inverse transform)
        **kwargs: Model hyperparameters
    
    Returns:
        Trained model, metrics dict
    """
    print(f"[train] Training {model_type} model...")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    
    # Initialize model
    if model_type == 'random_forest':
        model = RandomForestRegressor(
            n_estimators=kwargs.get('n_estimators', 100),
            max_depth=kwargs.get('max_depth', 10),
            min_samples_split=kwargs.get('min_samples_split', 2),
            random_state=42,
            n_jobs=-1
        )
    elif model_type == 'gradient_boosting':
        model = GradientBoostingRegressor(
            n_estimators=kwargs.get('n_estimators', 100),
            max_depth=kwargs.get('max_depth', 5),
            learning_rate=kwargs.get('learning_rate', 0.1),
            random_state=42
        )
    elif model_type == 'linear':
        model = LinearRegression()
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    # Train
    model.fit(X_train_scaled, y_train)
    
    # Predict
    y_pred_train = model.predict(X_train_scaled)
    y_pred_val = model.predict(X_val_scaled)
    
    # Inverse transform predictions if log transform was applied
    if transform_info and transform_info.get('log_transform', False):
        y_pred_train = np.expm1(y_pred_train)  # Inverse of log1p
        y_pred_val = np.expm1(y_pred_val)
        y_train_orig = np.expm1(y_train)
        y_val_orig = np.expm1(y_val)
        if transform_info.get('y_shift', 0) != 0:
            y_pred_train = y_pred_train + transform_info['y_shift']
            y_pred_val = y_pred_val + transform_info['y_shift']
            y_train_orig = y_train_orig + transform_info['y_shift']
            y_val_orig = y_val_orig + transform_info['y_shift']
    else:
        y_train_orig = y_train
        y_val_orig = y_val
    
    # Calculate metrics (on original scale)
    metrics = {
        'train_rmse': np.sqrt(mean_squared_error(y_train_orig, y_pred_train)),
        'train_mae': mean_absolute_error(y_train_orig, y_pred_train),
        'train_r2': r2_score(y_train_orig, y_pred_train),
        'val_rmse': np.sqrt(mean_squared_error(y_val_orig, y_pred_val)),
        'val_mae': mean_absolute_error(y_val_orig, y_pred_val),
        'val_r2': r2_score(y_val_orig, y_pred_val),
    }
    
    print(f"[train] Validation RMSE: {metrics['val_rmse']:.4f}")
    print(f"[train] Validation MAE: {metrics['val_mae']:.4f}")
    print(f"[train] Validation R²: {metrics['val_r2']:.4f}")
    
    # Store scaler with model
    model.scaler = scaler
    
    return model, metrics


def main(
    data_path: str,
    experiment_name: str = 'earthquake_prediction',
    target: str = 'magnitude',
    test_size: float = 0.2,
    model_type: str = 'random_forest',
    log_transform_target: bool = False,
    **hyperparameters
):
    """
    Main training function with MLflow tracking.
    
    Args:
        data_path: Path to processed data
        experiment_name: MLflow experiment name
        target: Target variable to predict
        test_size: Proportion of data for testing
        model_type: Type of model to train
        **hyperparameters: Model hyperparameters
    """
    # Set MLflow tracking URI (can be set via environment variable)
    # For Dagshub: mlflow.set_tracking_uri("https://dagshub.com/<username>/<repo>.mlflow")
    mlflow_tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
    if mlflow_tracking_uri:
        # Handle Dagshub authentication if credentials are provided
        mlflow_username = os.getenv('MLFLOW_TRACKING_USERNAME')
        mlflow_password = os.getenv('MLFLOW_TRACKING_PASSWORD')
        if mlflow_username and mlflow_password:
            import urllib.parse
            # Embed credentials in tracking URI for Dagshub
            parsed = urllib.parse.urlparse(mlflow_tracking_uri)
            auth_uri = f"{parsed.scheme}://{mlflow_username}:{mlflow_password}@{parsed.netloc}{parsed.path}"
            mlflow.set_tracking_uri(auth_uri)
            print(f"[train] Using MLflow tracking URI: {parsed.scheme}://{parsed.netloc}{parsed.path} (authenticated)")
        else:
            mlflow.set_tracking_uri(mlflow_tracking_uri)
            print(f"[train] Using MLflow tracking URI: {mlflow_tracking_uri}")
    else:
        print("[train] Using local MLflow tracking (set MLFLOW_TRACKING_URI for remote)")
    
    # Set or create experiment
    mlflow.set_experiment(experiment_name)
    
    # Load data
    df = load_data(data_path)
    
    # Auto-detect if log transform is beneficial for time_since_last
    if target == 'time_since_last' and not log_transform_target:
        # Check skewness
        target_skew = df[target].skew()
        if target_skew > 1.0:  # Highly skewed
            log_transform_target = True
            print(f"[train] Target is skewed (skewness={target_skew:.2f}), enabling log transformation")
    
    # Prepare features
    X, y, feature_names, transform_info = prepare_features(df, target=target, log_transform_target=log_transform_target)
    
    # Time-series split (maintain temporal order)
    # Sort by datetime if available
    if 'datetime' in df.columns:
        sort_idx = df['datetime'].argsort()
        X = X.iloc[sort_idx].reset_index(drop=True)
        y = y.iloc[sort_idx].reset_index(drop=True)
    
    # Split data (temporal split for time-series)
    split_idx = int(len(X) * (1 - test_size))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    # Further split training into train/val
    val_size = 0.2
    val_split_idx = int(len(X_train) * (1 - val_size))
    X_train, X_val = X_train.iloc[:val_split_idx], X_train.iloc[val_split_idx:]
    y_train, y_val = y_train.iloc[:val_split_idx], y_train.iloc[val_split_idx:]
    
    print(f"[train] Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    
    # Start MLflow run
    with mlflow.start_run():
        # Log parameters
        mlflow.log_param("model_type", model_type)
        mlflow.log_param("target", target)
        mlflow.log_param("train_size", len(X_train))
        mlflow.log_param("val_size", len(X_val))
        mlflow.log_param("test_size", len(X_test))
        mlflow.log_param("n_features", len(feature_names))
        
        # Log hyperparameters
        for key, value in hyperparameters.items():
            mlflow.log_param(key, value)
        
        # Train model
        model, metrics = train_model(
            X_train, y_train, X_val, y_val,
            model_type=model_type,
            transform_info=transform_info,
            **hyperparameters
        )
        
        # Log metrics
        for metric_name, metric_value in metrics.items():
            mlflow.log_metric(metric_name, metric_value)
        
        # Evaluate on test set
        scaler = model.scaler
        X_test_scaled = scaler.transform(X_test)
        y_pred_test = model.predict(X_test_scaled)
        
        # Inverse transform test predictions if needed
        if transform_info and transform_info.get('log_transform', False):
            y_pred_test = np.expm1(y_pred_test)
            y_test_orig = np.expm1(y_test)
            if transform_info.get('y_shift', 0) != 0:
                y_pred_test = y_pred_test + transform_info['y_shift']
                y_test_orig = y_test_orig + transform_info['y_shift']
        else:
            y_test_orig = y_test
        
        test_metrics = {
            'test_rmse': np.sqrt(mean_squared_error(y_test_orig, y_pred_test)),
            'test_mae': mean_absolute_error(y_test_orig, y_pred_test),
            'test_r2': r2_score(y_test_orig, y_pred_test),
        }
        
        for metric_name, metric_value in test_metrics.items():
            mlflow.log_metric(metric_name, metric_value)
        
        print(f"[train] Test RMSE: {test_metrics['test_rmse']:.4f}")
        print(f"[train] Test MAE: {test_metrics['test_mae']:.4f}")
        print(f"[train] Test R²: {test_metrics['test_r2']:.4f}")
        
        # Log model
        signature = infer_signature(X_train, y_train)
        mlflow.sklearn.log_model(
            model,
            "model",
            signature=signature,
            input_example=X_train.iloc[:5],
            registered_model_name=f"earthquake_{target}_predictor"
        )
        
        # Log feature importance (if available)
        if hasattr(model, 'feature_importances_'):
            feature_importance = pd.DataFrame({
                'feature': feature_names,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            # Log as artifact
            importance_path = "feature_importance.csv"
            feature_importance.to_csv(importance_path, index=False)
            mlflow.log_artifact(importance_path)
            os.remove(importance_path)
            
            print("\n[train] Top 10 Most Important Features:")
            print(feature_importance.head(10).to_string(index=False))
        
        # Log data info
        mlflow.log_param("data_path", data_path)
        mlflow.log_param("data_shape", f"{df.shape[0]}x{df.shape[1]}")
        
        print(f"\n[train] ✓ Model training complete!")
        print(f"[train] MLflow Run ID: {mlflow.active_run().info.run_id}")
        print(f"[train] Experiment: {experiment_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train earthquake prediction model with MLflow tracking"
    )
    parser.add_argument(
        "--data",
        required=True,
        help="Path to processed parquet file"
    )
    parser.add_argument(
        "--experiment-name",
        default="earthquake_prediction",
        help="MLflow experiment name"
    )
    parser.add_argument(
        "--target",
        default="magnitude",
        choices=['magnitude', 'time_since_last'],
        help="Target variable to predict"
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Proportion of data for testing"
    )
    parser.add_argument(
        "--model-type",
        default="random_forest",
        choices=['random_forest', 'gradient_boosting', 'linear'],
        help="Type of model to train"
    )
    parser.add_argument(
        "--n-estimators",
        type=int,
        default=100,
        help="Number of estimators (for tree models)"
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=10,
        help="Max depth (for tree models)"
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=0.1,
        help="Learning rate (for gradient boosting)"
    )
    parser.add_argument(
        "--log-transform",
        action='store_true',
        help="Apply log transformation to target variable (auto-enabled for time_since_last if skewed)"
    )
    
    args = parser.parse_args()
    
    hyperparameters = {
        'n_estimators': args.n_estimators,
        'max_depth': args.max_depth,
        'learning_rate': args.learning_rate,
    }
    
    main(
        data_path=args.data,
        experiment_name=args.experiment_name,
        target=args.target,
        test_size=args.test_size,
        model_type=args.model_type,
        log_transform_target=args.log_transform,
        **hyperparameters
    )

