import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from dataclasses import dataclass

from src.logger import logging
from src.exception import CustomException

@dataclass
class DataIngestionConfig:
    """
    Configuration paths for the data ingestion phase.
    """
    train_data_path: str = os.path.join("artifacts", "train.csv")
    test_data_path: str = os.path.join("artifacts", "test.csv")
    raw_data_path: str = os.path.join("artifacts", "raw.csv")

class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()

    def initiate_data_ingestion(self) -> tuple:
        """
        Ingests/loads raw data, splits it into training and testing sets, 
        and saves them as artifacts.
        """
        logging.info("Starting Data Ingestion component")
        try:
            # For demonstration, we create a dummy customer churn dataset if none exists,
            # or you would load it from database/API/CSV here.
            raw_path = self.ingestion_config.raw_data_path
            os.makedirs(os.path.dirname(raw_path), exist_ok=True)

            # Creating a mock churn dataset for initial testing
            logging.info("Creating mock customer churn dataset for pipeline skeleton")
            mock_data = pd.DataFrame({
                "tenure": [12, 24, 3, 5, 41, 1, 10, 36, 8, 15],
                "MonthlyCharges": [70.5, 89.2, 20.1, 55.4, 105.3, 19.8, 45.3, 95.1, 80.2, 65.4],
                "TotalCharges": [846.0, 2140.8, 60.3, 277.0, 4317.3, 19.8, 453.0, 3423.6, 641.6, 981.0],
                "Gender": ["Male", "Female", "Male", "Female", "Male", "Female", "Male", "Male", "Female", "Female"],
                "Contract": ["Month-to-month", "One year", "Month-to-month", "Month-to-month", "Two year", "Month-to-month", "Month-to-month", "One year", "Month-to-month", "Two year"],
                "Churn": [0, 0, 1, 1, 0, 1, 0, 0, 1, 0]
            })
            
            mock_data.to_csv(raw_path, index=False, header=True)
            logging.info(f"Raw data saved at {raw_path}")

            logging.info("Splitting dataset into train and test sets")
            train_set, test_set = train_test_split(mock_data, test_size=0.2, random_state=42)

            train_set.to_csv(self.ingestion_config.train_data_path, index=False, header=True)
            test_set.to_csv(self.ingestion_config.test_data_path, index=False, header=True)
            logging.info("Data Ingestion successfully completed")

            return (
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path
            )
        except Exception as e:
            raise CustomException(e, sys)

if __name__ == "__main__":
    obj = DataIngestion()
    obj.initiate_data_ingestion()
