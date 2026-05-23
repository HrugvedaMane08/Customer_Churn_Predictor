# Customer Churn Prediction

A production-grade Machine Learning project for predicting customer churn. Built with a modular source-based architecture, robust logging, exception handling, and a FastAPI serving layer.

## Project Structure

```
Customer_Churn_Prediction/
├── .gitignore
├── README.md
├── requirements.txt
├── setup.py
├── notebooks/                  # Jupyter notebooks for EDA and experimentation
├── artifacts/                  # Local folder for serialized models and preprocessing pipelines (git ignored)
├── src/                        # Main source code package
│   ├── __init__.py
│   ├── logger.py               # Custom logging utility
│   ├── exception.py            # Custom exception handler
│   ├── utils.py                # Helper utility functions
│   ├── components/             # Core ML pipeline components
│   │   ├── __init__.py
│   │   ├── data_ingestion.py
│   │   ├── data_transformation.py
│   │   ├── model_trainer.py
│   │   └── model_evaluation.py
│   └── pipeline/               # Executable end-to-end pipelines
│       ├── __init__.py
│       ├── train_pipeline.py
│       └── predict_pipeline.py
└── app/                        # FastAPI serving application
    ├── __init__.py
    └── main.py                 # FastAPI application and endpoint entry point
```

## Quick Start Setup

### 1. Create and Activate Virtual Environment
```bash
python -m venv .venv
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate
```

### 2. Install Dependencies
This project uses editable package installs. Installing `requirements.txt` will automatically run `setup.py`:
```bash
pip install -r requirements.txt
```

### 3. Run FastAPI Application
```bash
uvicorn app.main:app --reload
```

## Usage

- **Training Pipeline**: Can be triggered using python scripts or run via pipeline entry points.
- **FastAPI Endpoints**: Open `http://127.0.0.1:8000/docs` in your browser to view the interactive API swagger docs.
