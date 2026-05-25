# Running the Customer Churn Prediction Application

This document lists all the commands required to set up and run the Customer Churn Prediction application from scratch, along with the purpose of each command.

---

## 🛠️ Option 1: Running Locally (Recommended for Development)

To run the application locally, you will need to start both the **FastAPI Backend** and the **Next.js Frontend**.

### 1. Backend Setup & Run

Execute the following commands in the root of the project directory (`Customer_Churn_Prediction`):

#### Create a Virtual Environment
```bash
python -m venv .venv
```
* **Purpose**: Creates an isolated Python environment specifically for this project. This prevents dependency conflicts with other Python projects on your machine.

#### Activate the Virtual Environment
* **On Windows (PowerShell)**:
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
* **On Windows (Command Prompt)**:
  ```cmd
  .venv\Scripts\activate.bat
  ```
* **On macOS / Linux**:
  ```bash
  source .venv/bin/activate
  ```
* **Purpose**: Points your terminal session to the virtual environment's Python and pip installations rather than system-wide ones.

#### Install Backend Dependencies
```bash
pip install -r requirements.txt
```
* **Purpose**: Installs all required Python packages (such as `fastapi`, `uvicorn`, `scikit-learn`, `xgboost`, `pandas`, etc.) as defined in `requirements.txt`. The `-e .` at the end of `requirements.txt` also installs the local `src` directory as an editable package.

#### Run the FastAPI Backend
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
* **Purpose**: Starts the backend FastAPI web application on local port `8000` with hot-reloading active. Any changes you make to the backend python files will automatically reload the server.
* **URLs**:
  - Main API Endpoint / Dashboard: [http://127.0.0.1:8000](http://127.0.0.1:8000)
  - Interactive Swagger API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### 2. Frontend Setup & Run

Open a **separate terminal window** and navigate to the `frontend/` directory:

```bash
cd frontend
```

#### Install Frontend Dependencies
```bash
npm install
```
* **Purpose**: Installs all npm modules (like `next`, `react`, `tailwind-merge`, and UI library utilities) required by the Next.js React application, based on `package.json`.

#### Run the Frontend Development Server
```bash
npm run dev
```
* **Purpose**: Launches the Next.js development server on port `3000`.
* **URLs**:
  - Customer Churn UI Dashboard: [http://localhost:3000](http://localhost:3000)

---

## 🐳 Option 2: Running via Docker Compose

If you have Docker and Docker Compose installed and running on your system, you can spin up the entire application stack in a single command.

#### Start the Services
```bash
docker-compose up --build
```
* **Purpose**: Automatically builds the Docker images for both `ml-backend` and `next-frontend`, sets up the environment variables (e.g., pointing the frontend to the backend container's API route), maps host ports `8000` and `3000`, and starts both containers.

#### Stop the Services
```bash
docker-compose down
```
* **Purpose**: Stops and removes the active container instances, cleaning up local network assets created by Docker Compose.
