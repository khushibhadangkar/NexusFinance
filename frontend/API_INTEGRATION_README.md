# Phase 4 Step 1: Frontend-Backend API Integration

## Overview
This document describes the API integration implemented in Phase 4 Step 1, connecting the HTML frontend to the Flask backend APIs.

## API Endpoints Integrated

### 1. Budget API (`/budget`)
- **Method**: POST
- **Integration**: Signup form in `login.html`
- **Purpose**: Creates user budget when new account is created
- **Data**: `{income, goal, risk_profile}`

### 2. Expense API (`/expense`)
- **Method**: POST
- **Integration**: Expense form in `dashboard.html`
- **Purpose**: Adds new expenses to the system
- **Data**: `{user_id, category, amount, date}`

### 3. Summary API (`/summary`)
- **Method**: GET
- **Integration**: Dashboard financial overview
- **Purpose**: Displays total spending and category breakdown
- **Updates**: Total spent amount, expense charts, alerts

### 4. Forecast API (`/forecast/<user_id>`)
- **Method**: GET
- **Integration**: Dashboard forecasting section
- **Purpose**: Predicts future expenses using ARIMA
- **Parameters**: `periods=3` (default)

### 5. Recommendations API (`/recommendations/<user_id>`)
- **Method**: GET
- **Integration**: Investment recommendations section
- **Purpose**: Shows personalized investment suggestions
- **Parameters**: `n=5` (number of recommendations)

### 6. Investment API (`/investment`)
- **Method**: POST
- **Integration**: Investment suggestions
- **Purpose**: Provides investment advice based on risk profile
- **Data**: `{risk, savings}`

### 7. Predict API (`/predict`)
- **Method**: POST
- **Integration**: Financial advice scoring
- **Purpose**: Calculates financial advice score using ML model
- **Data**: `{monthly_income, monthly_expense_total, investment_amount}`

## Files Modified

### `dashboard.html`
- Added API configuration and helper functions
- Integrated expense form with `/expense` API
- Added functions for all API integrations
- Implemented error handling and loading states
- Added API connection testing

### `login.html`
- Added API configuration
- Integrated signup form with `/budget` API
- Added user info storage in localStorage
- Implemented loading states during account creation

## Key Features

### Error Handling
- Network error detection (backend not running)
- HTTP error status handling
- User-friendly error messages via toast notifications

### Loading States
- Button state changes during API calls
- Loading indicators for better UX

### Data Persistence
- User info stored in localStorage
- Budget data passed from signup to dashboard

### Real-time Updates
- Dashboard refreshes after adding expenses
- Charts update with new data
- Alerts shown for overspending

## Usage Instructions

### 1. Start Backend Server
```bash
cd backend
python app.py
```
The Flask server should run on `http://localhost:5000`

### 2. Open Frontend
- Open `frontend/index.html` in a web browser
- Click "Get Started" to go to login page
- Create a new account (will create budget via API)
- Access dashboard with full API integration

### 3. Test Features
- Add expenses through the expense form
- View financial summary with real data
- See investment recommendations
- Check expense forecasting

## API Configuration

The frontend is configured to connect to:
- **Base URL**: `http://localhost:5000`
- **Default User ID**: `1` (for testing)

## Error Scenarios Handled

1. **Backend Server Down**: Shows warning message
2. **Network Errors**: Displays connection error
3. **API Errors**: Shows specific error messages
4. **Invalid Data**: Form validation and error handling

## Next Steps (Phase 4 Remaining)

- Add more sophisticated user authentication
- Implement real user session management
- Add more interactive charts and visualizations
- Enhance error recovery mechanisms
- Add offline functionality

## Testing

To test the integration:
1. Ensure backend server is running
2. Open browser developer console
3. Check for API connection success message
4. Test adding expenses and viewing summaries
5. Verify all API calls are working correctly

