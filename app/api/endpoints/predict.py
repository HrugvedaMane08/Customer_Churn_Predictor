import sys
import os
import sqlite3
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.schemas.churn_schema import ChurnInputSchema
from src.pipeline.predict_pipeline import PredictPipeline, CustomData
from src.logger import logging

router = APIRouter()

# Local SQLite database path inside the artifacts directory
DB_PATH = os.path.join("artifacts", "predictions.db")

def init_db():
    """
    Initializes the local SQLite database and creates the prediction history table
    if it doesn't already exist.
    """
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                tenure INTEGER NOT NULL,
                monthly_charges REAL NOT NULL,
                total_charges REAL NOT NULL,
                gender TEXT NOT NULL,
                contract TEXT NOT NULL,
                churn_prediction INTEGER NOT NULL,
                confidence_score REAL
            )
        """)
        conn.commit()
        conn.close()
        logging.info("SQLite database prediction_history table initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize SQLite database: {str(e)}")

# Initialize database on router import
init_db()

@router.post("/", summary="Submit customer details to get a churn prediction")
def predict_churn(payload: ChurnInputSchema):
    """
    Validates input features using Pydantic, applies the preprocessing pipeline,
    runs inference on the trained classification model, and persists the record.
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
        predictions, probabilities = pipeline.predict_with_proba(df)
        
        # Output prediction is a numeric float (0.0 or 1.0)
        churn_prediction = int(predictions[0])
        churn_label = "Yes" if churn_prediction == 1 else "No"
        
        # Extract confidence score if probabilities are available
        confidence_score = None
        if probabilities is not None and len(probabilities) > 0:
            confidence_score = float(probabilities[0][churn_prediction])
        
        # Persist prediction in the SQLite database
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            timestamp = datetime.utcnow().isoformat() + "Z"
            cursor.execute("""
                INSERT INTO prediction_history (timestamp, tenure, monthly_charges, total_charges, gender, contract, churn_prediction, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, payload.tenure, payload.MonthlyCharges, payload.TotalCharges, payload.Gender, payload.Contract, churn_prediction, confidence_score))
            conn.commit()
            conn.close()
            logging.info("Prediction successfully logged to SQLite database.")
        except Exception as db_err:
            logging.error(f"Failed to persist prediction in SQLite database: {str(db_err)}")
        
        logging.info(f"Prediction successful. Result: {churn_label} ({churn_prediction})")
        response = {
            "prediction": [churn_prediction],
            "churn_label": churn_label
        }
        if confidence_score is not None:
            response["confidence_score"] = confidence_score
            
        return response
        
    except FileNotFoundError as fnfe:
        logging.error(f"Prediction failed due to missing model artifacts: {str(fnfe)}")
        raise HTTPException(status_code=400, detail=str(fnfe))
    except Exception as e:
        logging.error(f"Prediction error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error occurred during prediction: {str(e)}")

@router.get("/history", summary="Get all churn prediction history")
def get_prediction_history():
    """
    Retrieves all previously logged churn prediction records from the database.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, tenure, monthly_charges, total_charges, gender, contract, churn_prediction, confidence_score
            FROM prediction_history
            ORDER BY timestamp DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                "id": str(row[0]),
                "timestamp": row[1],
                "tenure": row[2],
                "MonthlyCharges": row[3],
                "TotalCharges": row[4],
                "gender": row[5],
                "Contract": row[6],
                "churn_prediction": row[7],
                "confidence_score": row[8]
            })
        return history
    except Exception as e:
        logging.error(f"Failed to fetch prediction history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@router.get("/stats", summary="Get aggregate analytics stats for churn predictions")
def get_churn_stats():
    """
    Calculates summary metrics across all logged predictions and returns them
    along with the most recent 10 records.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Total count
        cursor.execute("SELECT COUNT(*) FROM prediction_history")
        total_predictions = cursor.fetchone()[0]
        
        if total_predictions == 0:
            conn.close()
            return {
                "total_predictions": 0,
                "high_risk_count": 0,
                "average_monthly_charges": 0.0,
                "churn_rate_percentage": 0.0,
                "history": []
            }
            
        # 2. High risk count
        cursor.execute("SELECT COUNT(*) FROM prediction_history WHERE churn_prediction = 1")
        high_risk_count = cursor.fetchone()[0]
        
        # 3. Average monthly charges
        cursor.execute("SELECT AVG(monthly_charges) FROM prediction_history")
        average_monthly_charges = cursor.fetchone()[0] or 0.0
        
        # 4. Churn rate percentage
        churn_rate_percentage = (high_risk_count / total_predictions) * 100.0
        
        # 5. Fetch last 10 records for history preview
        cursor.execute("""
            SELECT id, timestamp, tenure, monthly_charges, total_charges, gender, contract, churn_prediction, confidence_score
            FROM prediction_history
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                "id": str(row[0]),
                "timestamp": row[1],
                "tenure": row[2],
                "MonthlyCharges": row[3],
                "TotalCharges": row[4],
                "gender": row[5],
                "Contract": row[6],
                "churn_prediction": row[7],
                "confidence_score": row[8]
            })
            
        return {
            "total_predictions": total_predictions,
            "high_risk_count": high_risk_count,
            "average_monthly_charges": float(average_monthly_charges),
            "churn_rate_percentage": float(churn_rate_percentage),
            "history": history
        }
    except Exception as e:
        logging.error(f"Failed to fetch churn stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database aggregation query failed: {str(e)}")
