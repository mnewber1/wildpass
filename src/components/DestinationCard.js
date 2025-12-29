import React, { useState } from 'react';
import './DestinationCard.css';
import FlightCard from './FlightCard';

function DestinationCard({ destination, flights, origin, buildYourOwnMode = false, buildYourOwnStep = 'outbound', onSelectFlight }) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Find the cheapest flight for the summary
  const cheapestFlight = flights.reduce((min, flight) =>
    flight.price < min.price ? flight : min
  , flights[0]);

  // Count non-stop flights
  const nonstopCount = flights.filter(f => f.stops === 0).length;

  // Check if this is trip planner mode (has trip_duration_display)
  const isTripPlanner = cheapestFlight.trip_duration_display !== undefined;

  return (
    <div className="destination-card">
      <div
        className="destination-summary"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="destination-header">
          <div className="destination-route">
            <span className="destination-origin">{origin}</span>
            <span className="destination-arrow">→</span>
            <span className="destination-name">{destination}</span>
            {isTripPlanner && cheapestFlight.trip_duration_display && (
              <span className="trip-duration-badge">
                ⏱️ {cheapestFlight.trip_duration_display}
              </span>
            )}
          </div>
          <div className="destination-price">
            <span className="price-from">from</span>
            {cheapestFlight.gowild_eligible ? (
              <>
                <span className="price-amount gowild-price-amount">GoWild Pass</span>
                <span className="gowild-taxes">+ taxes (~$5-15)</span>
              </>
            ) : (
              <span className="price-amount">${cheapestFlight.price}</span>
            )}
          </div>
        </div>

        <div className="destination-stats">
          <div className="stat">
            <span className="stat-value">{flights.length}</span>
            <span className="stat-label">options</span>
          </div>
          <div className="stat">
            <span className="stat-value">{nonstopCount}</span>
            <span className="stat-label">nonstop</span>
          </div>
          {!isTripPlanner && (
            <div className="stat">
              <span className="stat-value">{cheapestFlight.departure_time}</span>
              <span className="stat-label">earliest</span>
            </div>
          )}
          {isTripPlanner && (
            <div className="stat">
              <span className="stat-value">{cheapestFlight.trip_duration_display || 'N/A'}</span>
              <span className="stat-label">trip time</span>
            </div>
          )}
        </div>

        <div className="expand-indicator">
          <span className={`arrow-icon ${isExpanded ? 'expanded' : ''}`}>▼</span>
          <span className="expand-text">
            {isExpanded ? 'Hide flights' : 'Show all flights'}
          </span>
        </div>
      </div>

      {isExpanded && (
        <div className="destination-flights">
          <div className="flights-list">
            {flights.map((flight, index) => (
              <FlightCard
                key={index}
                flight={flight}
                buildYourOwnMode={buildYourOwnMode}
                buildYourOwnStep={buildYourOwnStep}
                onSelectFlight={onSelectFlight}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default DestinationCard;
