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
    Configuration class storing artifact directory paths.
    Using dataclasses is a production-grade practice to enforce clean, type-checked
    configuration parameters and paths.
    """
    train_data_path: str = os.path.join("artifacts", "train.csv")
    test_data_path: str = os.path.join("artifacts", "test.csv")
    raw_data_path: str = os.path.join("artifacts", "raw.csv")
    # IBM Telco Customer Churn raw dataset source URL
    dataset_source_url: str = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"

class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()

    def initiate_data_ingestion(self) -> tuple:
        """
        Ingests/loads the raw customer churn dataset from the source URL,
        saves the raw file, splits it into train/test subsets, and serializes
        them in the artifacts folder.
        """
        logging.info("Initializing Data Ingestion component")
        try:
            # 1. Read from data source (in production, this could be SQL database, S3 bucket, API, etc.)
            logging.info(f"Reading dataset from source URL: {self.ingestion_config.dataset_source_url}")
            df = pd.read_csv(self.ingestion_config.dataset_source_url)
            logging.info("Raw dataset read successfully into a Pandas DataFrame")

            # 2. Ensure artifacts directory exists
            os.makedirs(os.path.dirname(self.ingestion_config.raw_data_path), exist_ok=True)

            # 3. Save raw dataset as a lineage artifact
            logging.info(f"Saving raw dataset copy to: {self.ingestion_config.raw_data_path}")
            df.to_csv(self.ingestion_config.raw_data_path, index=False, header=True)

            # 4. Perform train-test splitting
            # Splitting early avoids data leakage during transformations/scaling
            logging.info("Splitting dataset into train and test subsets (Ratio: 80/20, Stratified)")
            
            # Stratification ensures both train and test have the same churn distribution
            train_set, test_set = train_test_split(
                df, 
                test_size=0.2, 
                random_state=42,
                stratify=df['Churn']
            )
            logging.info("Train-Test split completed successfully")

            # 5. Save split files
            logging.info(f"Saving training set to: {self.ingestion_config.train_data_path}")
            train_set.to_csv(self.ingestion_config.train_data_path, index=False, header=True)

            logging.info(f"Saving testing set to: {self.ingestion_config.test_data_path}")
            test_set.to_csv(self.ingestion_config.test_data_path, index=False, header=True)

            logging.info("Data Ingestion process completed successfully")

            return (
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path
            )
        except Exception as e:
            # Capture exact source script line number and file name
            raise CustomException(e, sys)

if __name__ == "__main__":
    # Test script running ingestion component directly
    try:
        obj = DataIngestion()
        train_data, test_data = obj.initiate_data_ingestion()
        print(f"Data ingestion successful. Train file: {train_data}, Test file: {test_data}")
    except Exception as e:
        print(f"Ingestion failed: {e}")
