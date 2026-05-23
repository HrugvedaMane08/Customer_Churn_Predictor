import os
import sys
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from dataclasses import dataclass

from src.logger import logging
from src.exception import CustomException
from src.utils import load_object

@dataclass
class ModelEvaluationConfig:
    metrics_file_path: str = os.path.join("artifacts", "metrics.csv")

class ModelEvaluation:
    def __init__(self):
        self.evaluation_config = ModelEvaluationConfig()

    def initiate_model_evaluation(self, test_array, model_path: str) -> dict:
        """
        Loads the trained model and evaluates it against the test dataset, 
        saving the performance metrics to a CSV file.
        """
        try:
            logging.info("Starting model evaluation on test dataset")
            
            X_test, y_test = test_array[:, :-1], test_array[:, -1]
            model = load_object(model_path)

            y_pred = model.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)

            metrics = {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1
            }

            logging.info(f"Evaluation Metrics: {metrics}")

            # Save metrics to CSV
            metrics_df = pd.DataFrame([metrics])
            metrics_df.to_csv(self.evaluation_config.metrics_file_path, index=False)
            logging.info(f"Metrics saved to {self.evaluation_config.metrics_file_path}")

            return metrics
        except Exception as e:
            raise CustomException(e, sys)
