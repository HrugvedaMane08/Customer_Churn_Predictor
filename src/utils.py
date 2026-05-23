import os
import sys
import dill
from sklearn.metrics import r2_score, accuracy_score, precision_score, recall_score, f1_score
from src.exception import CustomException
from src.logger import logging

def save_object(file_path: str, obj: any) -> None:
    """
    Serializes and saves a python object to the specified file path.
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "wb") as file_obj:
            dill.dump(obj, file_obj)
            
        logging.info(f"Object successfully saved at: {file_path}")
    except Exception as e:
        raise CustomException(e, sys)

def load_object(file_path: str) -> any:
    """
    Loads a serialized python object from the specified file path.
    """
    try:
        with open(file_path, "rb") as file_obj:
            obj = dill.load(file_obj)
        logging.info(f"Object successfully loaded from: {file_path}")
        return obj
    except Exception as e:
        raise CustomException(e, sys)

def evaluate_classifier_models(X_train, y_train, X_test, y_test, models: dict) -> dict:
    """
    Trains and evaluates a dictionary of classification models.
    """
    try:
        report = {}
        for model_name, model in models.items():
            logging.info(f"Training and evaluating model: {model_name}")
            model.fit(X_train, y_train)

            # Make predictions
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            # Calculate classification metrics
            test_accuracy = accuracy_score(y_test, y_test_pred)
            test_f1 = f1_score(y_test, y_test_pred, average='weighted')
            
            report[model_name] = {
                "accuracy": test_accuracy,
                "f1_score": test_f1
            }
            logging.info(f"Model {model_name} metrics - Accuracy: {test_accuracy:.4f}, F1: {test_f1:.4f}")
            
        return report
    except Exception as e:
        raise CustomException(e, sys)
