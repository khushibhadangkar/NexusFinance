# AI-Powered Smart Financial Goal Planner

This is a full-stack web application designed to help users manage their finances and achieve their goals using AI-driven insights and personalized recommendations.

**Live Frontend (Vercel):** [Your Vercel URL - e.g., https://nexus-finance-ai-umber.vercel.app]
**Live Backend (Render):** [Your Render URL - e.g., https://nexus-finance-ai.onrender.com]

---

## 🚀 Core Features

* **Secure Authentication:** Full user registration and login system using **JWT (JSON Web Tokens)** and **bcrypt** password hashing.
* **Financial Tracking:** A complete dashboard for users to add, track, and visualize their expenses and budgets.
* **50/20/30 Budgeting:** Automatically calculates a realistic budget (50% Needs, 20% Wants, 30% Savings) based on the user's income.
* **Live Data Visualization:** Uses Chart.js to render real-time charts for spending summaries, budget tracking, and more.

## 🧠 AI & Machine Learning Features

This project uses a combination of ML models and smart logic to provide proactive advice:

1.  **K-Means Clustering (User Segmentation):**
    * The backend groups users into "behavioral clusters" based on their income, risk, and goals.
    * This is used to power the recommendation engine.

2.  **ML-Powered Recommendations:**
    * The `GET /recommendations` API uses the user's cluster to provide a personalized list of *real* mutual funds and stocks.

3.  **Random Forest (Financial Score):**
    * A pre-trained Random Forest model (`POST /predict`) analyzes a user's finances to give them a "Financial Health Score."

4.  **"Weekly Focus" Card:**
    * The dashboard homepage features an AI-generated goal (e.g., "Your biggest drain was 'Food'. Try to cut spending by 10%.") based on the user's cluster and recent spending.

5.  **"Smart Nudges":**
    * When a user adds an expense, the `POST /expense` API instantly checks it against their budget. If they overspend, it sends back a pop-up notification (e.g., "Heads up! You're at 90% of your 'shopping' budget.").

## 🛠️ Technology Stack

* **Backend:** Flask, SQLAlchemy
* **Database:** SQLite
* **Machine Learning:** Scikit-learn, Pandas
* **Frontend:** HTML, CSS, JavaScript (Chart.js)
* **Deployment:**
    * Backend deployed on **Render**.
    * Frontend deployed on **Vercel**.

## ⚙️ How to Run Locally

1.  **Backend:**
    ```bash
    # Go into the backend folder
    cd backend
    
    # Create and activate a virtual environment
    python -m venv venv
    .\venv\Scripts\activate
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Run the database seeder (one time)
    # This creates and seeds the DB
    python init_db.py
    
    # Start the server
    python app.py
    ```

2.  **Frontend:**
    * Open the `frontend/login.html` file in your browser. The app is configured to connect to your local server (`http://127.0.0.1:5000`).
