import os
import sys
import pandas as pd
from src.exception import CustomException
from src.logger import logging
from src.utils import load_object

class PredictPipeline:
    def __init__(self):
        self.model_path = os.path.join("artifacts", "model.pkl")
        self.preprocessor_path = os.path.join("artifacts", "preprocessor.pkl")

    def predict(self, features: pd.DataFrame) -> list:
        """
        Loads the preprocessor and model, preprocesses the input features, 
        and returns prediction outputs.
        """
        try:
            logging.info("Starting prediction pipeline")
            if not os.path.exists(self.model_path) or not os.path.exists(self.preprocessor_path):
                raise FileNotFoundError("Model or preprocessor artifacts not found. Please run the training pipeline first.")

            model = load_object(self.model_path)
            preprocessor = load_object(self.preprocessor_path)

            logging.info("Preprocessing features for inference")
            scaled_data = preprocessor.transform(features)
            
            logging.info("Generating predictions")
            predictions = model.predict(scaled_data)
            return predictions.tolist()
        except Exception as e:
            raise CustomException(e, sys)

class CustomData:
    """
    Helper class to format user input dictionary into a Pandas DataFrame.
    """
    def __init__(self, 
                 tenure: int,
                 MonthlyCharges: float,
                 TotalCharges: float,
                 Gender: str,
                 Contract: str):
        self.tenure = tenure
        self.MonthlyCharges = MonthlyCharges
        self.TotalCharges = TotalCharges
        self.Gender = Gender
        self.Contract = Contract

    def get_data_as_data_frame(self) -> pd.DataFrame:
        try:
            custom_data_input_dict = {
                "tenure": [self.tenure],
                "MonthlyCharges": [self.MonthlyCharges],
                "TotalCharges": [self.TotalCharges],
                "gender": [self.Gender],
                "Contract": [self.Contract]
            }
            return pd.DataFrame(custom_data_input_dict)
        except Exception as e:
            raise CustomException(e, sys)
