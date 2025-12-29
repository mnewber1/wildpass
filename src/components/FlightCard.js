import React from 'react';
import './FlightCard.css';

function FlightCard({ flight, buildYourOwnMode = false, buildYourOwnStep = 'outbound', onSelectFlight }) {
  // Calculate trip statistics for completed build-your-own trips
  const calculateTripStats = () => {
    if (!flight.is_round_trip || !flight.return_flight) return null;

    const outboundDepart = new Date(`${flight.departure_date} ${flight.departure_time}`);
    const outboundArrive = new Date(`${flight.arrival_date || flight.arrivalDate} ${flight.arrival_time || flight.arrivalTime}`);
    const returnDepart = new Date(`${flight.return_flight.departure_date} ${flight.return_flight.departure_time}`);
    const returnArrive = new Date(`${flight.return_flight.arrival_date || flight.return_flight.arrivalDate} ${flight.return_flight.arrival_time || flight.return_flight.arrivalTime}`);

    // Total trip duration (from initial departure to final arrival)
    const totalTripMs = returnArrive - outboundDepart;
    const totalTripDays = Math.floor(totalTripMs / (1000 * 60 * 60 * 24));
    const totalTripHours = Math.floor((totalTripMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

    // Time at destination (from outbound arrival to return departure)
    const destinationMs = returnDepart - outboundArrive;
    const destinationDays = Math.floor(destinationMs / (1000 * 60 * 60 * 24));
    const destinationHours = Math.floor((destinationMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

    return {
      totalTripDays,
      totalTripHours,
      destinationDays,
      destinationHours,
      outboundDepart,
      returnArrive
    };
  };

  const tripStats = calculateTripStats();

  // Helper to render a single flight segment
  const renderFlightSegment = (flightData, label) => (
    <div className="flight-segment">
      {label && <div className="segment-label">{label}</div>}
      <div className="flight-details">
        <div className="detail-row">
          <span className="label">Departure:</span>
          <span className="value">{flightData.departure_date || flightData.departureDate} at {flightData.departure_time || flightData.departureTime}</span>
        </div>
        <div className="detail-row">
          <span className="label">Arrival:</span>
          <span className="value">{flightData.arrival_date || flightData.arrivalDate} at {flightData.arrival_time || flightData.arrivalTime}</span>
        </div>
        <div className="detail-row">
          <span className="label">Duration:</span>
          <span className="value">{flightData.duration}</span>
        </div>
        {flightData.stops !== undefined && (
          <div className="detail-row">
            <span className="label">Stops:</span>
            <span className="value">{flightData.stops === 0 ? 'Nonstop' : `${flightData.stops} stop(s)`}</span>
          </div>
        )}
        <div className="detail-row">
          <span className="label">Flight:</span>
          <span className="value">{flightData.airline || flight.airline} {flightData.flight_number || flightData.flightNumber}</span>
        </div>
      </div>
    </div>
  );

  return (
    <div className={`flight-card ${flight.is_round_trip ? 'round-trip' : 'one-way'} ${buildYourOwnMode && buildYourOwnStep === 'complete' ? 'completed-trip' : ''}`}>
      {/* Trip Summary Header for completed build-your-own trips */}
      {buildYourOwnMode && buildYourOwnStep === 'complete' && tripStats && (
        <div className="trip-summary-header">
          <div className="trip-summary-title">
            <span className="success-icon">✓</span>
            <h3>Your Custom Trip to {flight.destination}</h3>
          </div>
          <div className="trip-stats-grid">
            <div className="trip-stat">
              <div className="stat-icon">📅</div>
              <div className="stat-content">
                <div className="stat-value">
                  {tripStats.totalTripDays > 0 ? `${tripStats.totalTripDays}d ${tripStats.totalTripHours}h` : `${tripStats.totalTripHours}h`}
                </div>
                <div className="stat-label">Total Trip Time</div>
              </div>
            </div>
            <div className="trip-stat">
              <div className="stat-icon">🏖️</div>
              <div className="stat-content">
                <div className="stat-value">
                  {tripStats.destinationDays > 0 ? `${tripStats.destinationDays}d ${tripStats.destinationHours}h` : `${tripStats.destinationHours}h`}
                </div>
                <div className="stat-label">Time at Destination</div>
              </div>
            </div>
            <div className="trip-stat">
              <div className="stat-icon">💰</div>
              <div className="stat-content">
                <div className="stat-value">${flight.total_price?.toFixed(2) || (flight.price + (flight.return_flight?.price || 0)).toFixed(2)}</div>
                <div className="stat-label">Total Price</div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="flight-header">
        <div className="route">
          <span className="airport">{flight.origin}</span>
          <span className="arrow">{flight.is_round_trip ? '⇄' : '→'}</span>
          <span className="airport">{flight.destination}</span>
          {flight.gowild_eligible && !flight.blackout_dates?.has_blackout && (
            <span className="gowild-badge" title="Eligible for GoWild Pass redemption">
              🎫 GoWild
            </span>
          )}
          {flight.blackout_dates?.has_blackout && flight.gowild_eligible && (
            <span className="blackout-badge" title={flight.blackout_dates.message}>
              ⚠️ Blackout
            </span>
          )}
        </div>
        <div className="price-section">
          {buildYourOwnMode && buildYourOwnStep === 'complete' ? (
            <>
              <div className="price">${flight.total_price?.toFixed(2) || (flight.price + (flight.return_flight?.price || 0)).toFixed(2)}</div>
              <div className="price-label">Total for Both Flights</div>
            </>
          ) : flight.gowild_eligible ? (
            <>
              <div className="price gowild-price">GoWild Pass</div>
              <div className="price-label gowild-label">+ taxes/fees (~$5-15)</div>
              <div className="regular-price-strikethrough">${flight.price}</div>
            </>
          ) : (
            <>
              <div className="price">{flight.currency || '$'}{flight.price}</div>
              {flight.is_round_trip && <div className="price-label">Total</div>}
            </>
          )}
          {flight.seats_remaining && (
            <div className={`seats-remaining ${flight.seats_remaining <= 3 ? 'low' : ''}`}>
              {flight.seats_remaining <= 9 ? `Only ${flight.seats_remaining} seat${flight.seats_remaining === 1 ? '' : 's'} left!` : `${flight.seats_remaining} seats available`}
            </div>
          )}
        </div>
      </div>

      {flight.blackout_dates?.has_blackout && flight.gowild_eligible && (
        <div className="blackout-warning">
          <span className="warning-icon">⚠️</span>
          <div className="warning-content">
            <strong>GoWild Pass Blackout Period</strong>
            <p>{flight.blackout_dates.message}</p>
            <small>This flight cannot be booked with a GoWild pass during this period.</small>
          </div>
        </div>
      )}

      {flight.is_round_trip ? (
        <div className="round-trip-container">
          {renderFlightSegment(flight, `Outbound (${flight.origin} → ${flight.destination})`)}
          <div className="segment-divider"></div>
          {renderFlightSegment(flight.return_flight, `Return (${flight.destination} → ${flight.origin})`)}
        </div>
      ) : (
        renderFlightSegment(flight, null)
      )}

      <div className="flight-footer">
        <span className="airline">{flight.airline}</span>
        {buildYourOwnMode ? (
          buildYourOwnStep === 'complete' ? (
            <button className="book-button book-trip-button">
              Book This Trip →
            </button>
          ) : (
            <button
              className="select-flight-button"
              onClick={() => onSelectFlight && onSelectFlight(flight)}
            >
              {buildYourOwnStep === 'outbound' ? 'Select Outbound →' : '← Select Return'}
            </button>
          )
        ) : (
          <button className="book-button">View Details</button>
        )}
      </div>
    </div>
  );
}

export default FlightCard;
