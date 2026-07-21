

<div align="center">

# NexusFinance

### AI-Powered Personal Finance Intelligence Platform

A full-stack financial management platform that combines secure expense tracking, machine learning, and personalized investment recommendations to help users understand their financial habits and make data-driven financial decisions.

<p>

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-black?logo=flask)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?logo=javascript)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue?logo=sqlite)
![Scikit Learn](https://img.shields.io/badge/Scikit--Learn-ML-orange?logo=scikit-learn)
![License](https://img.shields.io/badge/License-MIT-green)

</p>

</div>

---

# Overview

NexusFinance is a full-stack personal finance platform designed to help users monitor spending, manage budgets, evaluate financial health, and receive AI-assisted financial recommendations.

The application combines traditional financial management with machine learning models that analyze user spending behaviour, estimate financial health, segment users based on financial characteristics, and recommend investment opportunities.

The system follows a client-server architecture with a Flask REST API, relational database persistence, JWT authentication, and an interactive frontend dashboard.

---

# Key Features

## Authentication

- JWT Authentication
- Secure Login & Registration
- Bcrypt Password Hashing
- Protected API Routes
- Session Management

---

## Personal Finance Management

- Expense Tracking
- Budget Planning
- Monthly Spending Analytics
- Category-wise Expense Breakdown
- Financial Goal Tracking
- Spending History

---

## AI & Machine Learning

### Financial Health Prediction

Predicts a user's financial health score using a trained Random Forest Regression model.

Input features include:

- Monthly Income
- Monthly Expenses
- Investment Amount

Output:

- Financial Health Score
- Personalized Recommendations

---

### User Behaviour Segmentation

Uses K-Means clustering to group users with similar financial behaviour.

Applications:

- Recommendation Personalization
- Behaviour Analysis
- Financial Pattern Detection

---

### Recommendation Engine

Generates personalized investment suggestions using:

- User Cluster
- Financial Health Score
- Spending Behaviour
- Historical Dataset Analysis

---

### Intelligent Budget Alerts

Automatically monitors spending against predefined budgets and generates smart notifications whenever overspending is detected.

---

# Architecture

```text
                    Browser
                       │
                       │
                       ▼
         HTML • CSS • JavaScript Dashboard
                       │
                 REST API Requests
                       │
                       ▼
              Flask Application Server
                       │
       ┌───────────────┼────────────────┐
       │               │                │
       ▼               ▼                ▼
 Authentication   Business Logic   ML Engine
   JWT/Bcrypt                     Random Forest
                                  K-Means
       │               │                │
       └───────────────┼────────────────┘
                       │
                       ▼
              SQLite Database
```

---

# Machine Learning Pipeline

```text
Financial Dataset
        │
        ▼
Data Cleaning
        │
        ▼
Feature Selection
        │
        ▼
Train/Test Split
        │
        ▼
Random Forest Model
        │
        ▼
Financial Health Prediction
        │
        ▼
Recommendation Engine
```

---

# Project Structure

```text
NexusFinance
│
├── backend
│   ├── app.py
│   ├── auth.py
│   ├── config.py
│   ├── dataset_loader.py
│   ├── init_db.py
│   ├── models.py
│   ├── requirements.txt
│   ├── finance_model.pkl
│   └── data
│
├── frontend
│   ├── login.html
│   ├── dashboard.html
│   ├── index.html
│   ├── auth.js
│   ├── notifications.js
│   ├── css
│   └── js
│
├── render.yaml
└── README.md
```

---

# Technology Stack

| Layer | Technologies |
|---------|--------------|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Flask |
| Database | SQLite, SQLAlchemy |
| Authentication | JWT, bcrypt |
| Machine Learning | Scikit-Learn |
| Data Processing | Pandas, NumPy |
| Visualization | Chart.js |
| Deployment | Render, Vercel |

---

# Database Design

```text
Users
-----
id
name
email
password_hash

        │
        │
        ▼

Expenses
--------
id
user_id
category
amount
date
description
```

---

# API Overview

## Authentication

```
POST /auth/register
```

Create a new user account.

---

```
POST /auth/login
```

Authenticate a user and return a JWT access token.

---

## Expense Management

```
GET /expenses
```

Retrieve all user expenses.

---

```
POST /expense
```

Create a new expense entry.

---

```
DELETE /expense/<id>
```

Delete an expense.

---

## Machine Learning

```
POST /predict
```

Predict financial health score.

Example

```json
{
    "monthly_income":70000,
    "monthly_expense_total":42000,
    "investment_amount":10000
}
```

Response

```json
{
    "financial_health_score":81.4
}
```

---

```
GET /recommendations
```

Returns personalized stock and mutual fund recommendations.

---

# Security

- JWT Authentication
- Password Hashing using bcrypt
- Protected API Endpoints
- CORS Configuration
- SQLAlchemy ORM
- Secure Password Storage

---

# Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/NexusFinance.git

cd NexusFinance
```

---

## Backend Setup

```bash
cd backend

python -m venv venv

source venv/bin/activate
```

Windows

```bash
venv\Scripts\activate
```

Install packages

```bash
pip install -r requirements.txt
```

Initialize database

```bash
python init_db.py
```

Run backend

```bash
python app.py
```

---

## Frontend

Simply open

```
frontend/login.html
```

or serve the folder using

```bash
python -m http.server
```

---

# Future Improvements

- React Frontend
- PostgreSQL Migration
- Docker Support
- CI/CD Pipeline
- Portfolio Management
- Real-time Stock APIs
- Explainable AI Recommendations
- Mobile Responsive Dashboard
- OAuth Authentication
- Cloud Storage

---

# Engineering Highlights

✔ Full-stack application architecture

✔ RESTful API design

✔ Machine Learning integration

✔ JWT authentication

✔ SQLAlchemy ORM

✔ Financial data analytics

✔ Data visualization

✔ Budget intelligence

✔ Personalized recommendations

✔ Modular backend architecture

---

# Disclaimer

This project is intended for educational and research purposes. Investment recommendations generated by the platform should not be interpreted as professional financial advice.

---

# License

Licensed under the MIT License.
