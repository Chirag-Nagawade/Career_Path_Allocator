# MargIntel Career Path Allocator

MargIntel is an advanced career guidance and path prediction system designed for 10th and 12th-grade students. It uses a hybrid approach combining **academic marks**, **psychometric personality questions**, and **student interest areas** to predict the most aligned career stream and options using a trained Random Forest model. Additionally, it offers location-targeted college recommendations in Maharashtra.

The Flask backend serves both the API endpoints and the static HTML/CSS/JS frontend seamlessly, meaning you only need to run a single server!

---

## 📋 System Prerequisites

Before running the project, make sure you have the following installed on your system:
1. **Python 3.10+** (Recommended)
2. **MongoDB Community Server** (Running locally on default port `27017`)
3. **Web Browser** (Chrome, Edge, Firefox, etc.)

---

## 🚀 Step-by-Step Setup Guide

Follow these steps in sequence to get the project up and running from scratch.

### Step 1: Open a Terminal & Navigate to Backend
Open your terminal (PowerShell, Command Prompt, or Git Bash) and navigate to the backend folder of the project:
```bash
cd backend
```

---

### Step 2: Set Up Python Virtual Environment (venv)
Creating a virtual environment ensures that the packages required by this project do not conflict with your global Python installation.

**On Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

*(Once activated, your terminal prompt will be prefixed with `(venv)`)*.

---

### Step 3: Install Required Dependencies
With the virtual environment active, install all the library requirements listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```
This installs essential libraries including **Flask, scikit-learn, pandas, numpy, pymongo, joblib, PyJWT, and reportlab**.

---

### Step 4: Database Setup (MongoDB)
Make sure your MongoDB server is active and running locally:
- **Windows**: The MongoDB service usually runs automatically in the background. If not, start it from Windows Services or run `mongod` in a separate terminal.
- **Mac/Linux**: Run `brew services start mongodb-community` or `sudo systemctl start mongod`.

The application connects to `mongodb://localhost:27017/` and will automatically create the database `career_path_allocator` and all required collections and indexes upon the first connection.

---

### Step 5: Feature Engineering & Model Training
The project uses advanced machine learning models (Random Forest Classifiers) to predict careers. You have two options to train the models:

#### Option A: Automatic Training (Zero Setup - Recommended)
You do not need to train the models manually. The backend is configured to automatically check if the model files (`career_model_10th.pkl` and `career_model_12th.pkl`) exist under the `backend/model/` directory when starting up. If they are missing:
1. It reads the raw student training datasets from `backend/data/`.
2. Automatically performs feature engineering (combining academic and psychometric features, encoding interests).
3. Saves the updated dataset in `data/` and trains the classification models automatically.

#### Option B: Manual Retraining (Force Retrain)
If you make changes to the datasets in `backend/data/` and want to force-train/rebuild the model files manually, run this command in your active terminal:
```bash
python -c "from excel_processor import ExcelDataProcessor; ExcelDataProcessor().auto_setup_models()"
```
This will perform the entire feature engineering pipeline, create `10th_data_updated.xlsx`/`12th_data_updated.xlsx`, train the models, and output accuracy metrics.

---

### Step 6: Run the Application
Start the Flask development server:
```bash
python app.py
```
Upon running, you should see output resembling:
```text
✅ Models found and ready for use!
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

---

### Step 7: Access the Web Application
Open your web browser and navigate to:
👉 **[http://localhost:5000](http://localhost:5000)**

You will be greeted by the **MargIntel Landing Page**. From here, you can:
1. **Sign Up / Log In** to create a student profile.
2. **Take the Assessment** (academic marks entry + 5 psychometric question sections).
3. **View Strength Analysis** (visualizes your strong and weak academic/psychometric areas).
4. **Get Career Prediction** (displays top predicted careers, including the scaled calibration ensuring the top choice is $\ge$ 80% match).
5. **Explore Recommended Colleges** (search targeted junior colleges and undergraduate colleges in Pune, Mumbai, Nagpur, Nashik, and Chhatrapati Sambhaji Nagar).
6. **Download PDF Reports** (generates a beautiful, personalized, and detailed career blueprint PDF).



## 🛠️ Troubleshooting & Tips

- **Flask server fails to start due to port in use**:
  The application runs on port `5000`. If you have another service using port 5000, you can edit the bottom of `backend/app.py` to use a different port (e.g., `port=8080`) or stop the conflicting process.
- **No Colleges showing up for Chhatrapati Sambhaji Nagar**:
  Make sure you selected a valid preferred city on the colleges page. Under [colleges.json](file:///d:/Career_Path_Allocator/backend/data/colleges.json), only 5 cities are kept (Pune, Mumbai, Nagpur, Nashik, and Chhatrapati Sambhaji Nagar).
- **Authentication errors / token expired**:
  If you encounter issues viewing pages, try logging out and logging back in. The application stores a secure JSON Web Token (JWT) in local storage which expires after 24 hours.
