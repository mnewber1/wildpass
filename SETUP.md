# Quick Setup Guide

Get WildPass running on your local machine in minutes with our automated setup script!

## Prerequisites

- Node.js (v16+)
- Python 3.7+
- npm or yarn
- pip

## Automated Setup (Recommended)

We've created an automated setup script that handles everything for you:

```bash
chmod +x setup.sh
./setup.sh
```

The script will:
- ✅ Check for required dependencies (Node.js, Python, pip)
- ✅ Create environment files from templates
- ✅ Optionally configure your Amadeus API credentials
- ✅ Set up Python virtual environment
- ✅ Install all backend dependencies
- ✅ Install all frontend dependencies
- ✅ Optionally start both servers automatically

Just follow the interactive prompts!

### Get Amadeus API Credentials (Optional)

If you want to use real flight data instead of mock data:

1. Go to [https://developers.amadeus.com](https://developers.amadeus.com)
2. Click "Register" to create a free account
3. After logging in, click "Create New App"
4. Give your app a name (e.g., "WildPass Flight Search")
5. Copy your **API Key** and **API Secret**
6. Enter them when the setup script prompts you

> **Note**: The free test API has limited flight data but is perfect for development. You can also skip this step and use `DEV_MODE=true` for testing with mock data.

---

## Manual Setup (Alternative)

If you prefer to set up manually or the automated script doesn't work for your system:

### Step 1: Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. The default settings in `.env` should work as-is:
```env
REACT_APP_API_URL=http://localhost:5001/api
```

### Step 2: Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create and activate virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

> **Note**: This installs Flask, CORS support, Amadeus SDK, python-dotenv, and other required packages.

4. Create backend environment file:
```bash
cp .env.example .env
```

5. Open `backend/.env` and add your Amadeus credentials (or set `DEV_MODE=true`):
```env
AMADEUS_API_KEY=your_api_key_here
AMADEUS_API_SECRET=your_api_secret_here
DEV_MODE=false
```

Replace `your_api_key_here` and `your_api_secret_here` with your credentials.

### Step 3: Run the Application

You'll need **two terminal windows** open:

#### Terminal 1 - Backend (from project root):
```bash
cd backend
source venv/bin/activate  # If using virtual environment
python app.py
```
This will start the Flask API on [http://localhost:5001](http://localhost:5001)

#### Terminal 2 - Frontend (from project root):
```bash
npm start
```
This will start the React app on [http://localhost:3000](http://localhost:3000)

> **Important**: The backend automatically loads your `.env` file, so your Amadeus API credentials will be available without any additional setup.

---

## Test the Application

1. Open your browser to [http://localhost:3000](http://localhost:3000)
2. Try a test search:
   - **Origin**: DEN (Denver)
   - **Destination**: MCO (Orlando)
   - **Departure Date**: Any future date
   - **Trip Type**: Round-trip
3. Click "Search Flights"

## Testing Without API (Development Mode)

If you want to test the app without Amadeus API credentials:

1. In `backend/.env`, set:
```env
DEV_MODE=true
```

2. Restart the backend server

This will return mock flight data instead of making real API calls.

## Troubleshooting

### "No flights found"
- The test API has limited data - try popular routes (DEN→MCO, LAX→LAS)
- Make sure your departure date is in the future
- Check backend terminal for API error messages

### "Cannot connect to backend"
- Verify backend is running on port 5001
- Check that `REACT_APP_API_URL` in `.env` is set to `http://localhost:5001/api`
- Restart both frontend and backend servers

### "Invalid API credentials"
- Double-check your API key and secret in `backend/.env`
- Make sure there are no extra spaces or quotes
- Verify your Amadeus account is active

### "Rate limit exceeded"
- The free test API has limits (1 call/second)
- Wait a few moments and try again
- Consider using `DEV_MODE=true` for testing

## Next Steps

Once everything is working:
- Read [README.md](README.md) for full feature documentation
- Explore Trip Planner mode
- Try the GoWild Pass filters
- Experiment with multi-airport searches

## Need Help?

- Check the [README.md](README.md) troubleshooting section
- Review backend logs for API errors
- Test with `DEV_MODE=true` to isolate API issues

---

Happy flight hunting! ✈️
