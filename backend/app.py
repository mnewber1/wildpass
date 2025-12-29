from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
# from scraper import FrontierScraper  # Commented out - using Amadeus API instead
from amadeus_api import AmadeusFlightSearch
from trip_planner import find_optimal_trips
from gowild_blackout import GoWildBlackoutDates
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json
import os
import random
import time

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize scraper (commented out - using Amadeus API)
# scraper = FrontierScraper()

# Initialize Amadeus API client
try:
    amadeus_client = AmadeusFlightSearch(
        api_key=os.environ.get('AMADEUS_API_KEY'),
        api_secret=os.environ.get('AMADEUS_API_SECRET')
    )
    AMADEUS_ENABLED = True
except ValueError as e:
    print(f"Warning: Amadeus API not configured: {e}")
    amadeus_client = None
    AMADEUS_ENABLED = False

# Development mode - set to True to return mock data instead of scraping
# If Amadeus is enabled, DEV_MODE defaults to False (use real data)
DEV_MODE = os.environ.get('DEV_MODE', 'false' if AMADEUS_ENABLED else 'true').lower() == 'true'

# Simple in-memory cache
cache = {}
CACHE_DURATION = timedelta(hours=1)  # Cache results for 1 hour

def get_cache_key(origins, destinations, departure_date, return_date, trip_type):
    """Generate a unique cache key for the search parameters"""
    return f"{','.join(sorted(origins))}_{','.join(sorted(destinations))}_{departure_date}_{return_date}_{trip_type}"

def is_cache_valid(cache_entry):
    """Check if cached entry is still valid"""
    if not cache_entry:
        return False
    cache_time = datetime.fromisoformat(cache_entry['timestamp'])
    return datetime.now() - cache_time < CACHE_DURATION

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Flight Search API is running',
        'amadeus_enabled': AMADEUS_ENABLED,
        'dev_mode': DEV_MODE
    })

def generate_mock_flights(origins, destinations, departure_date, return_date=None):
    """Generate mock flight data for development/testing"""
    flights = []

    # If destinations is ['ANY'], use a few sample destinations
    dest_list = destinations if destinations != ['ANY'] else ['MCO', 'LAS', 'MIA', 'PHX', 'ATL']

    # Check for blackout dates
    blackout_info = GoWildBlackoutDates.is_flight_affected_by_blackout(departure_date, return_date)

    for origin in origins:
        for destination in dest_list[:5]:  # Limit to 5 destinations
            if origin == destination:
                continue

            # Generate 1-2 mock flights per route
            for _ in range(random.randint(1, 2)):
                hour = random.randint(6, 20)
                minute = random.choice(['00', '15', '30', '45'])
                departure_time = f"{hour:02d}:{minute} {'AM' if hour < 12 else 'PM'}"
                duration_hours = random.randint(2, 6)
                duration_mins = random.choice([0, 15, 30, 45])

                flight = {
                    'origin': origin,
                    'destination': destination,
                    'departureDate': departure_date,
                    'departureTime': departure_time,
                    'arrivalDate': departure_date,
                    'arrivalTime': f"{(hour + duration_hours) % 24:02d}:{duration_mins:02d} {'AM' if (hour + duration_hours) < 12 else 'PM'}",
                    'duration': f"{duration_hours}h {duration_mins}m",
                    'stops': random.choice([0, 0, 0, 1]),  # Mostly nonstop
                    'price': round(random.uniform(29, 199), 2),
                    'seatsRemaining': random.randint(1, 15),
                    'airline': 'Frontier Airlines',
                    'flightNumber': f"F9-{random.randint(1000, 9999)}",
                    'gowild_eligible': random.choice([True, True, False]),  # Mostly eligible
                    'blackout_dates': blackout_info
                }
                flights.append(flight)

    return flights

