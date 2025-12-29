# WildPass - Flight Deal Finder

A full-stack flight search aggregator designed for Frontier Airlines GoWild Pass holders. Search, compare, and find the best flight deals across multiple airports with real-time data from the Amadeus Flight API.

## 🚀 Quick Start

**New to WildPass?** Run our automated setup script:

```bash
chmod +x setup.sh
./setup.sh
```

The script will guide you through the entire setup process, including optional Amadeus API configuration.

For detailed instructions or manual setup, see [SETUP.md](SETUP.md).

## Features

### Search Capabilities
- **Multi-Airport Search**: Search from multiple origins to multiple destinations simultaneously
- **Trip Types**:
  - One-way flights
  - Round-trip flights
  - Day-trip searches (same-day return)
  - **Trip Planner Mode**: Find optimal flights based on desired trip duration
- **Any Airport Option**: Search all available Frontier destinations from your origins
- **Date Flexibility**: Trip planner automatically searches future dates (up to 30 days) when initial date has no results

### GoWild Pass Features
- **GoWild Eligibility Detection**: Automatically identifies flights eligible for GoWild Pass redemption
- **GoWild Pricing Display**: Shows "GoWild Pass + taxes" instead of full price for eligible flights
- **GoWild Filter**: Filter search results to show only GoWild-eligible flights
- **Visual Indicators**: Green badges and gradient text to highlight GoWild opportunities
- **Blackout Date Warnings**: Automatic detection and warnings for GoWild blackout periods
  - Major holidays (Christmas, Thanksgiving, New Year's)
  - Peak travel seasons (Summer, Spring Break)
  - Holiday weekends (Memorial Day, Labor Day, etc.)
  - Clear visual warnings with detailed blackout period information

### Advanced Filtering & Sorting
- **Sort Options**:
  - Lowest Price
  - Non-Stop First
  - Earliest Departure
  - Longest Trip (for round trips - maximizes time at destination)
- **Filters**:
  - Non-Stop Only
  - GoWild Only
  - Max Trip Duration (for trip planner)

### Trip Planner Mode
- Specify desired trip length (in hours or days)
- Set maximum trip duration limit
- Prefer non-stop flights option
- Automatically finds best-matching flight combinations
- Shows trip duration badges on results

### User Experience
- **Seat Availability**: Shows remaining seats with urgency indicators
  - Green: 10+ seats available
  - Orange: 4-9 seats left
  - Red (pulsing): ≤3 seats left
- **Smart Caching**: Local and server-side caching (1-hour expiration) with cache indicators
- **Real-time Streaming**: Results appear progressively as routes are searched
- **Modern UI**: Clean, responsive design optimized for desktop and mobile
- **Expandable Flight Cards**: Click destinations to view all flight options

## Tech Stack

### Frontend
- React 18
- LocalStorage caching
- Server-Sent Events (SSE) for streaming results
- CSS3 with animations and gradients

### Backend
- Python 3.7+
- Flask + Flask-CORS
- **Amadeus Flight API** for real-time flight data
- Server-side caching with in-memory storage
- Trip optimization algorithms

## Getting Started

### Prerequisites

- Node.js (v16 or higher recommended)
- Python 3.7+
- npm or yarn
- pip
- **Amadeus API credentials** (free test account at [developers.amadeus.com](https://developers.amadeus.com))

### Installation

> **👉 For detailed setup instructions, see [SETUP.md](SETUP.md)**

#### Automated Setup (Recommended)

```bash
chmod +x setup.sh
./setup.sh
```

The setup script will:
- ✅ Verify prerequisites (Node.js, Python, pip)
- ✅ Create environment files
- ✅ Set up Python virtual environment
- ✅ Install all dependencies
- ✅ Configure Amadeus API credentials (optional)
- ✅ Start both servers (optional)

#### Manual Setup

1. **Get Amadeus API credentials** (optional - free at [developers.amadeus.com](https://developers.amadeus.com))

2. **Install dependencies:**
   ```bash
   npm install
   cd backend && python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   # Root directory
   cp .env.example .env

   # Backend directory
   cd backend
   cp .env.example .env
   # Edit backend/.env and add your Amadeus API credentials
   # Or set DEV_MODE=true for mock data
   ```

4. **Run the application** (requires 2 terminals):

   **Terminal 1 - Backend:**
   ```bash
   cd backend
   source venv/bin/activate
   python app.py
   ```

   **Terminal 2 - Frontend:**
   ```bash
   npm start
   ```

5. **Open [http://localhost:3000](http://localhost:3000)** in your browser

## Project Structure

```
wildpass/
├── backend/
│   ├── app.py                # Flask API server with streaming
│   ├── amadeus_api.py        # Amadeus API integration
│   ├── trip_planner.py       # Trip optimization algorithms
│   ├── gowild_blackout.py    # GoWild blackout dates configuration
│   ├── scraper.py            # Legacy scraper (deprecated)
│   ├── requirements.txt      # Python dependencies
│   ├── test_amadeus.py       # API testing
│   └── test_blackout_dates.py # Blackout dates testing
├── public/
│   └── index.html            # HTML template
├── src/
│   ├── components/
│   │   ├── SearchForm.js     # Search form with all trip types
│   │   ├── FlightResults.js  # Results with sorting/filtering
│   │   ├── DestinationCard.js # Grouped results by destination
│   │   └── FlightCard.js     # Individual flight details
│   ├── services/
│   │   └── api.js            # API calls with streaming support
│   ├── App.js                # Main app component
│   ├── App.css               # Global styles
│   └── index.js              # Entry point
├── .env.example              # Environment variables template
├── package.json
└── README.md
```

## How to Use

### Standard Search (One-Way, Round-Trip, Day-Trip)

1. **Select Trip Type**: Choose your desired trip type
2. **Enter Origins**: Add one or more origin airport codes (e.g., DEN, LAX)
3. **Choose Destinations**:
   - Enter specific airports (e.g., MCO, MIA)
   - OR check "Any Airport" to search all destinations
4. **Select Dates**: Pick departure (and return if applicable)
5. **Search**: Click "Search Flights"
6. **Filter/Sort**: Use filters and sort options to refine results
   - Toggle "Non-Stop Only" or "GoWild Only"
   - Sort by price, non-stop, earliest departure, or longest trip

### Trip Planner Mode

1. **Select "Trip Planner"** as trip type
2. **Enter Origins and Destinations**
3. **Set Trip Length**: Enter desired duration (e.g., "3 days" or "72 hours")
4. **Optional Settings**:
   - Max Trip Duration: Filter out longer trips
   - Prefer Non-Stop: Prioritize direct flights
5. **Select Earliest Departure Date**: The system will search forward if needed
6. **Search**: System finds flights matching your duration preference

## GoWild Pass Integration

### How It Works

The app automatically detects GoWild-eligible flights using:

1. **Fare Class Analysis**: Checks booking class codes (V, Q, X, N, O, S)
2. **Cabin Type**: Must be Economy Basic
3. **Price Heuristics**: Flights under $100 are likely eligible
4. **Visual Indicators**:
   - Green "🎫 GoWild" badge on eligible flights
   - "GoWild Pass + taxes" pricing display
   - Strikethrough of regular price

### GoWild Pass Holders Benefits

- **Filter GoWild-Only**: See only flights you can book with your pass
- **Compare Savings**: Regular price shown with strikethrough
- **Taxes Estimate**: Shows approximate tax/fee range ($5-15)
- **Seat Availability**: Know how many GoWild seats remain
- **Blackout Date Awareness**: Automatic warnings for restricted travel periods
  - Red warning badges on affected flights
  - Detailed information about which dates are blocked
  - Helps avoid booking attempts during blackout periods

## API Endpoints

### Flight Search
- `POST /api/search-stream` - Streaming flight search (SSE)
- `POST /api/search` - Standard flight search (deprecated)

### Trip Planner
- `POST /api/trip-planner` - Find optimal trips by duration

### Utility
- `GET /api/destinations` - Get all Frontier destinations
- `GET /api/health` - Health check
- `POST /api/cache/clear` - Clear server cache
- `GET /api/cache/stats` - Get cache statistics

See backend documentation for detailed API specs.

## Caching System

The app uses two levels of caching:

1. **Browser Cache (LocalStorage)**: 1-hour expiration per search
2. **Server Cache (In-Memory)**: 1-hour expiration per route

Cached results show a "📦 From Cache" badge. Click "Clear Cache" in the footer to force fresh data.

## Algorithm Details

### Trip Planner Scoring

Flights are scored based on:
- **Duration Match**: How close to desired trip length (lower diff = better)
- **Non-Stop Bonus**: -10 points for both legs non-stop, -5 for one, +5 for none
- **Final Score**: `duration_diff + nonstop_bonus` (lower is better)

Results sorted by best match, showing top 20.

### GoWild Eligibility Detection

1. Verify carrier is Frontier (F9)
2. Check `travelerPricings[].fareDetailsBySegment[].class` for restricted codes
3. Fallback to price threshold (<$100) if fare codes unavailable
4. Default to false if undetermined (conservative approach)

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm build` - Builds the app for production
- `npm test` - Launches the test runner

## Troubleshooting

### Backend Issues

**Backend won't start:**
- Ensure Python 3.7+ is installed: `python --version`
- Install dependencies: `pip install -r backend/requirements.txt`
- Check Amadeus credentials are set correctly

**Amadeus API errors:**
- Verify API key/secret are correct
- Check you haven't exceeded rate limits (test API: 1 call/second)
- Test endpoint: `curl http://localhost:5001/api/health`

**No flights found:**
- Test API has limited data (mainly major routes)
- Try popular routes: DEN→MCO, LAX→LAS
- Check console logs for API errors
- Set `DEV_MODE=true` for mock data testing

### Frontend Issues

**Frontend can't connect to backend:**
- Verify backend is running on port 5001
- Check `.env` has correct `REACT_APP_API_URL`
- Restart React dev server after changing `.env`
- Clear browser cache and LocalStorage

**Streaming not working:**
- Ensure browser supports EventSource (all modern browsers)
- Check browser console for SSE errors
- Verify Flask-CORS is configured correctly

**GoWild badges not showing:**
- Ensure Amadeus API is returning fare class data
- Check browser console for fare parsing errors
- May need real API (not test) for full fare details

## Development Mode

For testing without API calls:

```bash
export DEV_MODE=true
python backend/app.py
```

This generates mock flight data instead of calling Amadeus.

## Future Enhancements

- [ ] Add price history tracking
- [ ] Email/SMS notifications for price drops
- [ ] Calendar view for cheapest dates
- [ ] Support for multi-city trips
- [ ] Integration with other airlines
- [ ] Flight price prediction using ML
- [ ] Export results to CSV/JSON
- [ ] Mobile app (React Native)
- [ ] User accounts with saved searches

## Performance Optimization

- **Streaming Results**: Results appear progressively (don't wait for all routes)
- **Parallel API Calls**: Multiple routes searched concurrently
- **Smart Caching**: Reduces redundant API calls
- **Lazy Loading**: Flight details loaded on expand
- **Memoization**: React.useMemo prevents unnecessary re-renders

## Legal & Ethical Considerations

- **API Usage**: Uses official Amadeus API (not scraping)
- **Terms of Service**: Complies with Amadeus developer terms
- **Rate Limiting**: Respects API rate limits
- **Data Accuracy**: Real-time data from official sources
- **Educational Purpose**: Tool designed for personal use and learning

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test thoroughly
4. Submit a pull request

## License

This project is for educational and personal use. Not affiliated with Frontier Airlines or Amadeus.

## Support

For issues or questions:
- Check the troubleshooting section above
- Review backend logs for API errors
- Test with `DEV_MODE=true` first
- Ensure Amadeus API credentials are valid

---

**Note**: The Amadeus test API has limited flight data. For production use, upgrade to the production API for comprehensive results.
