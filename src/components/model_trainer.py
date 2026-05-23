import os
import sys
from dataclasses import dataclass

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

from src.logger import logging
from src.exception import CustomException
from src.utils import save_object, evaluate_classifier_models

@dataclass
class ModelTrainerConfig:
    trained_model_file_path: str = os.path.join("artifacts", "model.pkl")

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()

    def initiate_model_trainer(self, train_array, test_array) -> float:
        """
        Fits multiple classification models, evaluates them, selects the best one, 
        and saves it to the artifacts directory.
        """
        try:
            logging.info("Splitting training and test input data")
            X_train, y_train, X_test, y_test = (
                train_array[:, :-1],
                train_array[:, -1],
                test_array[:, :-1],
                test_array[:, -1]
            )

            # Dictionary of models to train
            models = {
                "LogisticRegression": LogisticRegression(),
                "RandomForest": RandomForestClassifier(random_state=42),
                "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
            }

            model_report: dict = evaluate_classifier_models(
                X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test, models=models
            )

            # Get the best model score and name
            best_model_score = -1
            best_model_name = None

            for model_name, metrics in model_report.items():
                if metrics["accuracy"] > best_model_score:
                    best_model_score = metrics["accuracy"]
                    best_model_name = model_name

            best_model = models[best_model_name]

            # Enforce a minimum threshold for the model
            min_score_threshold = 0.5
            if best_model_score < min_score_threshold:
                raise CustomException(
                    f"No model met the minimum performance threshold of {min_score_threshold}. Best score: {best_model_score}",
                    sys
                )

            logging.info(f"Best model selected: {best_model_name} with Accuracy: {best_model_score:.4f}")

            # Save the best model
            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=best_model
            )

            return best_model_score

        except Exception as e:
            raise CustomException(e, sys)
