import sys
from src.logger import logging
from src.exception import CustomException
from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTrainer
from src.components.model_evaluation import ModelEvaluation

class TrainPipeline:
    def __init__(self):
        pass

    def run_pipeline(self):
        """
        Executes the entire training pipeline end-to-end.
        """
        try:
            logging.info("Training Pipeline Execution Started")

            # 1. Data Ingestion
            ingestion = DataIngestion()
            train_path, test_path = ingestion.initiate_data_ingestion()

            # 2. Data Transformation
            transformation = DataTransformation()
            train_arr, test_arr, preprocessor_path = transformation.initiate_data_transformation(
                train_path=train_path, 
                test_path=test_path
            )

            # 3. Model Training
            trainer = ModelTrainer()
            best_model_score = trainer.initiate_model_trainer(
                train_array=train_arr,
                test_array=test_arr
            )

            # 4. Model Evaluation
            evaluation = ModelEvaluation()
            metrics = evaluation.initiate_model_evaluation(
                test_array=test_arr,
                model_path=trainer.model_trainer_config.trained_model_file_path
            )

            logging.info(f"Training Pipeline Completed. Best Model Accuracy: {best_model_score:.4f}")
            return metrics

        except Exception as e:
            raise CustomException(e, sys)

if __name__ == "__main__":
    pipeline = TrainPipeline()
    pipeline.run_pipeline()
