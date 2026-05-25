import os
import sys
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse

from app.api.router import api_router
from src.logger import logging

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Customer Churn Prediction Service",
    description="Production-grade ML prediction service with interactive dashboard and API endpoints.",
    version="1.0.0"
)

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register versioned API router
app.include_router(api_router, prefix="/api/v1")

# Determine paths for frontend build
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_path = os.path.join(BASE_DIR, "frontend", "out")
has_frontend = os.path.exists(frontend_path)

if has_frontend:
    logging.info(f"Frontend static build found at {frontend_path}. Mounting at root.")
    from starlette.exceptions import HTTPException as StarletteHTTPException
    from fastapi.staticfiles import StaticFiles
    
    # Custom 404 handler to fallback to Next.js 404 page
    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request, exc):
        if exc.status_code == 404:
            static_404 = os.path.join(frontend_path, "404.html")
            if os.path.exists(static_404):
                return FileResponse(static_404, status_code=404)
        return HTMLResponse(content=f"Error {exc.status_code}", status_code=exc.status_code)
    
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    Renders either the static frontend index or the fallback landing page.
    """
    if has_frontend:
        return FileResponse(os.path.join(frontend_path, "index.html"))

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Customer Churn Predictor</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
                --card-bg: rgba(30, 41, 59, 0.45);
                --card-border: rgba(255, 255, 255, 0.08);
                --accent-primary: #6366f1;
                --accent-secondary: #a855f7;
                --text-primary: #f8fafc;
                --text-secondary: #94a3b8;
                --glass-glow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            }

            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }

            body {
                font-family: 'Outfit', sans-serif;
                background: var(--bg-gradient);
                color: var(--text-primary);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 2rem;
                overflow-x: hidden;
            }

            .container {
                width: 100%;
                max-width: 650px;
                background: var(--card-bg);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid var(--card-border);
                border-radius: 24px;
                padding: 3rem;
                box-shadow: var(--glass-glow);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }

            .container:hover {
                transform: translateY(-4px);
                box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.15);
            }

            header {
                text-align: center;
                margin-bottom: 2.5rem;
            }

            h1 {
                font-size: 2.5rem;
                font-weight: 800;
                background: linear-gradient(to right, #818cf8, #c084fc);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.5rem;
            }

            p.subtitle {
                font-size: 1rem;
                color: var(--text-secondary);
            }

            .form-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1.5rem;
                margin-bottom: 2rem;
            }

            @media (max-width: 600px) {
                .form-grid {
                    grid-template-columns: 1fr;
                }
                .container {
                    padding: 1.5rem;
                }
            }

            .input-group {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }

            .input-group.full-width {
                grid-column: span 2;
            }

            @media (max-width: 600px) {
                .input-group.full-width {
                    grid-column: span 1;
                }
            }

            label {
                font-size: 0.9rem;
                font-weight: 600;
                color: var(--text-secondary);
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }

            input, select {
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid var(--card-border);
                border-radius: 12px;
                padding: 0.8rem 1.2rem;
                color: var(--text-primary);
                font-family: inherit;
                font-size: 1rem;
                transition: all 0.3s ease;
                outline: none;
            }

            input:focus, select:focus {
                border-color: var(--accent-primary);
                box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25);
            }

            button {
                width: 100%;
                background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
                border: none;
                border-radius: 12px;
                padding: 1rem;
                color: white;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
            }

            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
            }

            button:active {
                transform: translateY(0);
            }

            .result-card {
                margin-top: 2rem;
                padding: 1.5rem;
                border-radius: 16px;
                background: rgba(15, 23, 42, 0.4);
                border: 1px solid var(--card-border);
                display: none;
                text-align: center;
                animation: fadeIn 0.5s ease forwards;
            }

            .result-title {
                font-size: 1.2rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            }

            .result-value {
                font-size: 2rem;
                font-weight: 800;
            }

            .churn-yes {
                color: #f87171; /* Red */
                text-shadow: 0 0 10px rgba(248, 113, 113, 0.4);
            }

            .churn-no {
                color: #4ade80; /* Green */
                text-shadow: 0 0 10px rgba(74, 222, 128, 0.4);
            }

            .actions-row {
                display: flex;
                gap: 1rem;
                margin-top: 1.5rem;
                width: 100%;
            }

            .btn-secondary {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid var(--card-border);
                color: var(--text-primary);
                box-shadow: none;
            }

            .btn-secondary:hover {
                background: rgba(255, 255, 255, 0.1);
                box-shadow: none;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>ChurnPredict AI</h1>
                <p class="subtitle">Enter customer details below to estimate churn probability</p>
            </header>

            <form id="prediction-form" onsubmit="submitPrediction(event)">
                <div class="form-grid">
                    <div class="input-group">
                        <label for="tenure">Tenure (Months)</label>
                        <input type="number" id="tenure" name="tenure" required min="0" placeholder="e.g. 12" value="12">
                    </div>
                    <div class="input-group">
                        <label for="Gender">Gender</label>
                        <select id="Gender" name="Gender" required>
                            <option value="Male">Male</option>
                            <option value="Female">Female</option>
                        </select>
                    </div>
                    <div class="input-group">
                        <label for="MonthlyCharges">Monthly Charges ($)</label>
                        <input type="number" step="0.01" id="MonthlyCharges" name="MonthlyCharges" required min="0" placeholder="e.g. 70.50" value="70.5">
                    </div>
                    <div class="input-group">
                        <label for="TotalCharges">Total Charges ($)</label>
                        <input type="number" step="0.01" id="TotalCharges" name="TotalCharges" required min="0" placeholder="e.g. 846.00" value="846.0">
                    </div>
                    <div class="input-group full-width">
                        <label for="Contract">Contract Type</label>
                        <select id="Contract" name="Contract" required>
                            <option value="Month-to-month">Month-to-month</option>
                            <option value="One year">One year</option>
                            <option value="Two year">Two year</option>
                        </select>
                    </div>
                </div>

                <button type="submit" id="submit-btn">Run Churn Assessment</button>
            </form>

            <div class="result-card" id="result-card">
                <div class="result-title" id="result-title">Prediction Output</div>
                <div class="result-value" id="result-value">-</div>
            </div>

            <div class="actions-row">
                <button onclick="trainPipeline()" class="btn-secondary" id="train-btn">Run Training Pipeline</button>
                <a href="/docs" style="width: 100%; text-decoration: none;">
                    <button class="btn-secondary" style="width: 100%">API Documentation</button>
                </a>
            </div>
        </div>

        <script>
            async function submitPrediction(event) {
                event.preventDefault();
                const submitBtn = document.getElementById("submit-btn");
                const resultCard = document.getElementById("result-card");
                const resultValue = document.getElementById("result-value");
                
                submitBtn.disabled = true;
                submitBtn.innerText = "Processing...";

                const payload = {
                    tenure: parseInt(document.getElementById("tenure").value),
                    MonthlyCharges: parseFloat(document.getElementById("MonthlyCharges").value),
                    TotalCharges: parseFloat(document.getElementById("TotalCharges").value),
                    Gender: document.getElementById("Gender").value,
                    Contract: document.getElementById("Contract").value
                };

                try {
                    const response = await fetch("/api/v1/predict/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify(payload)
                    });

                    const data = await response.json();
                    
                    if (response.ok) {
                        resultCard.style.display = "block";
                        const churn = data.prediction[0];
                        if (churn === 1) {
                            resultValue.innerHTML = '<span class="churn-yes">High Churn Risk (1)</span>';
                        } else {
                            resultValue.innerHTML = '<span class="churn-no">Low Churn Risk (0)</span>';
                        }
                    } else {
                        alert("Error: " + (data.detail || "Unable to complete request. Please train the model first."));
                    }
                } catch (error) {
                    alert("Network error: " + error.message);
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.innerText = "Run Churn Assessment";
                }
            }

            async function trainPipeline() {
                const trainBtn = document.getElementById("train-btn");
                trainBtn.disabled = true;
                trainBtn.innerText = "Training...";

                try {
                    const response = await fetch("/api/v1/train/", {
                        method: "POST"
                    });
                    const data = await response.json();
                    
                    if (response.ok) {
                        alert("Training successful! Best model accuracy: " + data.best_model_accuracy.toFixed(4));
                    } else {
                        alert("Error training: " + data.detail);
                    }
                } catch (error) {
                    alert("Network error during training: " + error.message);
                } finally {
                    trainBtn.disabled = false;
                    trainBtn.innerText = "Run Training Pipeline";
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
