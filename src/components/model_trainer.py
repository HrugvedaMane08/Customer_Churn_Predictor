import os
import sys
from dataclasses import dataclass

import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from xgboost import XGBClassifier

from src.logger import logging
from src.exception import CustomException
from src.utils import save_object

@dataclass
class ModelTrainerConfig:
    trained_model_file_path: str = os.path.join("artifacts", "model.pkl")

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()
        
        # Configure local MLflow tracking
        mlflow_dir = os.path.join(os.getcwd(), "mlruns")
        os.makedirs(mlflow_dir, exist_ok=True)
        mlflow.set_tracking_uri(f"file:///{mlflow_dir}")
        mlflow.set_experiment("Telco_Customer_Churn_Prediction")

    def initiate_model_trainer(self, train_array, test_array) -> float:
        """
        Fits multiple classification models, performs grid-search hyperparameter tuning,
        tracks parameters and metrics in MLflow, selects the best model, and serializes it.
        """
        try:
            logging.info("Splitting train and test input arrays into features and target")
            X_train, y_train, X_test, y_test = (
                train_array[:, :-1],
                train_array[:, -1],
                test_array[:, :-1],
                test_array[:, -1]
            )

            # 1. Define candidate models
            models = {
                "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
                "RandomForest": RandomForestClassifier(random_state=42),
                "XGBoost": XGBClassifier(eval_metric='logloss', random_state=42)
            }

            # 2. Define hyperparameter search spaces for tuning
            params = {
                "LogisticRegression": {
                    "C": [0.1, 1.0, 10.0],
                    "solver": ["lbfgs", "liblinear"]
                },
                "RandomForest": {
                    "n_estimators": [50, 100],
                    "max_depth": [5, 8],
                    "min_samples_split": [2, 5]
                },
                "XGBoost": {
                    "learning_rate": [0.05, 0.1],
                    "n_estimators": [50, 100],
                    "max_depth": [3, 5]
                }
            }

            best_model_score = -1
            best_model_name = None
            best_model_object = None

            # 3. Fit, Tune, and Track each candidate model
            for model_name, model in models.items():
                logging.info(f"Starting Hyperparameter Tuning and MLflow logging for: {model_name}")
                
                # Start an MLflow run for this specific model configuration
                with mlflow.start_run(run_name=model_name) as run:
                    # Log parameters space
                    mlflow.log_param("model_type", model_name)
                    
                    # Set up Grid Search Cross-Validation
                    grid_search = GridSearchCV(
                        estimator=model,
                        param_grid=params[model_name],
                        cv=3,
                        scoring='accuracy',
                        n_jobs=-1
                    )
                    
                    grid_search.fit(X_train, y_train)
                    
                    # Extract the best tuned model
                    best_estimator = grid_search.best_estimator_
                    
                    # Log the best chosen parameters to MLflow
                    logging.info(f"Grid search complete for {model_name}. Best params: {grid_search.best_params_}")
                    for param_key, param_val in grid_search.best_params_.items():
                        mlflow.log_param(f"best_{param_key}", param_val)

                    # Generate predictions
                    y_test_pred = best_estimator.predict(X_test)

                    # Compute classification performance metrics
                    test_accuracy = accuracy_score(y_test, y_test_pred)
                    test_precision = precision_score(y_test, y_test_pred, average='weighted', zero_division=0)
                    test_recall = recall_score(y_test, y_test_pred, average='weighted', zero_division=0)
                    test_f1 = f1_score(y_test, y_test_pred, average='weighted', zero_division=0)

                    # Log metrics to MLflow
                    mlflow.log_metric("accuracy", test_accuracy)
                    mlflow.log_metric("precision", test_precision)
                    mlflow.log_metric("recall", test_recall)
                    mlflow.log_metric("f1_score", test_f1)

                    # Log model artifacts directly into MLflow registry
                    mlflow.sklearn.log_model(best_estimator, artifact_path="model")
                    logging.info(f"Model {model_name} metrics - Accuracy: {test_accuracy:.4f}, F1: {test_f1:.4f}")

                    # Track overall best model based on accuracy
                    if test_accuracy > best_model_score:
                        best_model_score = test_accuracy
                        best_model_name = model_name
                        best_model_object = best_estimator

            # 4. Enforce minimum performance threshold
            min_score_threshold = 0.6
            if best_model_score < min_score_threshold:
                raise CustomException(
                    f"No model met the minimum performance threshold of {min_score_threshold}. Best score: {best_model_score}",
                    sys
                )

            logging.info(f"Best overall model selected: {best_model_name} with Accuracy: {best_model_score:.4f}")

            # 5. Log the overall best model in a summary parent MLflow run
            with mlflow.start_run(run_name="Best_Model_Summary") as best_run:
                mlflow.log_param("selected_model", best_model_name)
                mlflow.log_metric("accuracy", best_model_score)
                mlflow.sklearn.log_model(best_model_object, artifact_path="best_model")

            # 6. Save best model as a localized pickle file for FastAPI predictions
            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=best_model_object
            )

            return best_model_score

        except Exception as e:
            raise CustomException(e, sys)