@app.route('/api/search', methods=['POST'])
def search_flights():
    """
    Search for flights based on provided parameters

    Expected JSON body:
    {
        "origins": ["DEN", "LAX"],
        "destinations": ["MCO", "MIA"],
        "tripType": "round-trip",
        "departureDate": "2025-06-15",
        "returnDate": "2025-06-20"
    }
    """
    try:
        data = request.get_json()

        origins = data.get('origins', [])
        destinations = data.get('destinations', [])
        trip_type = data.get('tripType', 'round-trip')
        departure_date = data.get('departureDate')
        return_date = data.get('returnDate')

        # Validate required fields
        if not origins or not destinations or not departure_date:
            return jsonify({
                'error': 'Missing required fields: origins, destinations, departureDate'
            }), 400

        # Check cache first
        cache_key = get_cache_key(origins, destinations, departure_date, return_date, trip_type)

        if cache_key in cache and is_cache_valid(cache[cache_key]):
            print(f"Returning cached results for {cache_key}")
            return jsonify({
                'flights': cache[cache_key]['flights'],
                'cached': True,
                'searchParams': data,
                'devMode': DEV_MODE
            })

        # Use mock data in dev mode, Amadeus API if enabled, otherwise scrape
        if DEV_MODE:
            print(f"[DEV MODE] Generating mock flights for {origins} -> {destinations}")
            flights = generate_mock_flights(origins, destinations, departure_date, return_date)
        elif AMADEUS_ENABLED:
            # Use Amadeus API for real flight data
            print(f"[AMADEUS API] Searching flights for {origins} -> {destinations}")

            # Set return_date based on trip type
            if trip_type == 'one-way':
                search_return_date = None
            elif trip_type == 'day-trip':
                search_return_date = departure_date
            else:  # round-trip
                search_return_date = return_date

            flights = amadeus_client.search_flights(
                origins=origins,
                destinations=destinations,
                departure_date=departure_date,
                return_date=search_return_date,
                adults=1
            )
        else:
            # Scraper not available - return error
            print(f"ERROR: Neither Amadeus API nor scraper is available")
            return jsonify({
                'error': 'Flight search not available. Please configure Amadeus API credentials or enable DEV_MODE.',
                'devMode': DEV_MODE,
                'amadeusEnabled': AMADEUS_ENABLED
            }), 503

        # Cache the results
        cache[cache_key] = {
            'flights': flights,
            'timestamp': datetime.now().isoformat()
        }

        return jsonify({
            'flights': flights,
            'cached': False,
            'searchParams': data,
            'count': len(flights),
            'devMode': DEV_MODE
        })

    except Exception as e:
        print(f"Error in search_flights: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/search/stream', methods=['POST'])
def search_flights_stream():
    """
    Search for flights with streaming results (Server-Sent Events)

    Returns results as they become available for each route
    """
    try:
        data = request.get_json()

        origins = data.get('origins', [])
        destinations = data.get('destinations', [])
        trip_type = data.get('tripType', 'round-trip')
        departure_date = data.get('departureDate')
        return_date = data.get('returnDate')

        # Validate required fields
        if not origins or not destinations or not departure_date:
            return jsonify({
                'error': 'Missing required fields: origins, destinations, departureDate'
            }), 400

        def generate():
            """Generator function for streaming results"""
            all_flights = []
            streamed_results = []

            def stream_callback(route, flights):
                """Callback to store results for streaming"""
                streamed_results.append({
                    'route': route,
                    'flights': flights,
                    'count': len(flights)
                })

            # Use mock data in dev mode, Amadeus API if enabled
            if DEV_MODE:
                # For mock data, simulate streaming
                dest_list = destinations if destinations != ['ANY'] else ['MCO', 'LAS', 'MIA', 'PHX', 'ATL']

                # Check for blackout dates
                blackout_info = GoWildBlackoutDates.is_flight_affected_by_blackout(departure_date, return_date)

                for origin in origins:
                    for destination in dest_list[:5]:
                        if origin == destination:
                            continue

                        # Generate mock flights for this route
                        route_flights = []
                        for _ in range(random.randint(1, 3)):
                            hour = random.randint(6, 20)
                            minute = random.choice(['00', '15', '30', '45'])
                            flight = {
                                'origin': origin,
                                'destination': destination,
                                'departure_date': departure_date,
                                'departure_time': f"{hour:02d}:{minute}",
                                'arrival_time': f"{(hour+3):02d}:{minute}",
                                'duration': '3h 0m',
                                'price': round(random.uniform(29, 199), 2),
                                'currency': 'USD',
                                'airline': 'Frontier Airlines',
                                'flight_number': f"F9-{random.randint(1000, 9999)}",
                                'stops': 0,
                                'aircraft': '320',
                                'booking_class': 'Economy',
                                'gowild_eligible': random.choice([True, True, False]),
                                'blackout_dates': blackout_info
                            }
                            route_flights.append(flight)

                        all_flights.extend(route_flights)

                        # Stream this route's results
                        event_data = {
                            'route': f"{origin}->{destination}",
                            'flights': route_flights,
                            'count': len(route_flights)
                        }
                        yield f"data: {json.dumps(event_data)}\n\n"
                        time.sleep(0.1)  # Simulate API delay

            elif AMADEUS_ENABLED:
                # Set return_date based on trip type
                if trip_type == 'one-way':
                    search_return_date = None
                elif trip_type == 'day-trip':
                    search_return_date = departure_date
                else:  # round-trip
                    search_return_date = return_date

                # Search with streaming callback
                all_flights = amadeus_client.search_flights(
                    origins=origins,
                    destinations=destinations,
                    departure_date=departure_date,
                    return_date=search_return_date,
                    adults=1,
                    callback=stream_callback
                )

                # Stream the collected results
                for result in streamed_results:
                    yield f"data: {json.dumps(result)}\n\n"

            # Send completion event
            completion_data = {
                'complete': True,
                'total_flights': len(all_flights)
            }
            yield f"data: {json.dumps(completion_data)}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )

    except Exception as e:
        print(f"Error in search_flights_stream: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/destinations', methods=['GET'])
def get_destinations():
    """Get list of all Frontier destinations"""
    # Scraper not available - return empty list or implement Amadeus destination search
    destinations = []
    return jsonify({
        'destinations': destinations,
        'count': len(destinations),
        'message': 'Destination search not implemented with Amadeus API'
    })

@app.route('/api/trip-planner', methods=['POST'])
def trip_planner():
    """
    Plan trips based on desired trip length

    Finds flight combinations that best match the requested trip duration
    """
    try:
        data = request.get_json()

        origins = data.get('origins', [])
        destinations = data.get('destinations', [])
        departure_date = data.get('departureDate')
        trip_length = data.get('tripLength')
        trip_length_unit = data.get('tripLengthUnit', 'days')
        nonstop_preferred = data.get('nonstopPreferred', False)
        max_trip_duration = data.get('maxTripDuration')
        max_trip_duration_unit = data.get('maxTripDurationUnit', 'days')

        # Validate required fields
        if not origins or not destinations or not departure_date or not trip_length:
            return jsonify({
                'error': 'Missing required fields: origins, destinations, departureDate, tripLength'
            }), 400

        # Calculate return date window (search several days to find options)
        depart_dt = datetime.strptime(departure_date, '%Y-%m-%d')
        trip_hours = float(trip_length) * (24 if trip_length_unit == 'days' else 1)

        all_flights = []
        optimal_trips = []
        days_searched = 0
        max_days_to_search = 30

        # Keep searching future dates until we find results or hit 30 days
        while len(optimal_trips) == 0 and days_searched < max_days_to_search:
            current_depart_dt = depart_dt + timedelta(days=days_searched)
            current_departure_date = current_depart_dt.strftime('%Y-%m-%d')
            target_return = current_depart_dt + timedelta(hours=trip_hours)

            # Search a range of dates around target (±2 days for flexibility)
            return_dates = [
                (target_return - timedelta(days=2)).strftime('%Y-%m-%d'),
                (target_return - timedelta(days=1)).strftime('%Y-%m-%d'),
                target_return.strftime('%Y-%m-%d'),
                (target_return + timedelta(days=1)).strftime('%Y-%m-%d'),
                (target_return + timedelta(days=2)).strftime('%Y-%m-%d'),
            ]

            print(f"Searching departure date: {current_departure_date} (day {days_searched + 1}/{max_days_to_search})")

            # Search for round trips with each return date
            batch_flights = []
            for return_date in return_dates:
                if AMADEUS_ENABLED:
                    flights = amadeus_client.search_flights(
                        origins=origins,
                        destinations=destinations,
                        departure_date=current_departure_date,
                        return_date=return_date,
                        adults=1
                    )
                    batch_flights.extend(flights)

            all_flights.extend(batch_flights)

            # Use trip planner to find optimal combinations
            optimal_trips = find_optimal_trips(
                all_flights,
                trip_length=trip_length,
                trip_length_unit=trip_length_unit,
                nonstop_preferred=nonstop_preferred,
                max_duration=max_trip_duration,
                max_duration_unit=max_trip_duration_unit
            )

            if len(optimal_trips) > 0:
                print(f"Found {len(optimal_trips)} matching trips on day {days_searched + 1}")
                break

            days_searched += 1

        # Return top 20 best matches
        return jsonify({
            'flights': optimal_trips[:20],
            'total_options': len(optimal_trips),
            'target_duration': f"{trip_length} {trip_length_unit}",
            'days_searched': days_searched + 1,
            'earliest_departure': (depart_dt + timedelta(days=days_searched)).strftime('%Y-%m-%d') if optimal_trips else None
        })

    except Exception as e:
        print(f"Error in trip_planner: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear the flight cache"""
    global cache
    cache = {}
    return jsonify({'message': 'Cache cleared successfully'})

@app.route('/api/cache/stats', methods=['GET'])
def cache_stats():
    """Get cache statistics"""
    valid_entries = sum(1 for entry in cache.values() if is_cache_valid(entry))
    return jsonify({
        'total_entries': len(cache),
        'valid_entries': valid_entries,
        'expired_entries': len(cache) - valid_entries
    })

if __name__ == '__main__':
    # Run on port 5001 (5000 is often used by macOS AirPlay)
    app.run(debug=True, port=5001, host='127.0.0.1')
