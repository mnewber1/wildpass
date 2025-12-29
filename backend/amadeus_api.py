"""
Amadeus API Integration for Flight Search
"""
from amadeus import Client, ResponseError
from datetime import datetime
import os
from gowild_blackout import GoWildBlackoutDates

class AmadeusFlightSearch:
    def __init__(self, api_key=None, api_secret=None):
        """Initialize Amadeus client with API credentials"""
        self.api_key = api_key or os.environ.get('AMADEUS_API_KEY')
        self.api_secret = api_secret or os.environ.get('AMADEUS_API_SECRET')

        if not self.api_key or not self.api_secret:
            raise ValueError("Amadeus API credentials not provided")

        self.amadeus = Client(
            client_id=self.api_key,
            client_secret=self.api_secret
        )

    def search_flights(self, origins, destinations, departure_date, return_date=None, adults=1, callback=None):
        """
        Search for flights using Amadeus API

        Args:
            origins: List of origin airport codes
            destinations: List of destination airport codes (or ['ANY'])
            departure_date: Departure date in YYYY-MM-DD format
            return_date: Optional return date for round-trip
            adults: Number of adult passengers
            callback: Optional callback function(route, flights) called for each route with results

        Returns:
            List of flight dictionaries matching our app's format
        """
        all_flights = []

        # Handle "ANY" destination
        if destinations == ['ANY']:
            # Get popular destinations (we'll need to define these or use a different approach)
            destinations = self._get_popular_destinations(origins)

        # Search each origin-destination pair
        for origin in origins:
            for destination in destinations:
                if origin == destination:
                    continue

                try:
                    # Build search parameters
                    search_params = {
                        'originLocationCode': origin,
                        'destinationLocationCode': destination,
                        'departureDate': departure_date,
                        'adults': adults,
                        'max': 250,  # Request more to get enough Frontier results after filtering
                        'includedAirlineCodes': 'F9'  # Filter for Frontier Airlines only (F9)
                    }

                    # Only add returnDate if it's provided (for round-trip)
                    if return_date:
                        search_params['returnDate'] = return_date

                    # Search one-way or round-trip
                    response = self.amadeus.shopping.flight_offers_search.get(**search_params)

                    # Convert Amadeus format to our app format
                    flights = self._convert_amadeus_to_app_format(response.data, origin, destination)
                    all_flights.extend(flights)

                    # Call callback with results for this route if provided
                    if callback and flights:
                        callback(f"{origin}->{destination}", flights)

                except ResponseError as error:
                    print(f"Error searching {origin} to {destination}: {error}")
                    print(f"Error details: {error.response.body if hasattr(error, 'response') else 'No details'}")
                    continue

        return all_flights

    def _convert_amadeus_to_app_format(self, amadeus_offers, origin, destination):
        """Convert Amadeus flight offers to our app's format"""
        flights = []

        for offer in amadeus_offers:
            try:
                # Get price (applies to the whole trip)
                price = float(offer['price']['total'])
                currency = offer['price']['currency']

                # Get seats remaining (if available)
                seats_remaining = offer.get('numberOfBookableSeats')

                # Check if this is a round-trip (multiple itineraries)
                itineraries = offer['itineraries']
                is_round_trip = len(itineraries) > 1

                # Determine if this is GoWild eligible
                # GoWild uses Economy Basic fare class, typically the lowest price point
                gowild_eligible = self._is_gowild_eligible(offer)

                # Check for blackout dates
                departure_date = itineraries[0]['segments'][0]['departure']['at'][:10]
                return_date = None
                if is_round_trip:
                    return_date = itineraries[1]['segments'][0]['departure']['at'][:10]

                blackout_info = GoWildBlackoutDates.is_flight_affected_by_blackout(
                    departure_date,
                    return_date
                )

                # Convert to USD if needed (rough conversion for test API)
                # In production, you'd want real-time exchange rates
                if currency == 'EUR':
                    price = price * 1.1  # Approximate EUR to USD conversion
                    currency = 'USD'

                if is_round_trip:
                    # Process as round-trip with outbound and return flights
                    outbound = self._parse_itinerary(itineraries[0], origin, destination)
                    return_flight = self._parse_itinerary(itineraries[1], destination, origin)

                    flight = {
                        **outbound,
                        'price': round(price, 2),
                        'currency': currency,
                        'is_round_trip': True,
                        'return_flight': return_flight,
                        'total_price': round(price, 2),  # Total for both directions
                        'seats_remaining': seats_remaining,
                        'gowild_eligible': gowild_eligible,
                        'blackout_dates': blackout_info
                    }
                else:
                    # One-way flight
                    flight_data = self._parse_itinerary(itineraries[0], origin, destination)
                    flight = {
                        **flight_data,
                        'price': round(price, 2),
                        'currency': currency,
                        'is_round_trip': False,
                        'seats_remaining': seats_remaining,
                        'gowild_eligible': gowild_eligible,
                        'blackout_dates': blackout_info
                    }

                flights.append(flight)

            except (KeyError, IndexError) as e:
                print(f"Error parsing offer: {e}")
                continue

        return flights

    def _parse_itinerary(self, itinerary, origin, destination):
        """Parse a single itinerary (one direction of travel)"""
        segments = itinerary['segments']
        first_segment = segments[0]
        last_segment = segments[-1]

        # Parse times
        departure_time = self._parse_datetime(first_segment['departure']['at'])
        arrival_time = self._parse_datetime(last_segment['arrival']['at'])

        # Calculate duration
        duration = itinerary['duration']  # Format: PT2H30M

        # Count stops
        stops = len(segments) - 1

        # Get airline info
        airline_code = first_segment['carrierCode']
        flight_number = f"{airline_code}{first_segment['number']}"

        return {
            'origin': origin,
            'destination': destination,
            'departure_time': departure_time.strftime('%I:%M %p'),  # 12-hour format with AM/PM
            'arrival_time': arrival_time.strftime('%I:%M %p'),      # 12-hour format with AM/PM
            'departure_date': departure_time.strftime('%Y-%m-%d'),
            'arrival_date': arrival_time.strftime('%Y-%m-%d'),
            'duration': self._format_duration(duration),
            'airline': self._get_airline_name(airline_code),
            'flight_number': flight_number,
            'stops': stops,
            'aircraft': last_segment.get('aircraft', {}).get('code', 'N/A'),
            'booking_class': segments[0].get('cabin', 'Economy')
        }

    def _parse_datetime(self, datetime_str):
        """Parse ISO datetime string"""
        # Format: 2024-01-15T14:30:00
        return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))

    def _format_duration(self, duration_str):
        """Convert PT2H30M to '2h 30m' format"""
        # Remove PT prefix
        duration_str = duration_str.replace('PT', '')

        hours = 0
        minutes = 0

        if 'H' in duration_str:
            parts = duration_str.split('H')
            hours = int(parts[0])
            duration_str = parts[1] if len(parts) > 1 else ''

        if 'M' in duration_str:
            minutes = int(duration_str.replace('M', ''))

        if hours and minutes:
            return f"{hours}h {minutes}m"
        elif hours:
            return f"{hours}h"
        else:
            return f"{minutes}m"

    def _get_airline_name(self, code):
        """Map airline codes to names"""
        airline_map = {
            'F9': 'Frontier Airlines',
            'AA': 'American Airlines',
            'UA': 'United Airlines',
            'DL': 'Delta Air Lines',
            'WN': 'Southwest Airlines',
            'B6': 'JetBlue Airways',
            'NK': 'Spirit Airlines',
            'AS': 'Alaska Airlines',
        }
        return airline_map.get(code, code)

    def _is_gowild_eligible(self, offer):
        """
        Determine if a flight offer is eligible for Frontier GoWild pass redemption

        GoWild eligibility criteria:
        1. Must be Frontier Airlines (F9)
        2. Must be Economy Basic fare class (lowest tier)
        3. Typically identified by specific fare families or booking codes

        Args:
            offer: Amadeus flight offer object

        Returns:
            Boolean indicating GoWild eligibility
        """
        try:
            # Check if carrier is Frontier (F9)
            itineraries = offer.get('itineraries', [])
            if not itineraries:
                return False

            # Check first segment's carrier
            first_segment = itineraries[0]['segments'][0]
            carrier = first_segment.get('carrierCode')
            if carrier != 'F9':
                return False

            # Check traveler pricing for fare details
            traveler_pricings = offer.get('travelerPricings', [])
            if not traveler_pricings:
                return False

            # Look at the fare detail basis (booking class code)
            fare_detail_by_segment = traveler_pricings[0].get('fareDetailsBySegment', [])
            if not fare_detail_by_segment:
                return False

            # Check cabin class and fare basis
            # GoWild typically uses ECONOMY cabin with specific fare codes
            for segment_fare in fare_detail_by_segment:
                cabin = segment_fare.get('cabin', '').upper()
                fare_basis = segment_fare.get('fareBasis', '')
                booking_class = segment_fare.get('class', '')

                # GoWild uses Economy Basic which is typically:
                # - ECONOMY cabin
                # - Booking classes: V, Q, X, or other restricted codes
                # - Lowest fare basis codes (often starting with V, Q, X)
                if cabin == 'ECONOMY':
                    # Common GoWild booking classes (most restrictive)
                    gowild_classes = ['V', 'Q', 'X', 'N', 'O', 'S']
                    if booking_class in gowild_classes:
                        return True

                    # Also check if fare basis starts with these codes
                    if fare_basis and any(fare_basis.startswith(code) for code in gowild_classes):
                        return True

            # If we can't determine from fare codes, use price as a heuristic
            # GoWild eligible seats are typically the lowest priced
            # This is a fallback - not 100% accurate but useful
            price = float(offer['price']['total'])

            # For Frontier, if price is below typical thresholds, likely GoWild eligible
            # This varies by route but can be a good indicator
            # Round trips under $100 or one-ways under $50 are often GoWild eligible
            if price < 100:  # Conservative threshold
                return True

            return False

        except (KeyError, IndexError, ValueError) as e:
            # If we can't determine, default to False for safety
            print(f"Error determining GoWild eligibility: {e}")
            return False

    def _get_popular_destinations(self, origins):
        """
        Get popular destinations for 'ANY' airport search
        In production, you might want to use Amadeus's airport routes API
        """
        # Common US destinations
        popular = ['MCO', 'LAS', 'MIA', 'PHX', 'ATL', 'LAX', 'DFW', 'ORD', 'DEN', 'SEA']

        # Remove any that are in origins
        destinations = [dest for dest in popular if dest not in origins]

        # Limit to top 10 to avoid too many API calls
        return destinations[:10]
