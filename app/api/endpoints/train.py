import sys
from fastapi import APIRouter, HTTPException
from src.pipeline.train_pipeline import TrainPipeline
from src.logger import logging

router = APIRouter()

@router.post("/", summary="Trigger the pipeline training run")
def train_model():
    """
    Executes the full pipeline end-to-end: Ingestion -> Transformation -> Training -> Evaluation.
    """
    try:
        logging.info("API endpoint triggered to run training pipeline")
        pipeline = TrainPipeline()
        metrics = pipeline.run_pipeline()
        return {
            "status": "Success",
            "message": "Model training completed successfully.",
            "best_model_accuracy": metrics["accuracy"],
            "metrics": metrics
        }
    except Exception as e:
        logging.error(f"Training pipeline API failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model training pipeline failed: {str(e)}")
