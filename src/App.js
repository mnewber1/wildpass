import React, { useState } from 'react';
import './App.css';
import SearchForm from './components/SearchForm';
import FlightResults from './components/FlightResults';
import { searchFlightsStreaming, clearLocalCache, planTrip } from './services/api';

function App() {
  const [searchParams, setSearchParams] = useState(null);
  const [flights, setFlights] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fromCache, setFromCache] = useState(false);
  const [routesSearched, setRoutesSearched] = useState(0);
  const [totalRoutes, setTotalRoutes] = useState(0);
  const [tripPlannerInfo, setTripPlannerInfo] = useState(null);

  // Build-your-own mode state
  const [selectedOutboundFlight, setSelectedOutboundFlight] = useState(null);
  const [returnFlights, setReturnFlights] = useState([]);
  const [buildYourOwnStep, setBuildYourOwnStep] = useState('outbound'); // 'outbound' or 'return'

  const handleSelectOutboundFlight = (flight) => {
    setSelectedOutboundFlight(flight);
    setBuildYourOwnStep('return');
    setReturnFlights([]);

    // Use desired return date if specified, otherwise use outbound arrival date
    const returnDepartureDate = searchParams.desiredReturnDate || (flight.arrival_date || flight.arrivalDate);

    // Automatically search for return flights
    // Search from destination back to origin
    const returnSearchParams = {
      searchMode: 'build-your-own-return',
      tripType: 'one-way',
      origins: [flight.destination],
      destinations: [flight.origin],
      departureDate: returnDepartureDate,
      returnDate: null
    };

    console.log('🔄 Searching for return flights:', returnSearchParams);
    console.log(`   From: ${flight.destination} → To: ${flight.origin}`);
    console.log(`   Return date: ${returnDepartureDate}`);

    handleSearch(returnSearchParams);
  };

  const handleSelectReturnFlight = (flight) => {
    // Combine outbound and return into a complete trip
    const completedTrip = {
      ...selectedOutboundFlight,
      is_round_trip: true,
      return_flight: flight,
      total_price: (selectedOutboundFlight.price || 0) + (flight.price || 0)
    };

    // You could either add this to flights or show it separately
    setFlights([completedTrip]);
    setBuildYourOwnStep('complete');
  };

  const handleResetBuildYourOwn = () => {
    setSelectedOutboundFlight(null);
    setReturnFlights([]);
    setBuildYourOwnStep('outbound');
    setFlights([]);
  };

  const handleSearch = async (params) => {
    setSearchParams(params);
    setLoading(true);
    setError(null);

    // Always clear flights when starting a new search
    setFlights([]);

    // Reset build-your-own state when starting fresh outbound search
    if (params.searchMode === 'build-your-own') {
      setSelectedOutboundFlight(null);
      setBuildYourOwnStep('outbound');
      setReturnFlights([]);
    }

    setFromCache(false);
    setRoutesSearched(0);
    setTripPlannerInfo(null);

    // Handle trip planner mode differently
    if (params.tripType === 'trip-planner') {
      try {
        const result = await planTrip(params);
        setFlights(result.flights || []);
        setTripPlannerInfo({
          days_searched: result.days_searched,
          earliest_departure: result.earliest_departure,
          total_options: result.total_options
        });
        setLoading(false);

        // Show message if results were found on a later date
        if (result.days_searched > 1 && result.flights?.length > 0) {
          console.log(`Trip planner searched ${result.days_searched} days and found ${result.total_options} options starting ${result.earliest_departure}`);
        } else {
          console.log(`Trip planner found ${result.total_options} options, showing top ${result.flights?.length}`);
        }
      } catch (err) {
        setError(err.message || 'Failed to plan trip. Please try again.');
        console.error('Trip planner error:', err);
        setLoading(false);
      }
      return;
    }

    // Calculate total routes for regular search
    const origins = params.origins || [];
    const destinations = params.destinations || [];
    const total = origins.length * destinations.length;
    setTotalRoutes(total);

    // Use streaming API for regular searches
    searchFlightsStreaming(
      params,
      // onFlights callback - called each time new flights arrive
      (newFlights) => {
        setFlights(prevFlights => [...prevFlights, ...newFlights]);
        setRoutesSearched(prev => prev + 1);
      },
      // onComplete callback - called when search is done
      (result) => {
        setLoading(false);
        setFromCache(result.fromCache || false);
        console.log(`Search complete: ${result.total} total flights`);
      },
      // onError callback
      (err) => {
        setError(err.message || 'Failed to fetch flights. Please try again.');
        console.error('Search error:', err);
        setLoading(false);
      }
    );
  };

  return (
    <div className="App">
      <header className="header">
        <div className="container">
          <h1>WildPass</h1>
          <p className="tagline">Find the best flight deals across multiple destinations</p>
        </div>
      </header>

      <main className="main">
        <div className="container">
          <SearchForm onSearch={handleSearch} loading={loading} />
          {error && (
            <div className="error-message">
              <p>⚠️ {error}</p>
            </div>
          )}
          {loading && (
            <div className="loading-message">
              <div className="spinner"></div>
              <p>Searching for flights... {routesSearched}/{totalRoutes} routes searched</p>
              {flights.length > 0 && (
                <p className="flights-found">{flights.length} flights found so far</p>
              )}
            </div>
          )}
          {searchParams && flights.length > 0 && (
            <FlightResults
              flights={flights}
              searchParams={searchParams}
              fromCache={fromCache}
              isLoading={loading}
              tripPlannerInfo={tripPlannerInfo}
              buildYourOwnMode={searchParams.searchMode === 'build-your-own' || searchParams.searchMode === 'build-your-own-return'}
              buildYourOwnStep={buildYourOwnStep}
              selectedOutboundFlight={selectedOutboundFlight}
              onSelectOutbound={handleSelectOutboundFlight}
              onSelectReturn={handleSelectReturnFlight}
              onResetBuildYourOwn={handleResetBuildYourOwn}
            />
          )}
        </div>
      </main>

      <footer className="footer">
        <div className="container">
          <p>&copy; 2025 WildPass. Flight data will be scraped from Frontier Airlines.</p>
          <button
            className="clear-cache-btn"
            onClick={() => {
              clearLocalCache();
              alert('Cache cleared! Please search again.');
              setFlights([]);
              setSearchParams(null);
            }}
            title="Clear cached flight data"
          >
            Clear Cache
          </button>
        </div>
      </footer>
    </div>
  );
}

export default App;
