# app.py

import os
import random
import pandas as pd
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from datetime import datetime, date, timedelta

# Import models
from models import db, User, Expense
# Import datasets
from dataset_loader import load_all_datasets
# Import authentication
# ✅ FIX: Import token_required
from auth import register_user, login_user, token_required
from config import get_config

# ----------------------------------------
# App Config
# ----------------------------------------
app = Flask(__name__)
config = get_config()
app.config.from_object(config)
# This tells your backend to trust your frontend
CORS(app, 
     origins=[
        "http://127.0.0.1:5500",  # For local testing
        "https_or_http_://your_local_ip_address:port", # for mobile testing
        "https://nexus-finance-ai-umber.vercel.app" # Your live frontend
     ], 
     supports_credentials=True
)
db.init_app(app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------
# Load Datasets
# ----------------------------------------
all_data = load_all_datasets()
mf_data = all_data.get('mutual_funds')
nifty_50_df = all_data.get('nifty_50_historical')

# ----------------------------------------
# ML Model - Random Forest
# ----------------------------------------
def train_model():
    print("🔄 Training model on dataset...")
    df_tracker = pd.read_csv(os.path.join(BASE_DIR, "data", "personal_finance_tracker_dataset.csv"))
    if df_tracker.empty:
        print("❌ Dataset is empty. Skipping model training.")
        return None
    X = df_tracker[["monthly_income", "monthly_expense_total", "investment_amount"]]
    y = df_tracker["financial_advice_score"]
    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor()
    model.fit(X_train, y_train)
    joblib.dump(model, os.path.join(BASE_DIR, "finance_model.pkl"))
    print("✅ Model training complete. Saved as finance_model.pkl")
    return model

def load_model():
    model_path = os.path.join(BASE_DIR, "finance_model.pkl")
    if os.path.exists(model_path):
        print("✅ Model loaded from finance_model.pkl")
        return joblib.load(model_path)
    else:
        return train_model()

model = load_model()

# ----------------------------------------
# API Routes
# ----------------------------------------

# 🔐 Authentication Routes
@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Invalid request data"}), 400
    
    # Validate required fields
    required_fields = ['email', 'password', 'name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400
    
    # Extract optional fields
    income = data.get('income')
    goal = data.get('goal')
    risk_profile = data.get('risk_profile')
    
    result, status_code = register_user(
        email=data['email'],
        password=data['password'],
        name=data['name'],
        income=income,
        goal=goal,
        risk_profile=risk_profile
    )
    
    return jsonify(result), status_code

@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Invalid request data"}), 400
    
    if not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400
    
    result, status_code = login_user(
        email=data['email'],
        password=data['password']
    )
    
    return jsonify(result), status_code

@app.route("/auth/me", methods=["GET"])
@token_required
def get_user_profile(current_user):
    return jsonify({
        'user': {
            'id': current_user.id,
            'email': current_user.email,
            'name': current_user.name,
            'income': current_user.income,
            'goal': current_user.goal,
            'risk_profile': current_user.risk_profile,
            'created_at': current_user.created_at.isoformat() if current_user.created_at else None
        }
    })

@app.route("/auth/logout", methods=["POST"])
@token_required
def logout(current_user):
    return jsonify({"message": "Logged out successfully"})

# 1️⃣ Budget API
@app.route("/budget", methods=["POST"])
@token_required  # ✅ FIX: Protect the route
def budget(current_user): # ✅ FIX: Get the logged-in user
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Invalid request data"}), 400
    
    income = data.get("income")
    goal = data.get("goal")
    risk_profile = data.get("risk_profile")

    if not income:
        return jsonify({"error": "Income is required"}), 400

    try:
        # ✅ FIX: Update the CURRENT user, don't create a new one
        current_user.income = float(income)
        current_user.goal = goal
        current_user.risk_profile = risk_profile
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    # Calculate individual category budgets
    housing = round(current_user.income * 0.30, 2)  # 30%
    food = round(current_user.income * 0.15, 2)      # 15%
    transportation = round(current_user.income * 0.10, 2)  # 10%
    utilities = round(current_user.income * 0.10, 2)       # 10%
    entertainment = round(current_user.income * 0.05, 2)   # 5%
    savings = round(current_user.income * 0.30, 2)         # 30%

    return jsonify({
        "income": current_user.income,
        "goal": current_user.goal,
        "budget_split": {
            "Housing": housing,
            "Food": food,
            "Transportation": transportation,
            "Utilities": utilities,
            "Entertainment": entertainment,
            "Savings": savings
        }
    })

# 2️⃣ Expense API
@app.route("/expense", methods=["POST"])
@token_required # ✅ FIX: Protect the route
def expense(current_user): # ✅ FIX: Get the logged-in user
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Invalid request data"}), 400
    
    # ✅ FIX: Get user_id from the token, not the JSON body
    user_id = current_user.id 
    category = data.get("category").lower()
    amount = data.get("amount")
    date_str = data.get("date")

    if not all([category, amount]):
        return jsonify({"error": "category and amount are required"}), 400

    try:
        if date_str:    
            try:
                created_at = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"error": "date must be YYYY-MM-DD"}), 400
        else:
            created_at = date.today()

        exp = Expense(user_id=user_id, category=category, amount=float(amount), created_at=created_at)
        db.session.add(exp)
        db.session.commit()

        # ✅ FIX: Added "Smart Nudge" logic here
        nudge_message = get_smart_nudge(user_id, category, float(amount))

        return jsonify({
            "message": "Expense added successfully",
            "category": category,
            "amount": float(amount),
            "date": created_at.isoformat(),
            "nudge_message": nudge_message # Send the nudge back to the frontend
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# 3️⃣ Summary API
@app.route("/summary", methods=["GET"])
@token_required # ✅ FIX: Protect the route
def summary(current_user): # ✅ FIX: Get the logged-in user
    """Get financial summary for the logged-in user"""
    try:
        # ✅ FIX: Filter expenses for the CURRENT user only
        expenses = Expense.query.filter_by(user_id=current_user.id).all()
        
        total_spent = sum([e.amount for e in expenses])
        expense_data = {}
        for e in expenses:
            expense_data[e.category] = expense_data.get(e.category, 0) + e.amount
        
        overspending_alerts = []
        # Logic to check against user's budget (assuming budget is set)
        if current_user.income:
            wants_limit = current_user.income * 0.3
            wants_spent = expense_data.get("Entertainment", 0) + expense_data.get("Shopping", 0)
            if wants_spent > wants_limit:
                 overspending_alerts.append(f"Overspending in 'Wants': ₹{wants_spent} spent vs ₹{wants_limit} budget")

        return jsonify({
            "total_spent": total_spent, 
            "by_category": expense_data, 
            "alerts": overspending_alerts
        })
    except Exception as e:
        return jsonify({"error": f"Error fetching summary: {str(e)}"}), 500

# 4️⃣ Investment API
@app.route("/investment", methods=["POST"])
@token_required # ✅ FIX: Protect the route
def investment(current_user): # ✅ FIX: Get the logged-in user
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Invalid request data"}), 400
    
    # ✅ FIX: Use user's profile data as default
    risk = data.get("risk", current_user.risk_profile or "medium").lower()
    savings = data.get("savings", current_user.income * 0.2 if current_user.income else 5000)
    
    suggestions = []
    if risk == "low":
        suggestions.append("Consider Fixed Deposits (FDs), Recurring Deposits (RDs), or Government Bonds.")
        if savings > 50000: 
            suggestions.append("You have significant savings, consider PPF or low-risk Debt Mutual Funds.")
    elif risk == "high":
        suggestions.append("You can explore Equity Mutual Funds, direct Stocks, or ETFs.")
        if savings > 100000: 
            suggestions.append("Given your high savings, a diversified portfolio of large-cap stocks could be beneficial.")
    else:
        suggestions.append("A balanced approach: Consider SIPs in Index Funds or Balanced Mutual Funds.")
        if savings > 20000: 
            suggestions.append("Start with an Index Fund SIP to build your wealth with moderate risk.")
    
    if mf_data is not None and not mf_data.empty:
        try:
            random_fund = mf_data['Scheme'].sample(n=1).iloc[0]
            suggestions.append(f"Based on our analysis, a good option is: {random_fund}.")
        except:
            pass

    return jsonify({
        "risk_profile": risk, 
        "savings": savings, 
        "suggestions": suggestions
    })

# 5️⃣ Tips API
@app.route("/tips", methods=["GET"])
@token_required # ✅ FIX: Protect the route
def tips(current_user): # ✅ FIX: Get the logged-in user
    try:
        # ✅ FIX: Get expenses for the CURRENT user only
        expenses = Expense.query.filter_by(user_id=current_user.id).all()
        expense_data = {}
        for e in expenses:
            expense_data[e.category] = expense_data.get(e.category, 0) + e.amount
        
        if expense_data.get("Food", 0) > 5000: 
            return jsonify({"tip": "Try cooking at home instead of eating out to save more."})
        elif expense_data.get("Entertainment", 0) > 3000: 
            return jsonify({"tip": "Look for free or low-cost entertainment options like a picnic or a library trip."})
        elif expense_data.get("Shopping", 0) > 7000: 
            return jsonify({"tip": "Before you buy, ask yourself if you really need it. Pause and think."})
        else:
            tips_list = [
                "Track your spending daily to cut unnecessary costs.", 
                "Start an SIP with even ₹500 — consistency matters.", 
                "Maintain an emergency fund of 6 months' expenses.", 
                "Avoid using credit cards for wants, stick to needs.", 
                "Review and rebalance your budget every month."
            ]
            return jsonify({"tip": random.choice(tips_list)})
    except Exception as e:
        return jsonify({"error": f"Error fetching tips: {str(e)}"}), 500

# 6️⃣ Predict Financial Advice Score
@app.route('/predict', methods=['POST'])
@token_required # ✅ FIX: Protect the route
def predict(current_user): # ✅ FIX: Get the logged-in user
    if model is None:
        return jsonify({"error": "ML model is not loaded."}), 500

    data = request.json
    if not data:
        return jsonify({"error": "Invalid request data"}), 400
    
    try:
        # ✅ FIX: Use user's data as default if not provided
        X_new = [[
            data.get("monthly_income", current_user.income or 50000),
            data.get("monthly_expense_total", 20000), # Note: We should query this
            data.get("investment_amount", 5000)
        ]]
        prediction = model.predict(X_new)[0]
        return jsonify({"prediction": round(float(prediction), 2)})
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 400

# 7️⃣ Stock Data API
@app.route("/api/stock_data/<symbol>", methods=["GET"])
def get_stock_data(symbol):
    try:
        if nifty_50_df is not None and not nifty_50_df.empty:
            nifty_50_df['Symbol'] = nifty_50_df['Symbol'].astype(str).str.strip().str.upper()
            symbol = symbol.upper()
            stock_data = nifty_50_df[nifty_50_df['Symbol'] == symbol].tail(100)

            if not stock_data.empty:
                return jsonify(stock_data.to_dict('records'))

        return jsonify({"error": f"No data found for {symbol}"}), 404
    except Exception as e:
        return jsonify({"error": f"Error fetching stock data: {str(e)}"}), 500

# 8️⃣ Stock List API
@app.route("/api/stocks/list", methods=["GET"])
def get_stock_list():
    try:
        if nifty_50_df is not None and "Symbol" in nifty_50_df.columns:
            symbols = sorted(nifty_50_df["Symbol"].unique().tolist())
            return jsonify({"available_symbols": symbols})
        return jsonify({"error": "No stock symbols available"}), 404
    except Exception as e:
        return jsonify({"error": f"Error fetching stock list: {str(e)}"}), 500

# 9️⃣ Cluster Users API (K-Means)
@app.route("/cluster_users", methods=["GET"])
@token_required # ✅ FIX: Protect the route
def cluster_users(current_user): # ✅ FIX: Get the logged-in user
    try:
        users = User.query.all()
        if not users or len(users) < 2: # K-Means needs at least 2 users
            return jsonify({"error": "Not enough users to cluster."}), 400

        df = pd.DataFrame([{
            "id": u.id, # ✅ FIX: Added ID to dataframe
            "income": u.income or 0,
            "goal": 1 if u.goal else 0,
            "risk": {"low": 0, "medium": 1, "high": 2}.get((u.risk_profile or "").lower(), 1)
        } for u in users])

        kmeans = KMeans(n_clusters=min(3, len(df)), random_state=42, n_init=10)
        df["cluster"] = kmeans.fit_predict(df[["income", "goal", "risk"]])

        # ✅ FIX: Find the cluster for the *current* user
        current_user_cluster = df[df['id'] == current_user.id]['cluster'].iloc[0]

        return jsonify({
            "clusters": df.to_dict(orient="records"),
            "current_user_cluster": int(current_user_cluster)
            })
    except Exception as e:
        return jsonify({"error": f"Error clustering users: {str(e)}"}), 500

# ---------- Recommendation Engine ----------
def _get_user_cluster_and_peers(user_id):
    users = User.query.all()
    if not users or len(users) < 3:
        return None, [] 

    df = pd.DataFrame([{
        "id": u.id,
        "income": float(u.income or 0),
        "goal": 1 if (u.goal and str(u.goal).strip()) else 0,
        "risk": {"low": 0, "medium": 1, "high": 2}.get((u.risk_profile or "").lower(), 1)
    } for u in users])

    k = min(3, len(df)) 
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    features = df[["income", "risk", "goal"]].values
    labels = kmeans.fit_predict(features)

    df["cluster"] = labels
    row = df[df["id"] == user_id]
    if row.empty:
        return None, []
    cluster_label = int(row["cluster"].iloc[0])
    peer_ids = df[df["cluster"] == cluster_label]["id"].tolist()
    peer_ids = [pid for pid in peer_ids if pid != user_id]
    return cluster_label, peer_ids

def _find_best_return_column(df):
    candidates = [c for c in df.columns if any(k in c.lower() for k in ["1y", "1 yr", "1yr", "1-year", "return", "returns", "3y", "3yr", "aum"])]
    numeric_candidates = []
    for c in candidates:
        try:
            pd.to_numeric(df[c].dropna().iloc[:5])
            numeric_candidates.append(c)
        except Exception:
            continue
    return numeric_candidates[0] if numeric_candidates else None

def _content_based_mf_recs(user, n=5):
    if mf_data is None or mf_data.empty:
        return []

    df = mf_data.copy()
    cols = [c.strip() for c in df.columns]
    df.columns = cols
    risk_cols = [c for c in df.columns if c.lower() in ("risk","risk_profile","risk level","risk_level")]
    risk_col = risk_cols[0] if risk_cols else None
    return_col = _find_best_return_column(df)

    filtered = df
    user_risk = (user.risk_profile or "").lower()
    if risk_col and user_risk:
        try:
            filtered = df[df[risk_col].astype(str).str.lower().str.contains(user_risk.split()[0])]
        except Exception:
            filtered = df

    if return_col:
        filtered = filtered.copy()
        filtered[return_col] = pd.to_numeric(filtered[return_col], errors='coerce')
        filtered = filtered.sort_values(by=return_col, ascending=False)
    else:
        filtered = filtered

    key_col = "Scheme" if "Scheme" in filtered.columns else (filtered.columns[0] if len(filtered.columns)>0 else None)
    if key_col is None:
        return []

    recs = []
    for _, row in filtered.iterrows():
        name = str(row[key_col])
        reason = "Matched by risk & top return" if return_col and risk_col else ("Top performer" if return_col else "Popular fund")
        recs.append({"scheme": name, "reason": reason})
        if len(recs) >= n:
            break
    return recs

def _collaborative_recs(peer_ids, n=3):
    if mf_data is None or mf_data.empty:
        return []

    df = mf_data.copy()
    return_col = _find_best_return_column(df)
    if return_col:
        df[return_col] = pd.to_numeric(df[return_col], errors='coerce')
        df = df.sort_values(by=return_col, ascending=False)
    key_col = "Scheme" if "Scheme" in df.columns else df.columns[0]
    recs = []
    for _, row in df.iterrows():
        recs.append({"scheme": str(row[key_col]), "reason": "Top dataset performer / peer proxy"})
        if len(recs) >= n:
            break
    return recs

def recommend_for_user(user_id, n=5):
    user = User.query.get(user_id)
    if not user:
        return {"error": "user not found"}

    cluster_label, peer_ids = _get_user_cluster_and_peers(user_id)

    c_n = max(1, int(round(n * 0.6)))
    coll_n = n - c_n

    content_recs = _content_based_mf_recs(user, c_n)
    collab_recs = _collaborative_recs(peer_ids, coll_n)

    combined = []
    seen = set()
    for r in (content_recs + collab_recs):
        if r["scheme"] not in seen:
            combined.append(r)
            seen.add(r["scheme"])
        if len(combined) >= n:
            break

    if len(combined) < n:
        if (user.risk_profile or "").lower() == "low":
            generic = ["Fixed Deposits (FD)", "PPF / Debt Mutual Funds", "Recurring Deposit (RD)"]
        elif (user.risk_profile or "").lower() == "high":
            generic = ["Index Fund SIP", "Large-cap Equity Mutual Funds", "ETFs / Stocks"]
        else:
            generic = ["Balanced Mutual Funds", "Index Fund SIP"]
        for g in generic:
            if len(combined) >= n: 
                break
            if g not in seen:
                combined.append({"scheme": g, "reason": "Safe generic suggestion for your risk profile"})
                seen.add(g)

    return {
        "user_id": user_id,
        "cluster": int(cluster_label) if cluster_label is not None else None,
        "recommendations": combined
    }

@app.route("/recommendations", methods=["GET"]) # ✅ FIX: Removed <int:user_id>
@token_required # ✅ FIX: Protect the route
def recommendations(current_user): # ✅ FIX: Get the logged-in user
    try:
        n = request.args.get("n", default=5, type=int)
        
        # ✅ FIX: Use the logged-in user's ID
        result = recommend_for_user(current_user.id, n=n) 
        
        status = 200 if "error" not in result else 400
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": f"Error generating recommendations: {str(e)}"}), 500

# ----------------------------------------
# Smart Nudge Function (Corrected)
# ----------------------------------------
def get_smart_nudge(user_id, category, amount):
    """Generates a smart nudge based on the expense just added."""
    try:
        user = User.query.get(user_id)
        if not user or not user.income:
            return None # Not enough data for a nudge

        # Define individual budget limits for each category
        budget_limits = {
            "housing": user.income * 0.30,
            "food": user.income * 0.15,
            "transportation": user.income * 0.10,
            "utilities": user.income * 0.10,
            "entertainment": user.income * 0.05,
            "savings": user.income * 0.30
        }
        
        budget_limit = budget_limits.get(category, 0)
        
        # If category not in budget limits, don't generate a nudge
        if budget_limit == 0:
            return None

        # Get total spending in this category for the month
        today = date.today()
        start_of_month = today.replace(day=1)
        expenses = Expense.query.filter(
            Expense.user_id == user_id,
            Expense.category == category,
            Expense.created_at >= start_of_month
        ).all()
        
        # This total *includes* the expense just added
        total_spent = sum(e.amount for e in expenses) 
        
        # Check if this new expense pushes them over the limit
        if total_spent > budget_limit:
            return f"Budget Alert! You've spent ₹{total_spent:,.0f} on '{category}' this month, which is over your ₹{budget_limit:,.0f} budget."
        elif total_spent > budget_limit * 0.8:
             return f"Heads up! You're at {int((total_spent/budget_limit)*100)}% of your '{category}' budget for the month."

        # Nudge 2: Check for frequent small purchases
        if category == "food" and amount < 300: # e.g., small coffee/snack
             count = Expense.query.filter(
                Expense.user_id == user_id,
                Expense.category == "food",
                Expense.amount < 300
             ).count()
             if count > 10: # If more than 10 small food purchases
                return f"This is your {count}th small food purchase this month. These can add up!"

        return None # No nudge needed
    except Exception as e:
        print(f"Nudge error: {e}")
        return None

# ----------------------------------------
# ✅ NEW: Weekly Focus API
# ----------------------------------------
@app.route("/weekly_focus", methods=["GET"])
@token_required
def weekly_focus(current_user):
    """Generates a single, actionable focus for the week."""
    try:
        # 1. Get user's cluster
        cluster_label, _ = _get_user_cluster_and_peers(current_user.id)
        
        # 2. Find top spending category in the last 7 days
        seven_days_ago = date.today() - timedelta(days=7)
        recent_expenses = Expense.query.filter(
            Expense.user_id == current_user.id,
            Expense.created_at >= seven_days_ago
        ).all()

        top_category = "General Savings"
        top_amount = 0
        if recent_expenses:
            category_spend = {}
            for e in recent_expenses:
                category_spend[e.category] = category_spend.get(e.category, 0) + e.amount
            
            if category_spend:
                top_category = max(category_spend, key=category_spend.get)
                top_amount = category_spend[top_category]

        # 3. Generate the message based on cluster
        focus_message = ""
        if cluster_label == 0: # Assuming 0 is "Low Income / Saver"
            focus_message = f"Your focus is on building momentum! Your top expense was '{top_category}' (₹{top_amount:,.0f}). Try to save an extra ₹500 this week!"
        elif cluster_label == 1: # Assuming 1 is "Medium Income / Balanced"
            focus_message = f"Your biggest drain was '{top_category}' (₹{top_amount:,.0f}). Let's try to cut spending in this one category by 10%!"
        elif cluster_label == 2: # Assuming 2 is "High Income / Spender"
            focus_message = f"You're in the 'High Spender' group. Your top category was '{top_category}' (₹{top_amount:,.0f}). A great goal is to keep that specific category under ₹2000 this week."
        else: # Fallback
             focus_message = f"Your top spending category last week was '{top_category}' (₹{top_amount:,.0f}). See if you can reduce that by 10%!"

        return jsonify({"focus_message": focus_message})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------------------
# ✅ NEW: DEV ROUTE - Add Sample Users
# ----------------------------------------
@app.route("/seed_db", methods=["GET"])
def seed_db():
    """Adds 30 sample users AND their expenses to the database."""
    try:
        if User.query.count() > 1:
            return jsonify({"message": "Database already has sample users."}), 400

        print("🌱 Seeding database with 30 sample users...")

        sample_users = []
        goals = ["Retirement", "Investment Growth", "Emergency Fund", "Debt Payoff"]
        risks = ["low", "medium", "high"]

        for i in range(30):
            # Create varied profiles
            risk_profile = random.choice(risks)
            
            if risk_profile == "low":
                income = random.randint(30000, 60000)
                goal = "Emergency Fund"
            elif risk_profile == "medium":
                income = random.randint(60000, 100000)
                goal = random.choice(["Retirement", "Investment Growth"])
            else: # high risk
                income = random.randint(100000, 200000)
                goal = "Aggressive Growth"

            user = User(
                name=f"Sample User {i+1}",
                email=f"user{i+1}@example.com",
                password="pass123", # All sample users have the same password
                income=income,
                goal=goal,
                risk_profile=risk_profile
            )
            sample_users.append(user)

        db.session.add_all(sample_users)
        db.session.commit()
        
        print("...✅ 30 users created. Now adding expenses...")
        
        # --- NEW: Add Expenses for Each User ---
        all_expenses = []
        categories = ["food", "transportation", "shopping", "utilities", "entertainment", "healthcare"]
        today = date.today()

        for user in sample_users:
            # Give each user between 20 and 50 expenses
            for _ in range(random.randint(20, 50)):
                # Make amount relative to their income
                max_expense = user.income / 100 
                amount = round(random.uniform(5.0, max_expense), 2)
                
                # Make date in the last 3 months
                random_day = random.randint(1, 90)
                expense_date = today - timedelta(days=random_day)
                
                exp = Expense(
                    user_id=user.id,
                    category=random.choice(categories),
                    amount=amount,
                    created_at=expense_date
                )
                all_expenses.append(exp)

        db.session.add_all(all_expenses)
        db.session.commit()

        print(f"✅ Database seeding complete. Added {len(all_expenses)} sample expenses.")
        return jsonify({
            "message": f"Successfully added 30 sample users and {len(all_expenses)} expenses."
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"❌ Database seeding failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ----------------------------------------
# Root Test Route
# ----------------------------------------
@app.route("/", methods=["GET"])
def home():
    if mf_data is not None and not mf_data.empty: 
        dataset_preview = mf_data.head(3).to_dict()
    elif nifty_50_df is not None and not nifty_50_df.empty: 
        dataset_preview = nifty_50_df.head(3).to_dict()
    else: 
        dataset_preview = {"message": "No datasets loaded."}
    
    return jsonify({
        "message": "Backend with DB + Dataset is working!",
        "dataset_preview": dataset_preview
    })

# ----------------------------------------
# Run App
# ----------------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)