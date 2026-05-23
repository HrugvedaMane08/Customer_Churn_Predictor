import sys
from fastapi import APIRouter, HTTPException
from app.schemas.churn_schema import ChurnInputSchema
from src.pipeline.predict_pipeline import PredictPipeline, CustomData
from src.logger import logging

router = APIRouter()

@router.post("/", summary="Submit customer details to get a churn prediction")
def predict_churn(payload: ChurnInputSchema):
    """
    Validates input features using Pydantic, applies the preprocessing pipeline,
    and runs inference on the trained classification model.
    """
    try:
        logging.info(f"Received API request for customer churn prediction: {payload}")
        
        # Instantiate CustomData mapper
        custom_data = CustomData(
            tenure=payload.tenure,
            MonthlyCharges=payload.MonthlyCharges,
            TotalCharges=payload.TotalCharges,
            Gender=payload.Gender,
            Contract=payload.Contract
        )
        
        df = custom_data.get_data_as_data_frame()
        pipeline = PredictPipeline()
        predictions = pipeline.predict(df)
        
        # Output prediction is a numeric float (0.0 or 1.0)
        churn_prediction = int(predictions[0])
        churn_label = "Yes" if churn_prediction == 1 else "No"
        
        logging.info(f"Prediction successful. Result: {churn_label} ({churn_prediction})")
        return {
            "prediction": [churn_prediction],
            "churn_label": churn_label
        }
        
    except FileNotFoundError as fnfe:
        logging.error(f"Prediction failed due to missing model artifacts: {str(fnfe)}")
        raise HTTPException(status_code=400, detail=str(fnfe))
    except Exception as e:
        logging.error(f"Prediction error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error occurred during prediction: {str(e)}")
