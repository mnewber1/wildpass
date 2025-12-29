import React, { useState } from 'react';
import './SearchForm.css';

function SearchForm({ onSearch, loading }) {
  const [searchMode, setSearchMode] = useState('package'); // 'package' or 'build-your-own'
  const [origins, setOrigins] = useState('');
  const [destinations, setDestinations] = useState('');
  const [anyDestination, setAnyDestination] = useState(false);
  const [tripType, setTripType] = useState('round-trip');
  const [departureDate, setDepartureDate] = useState('');
  const [returnDate, setReturnDate] = useState('');
  const [tripLength, setTripLength] = useState('');
  const [tripLengthUnit, setTripLengthUnit] = useState('days');
  const [maxTripDuration, setMaxTripDuration] = useState('');
  const [maxTripDurationUnit, setMaxTripDurationUnit] = useState('days');
  const [nonstopPreferred, setNonstopPreferred] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();

    const originAirports = origins.split(',').map(s => s.trim()).filter(s => s);
    const destinationAirports = anyDestination
      ? ['ANY']
      : destinations.split(',').map(s => s.trim()).filter(s => s);

    const searchParams = {
      searchMode,
      origins: originAirports,
      destinations: destinationAirports,
      tripType: searchMode === 'build-your-own' ? 'one-way' : tripType, // Always one-way for build-your-own
      departureDate,
      returnDate: tripType === 'one-way' || searchMode === 'build-your-own' ? null : returnDate,
    };

    // Add build-your-own specific parameters
    if (searchMode === 'build-your-own' && returnDate) {
      searchParams.desiredReturnDate = returnDate;
    }

    // Add trip planner specific parameters
    if (tripType === 'trip-planner') {
      searchParams.tripLength = tripLength;
      searchParams.tripLengthUnit = tripLengthUnit;
      searchParams.nonstopPreferred = nonstopPreferred;
      if (maxTripDuration) {
        searchParams.maxTripDuration = maxTripDuration;
        searchParams.maxTripDurationUnit = maxTripDurationUnit;
      }
    }

    onSearch(searchParams);
  };

  return (
    <div className="search-form-container">
      <h2>Search Flights</h2>
      <form onSubmit={handleSubmit} className="search-form">
        <div className="form-group">
          <label htmlFor="searchMode">Search Mode</label>
          <div className="trip-type-selector">
            <label className={`trip-type-option ${searchMode === 'package' ? 'active' : ''}`}>
              <input
                type="radio"
                name="searchMode"
                value="package"
                checked={searchMode === 'package'}
                onChange={(e) => setSearchMode(e.target.value)}
              />
              <span>Package Trip</span>
            </label>
            <label className={`trip-type-option ${searchMode === 'build-your-own' ? 'active' : ''}`}>
              <input
                type="radio"
                name="searchMode"
                value="build-your-own"
                checked={searchMode === 'build-your-own'}
                onChange={(e) => setSearchMode(e.target.value)}
              />
              <span>Build Your Own</span>
            </label>
          </div>
          <small>
            {searchMode === 'package'
              ? 'Search for complete round-trip packages'
              : 'Select outbound flight first, then choose your return flight'}
          </small>
        </div>

        {searchMode === 'package' && (
          <div className="form-group">
            <label htmlFor="tripType">Trip Type</label>
            <div className="trip-type-selector">
              <label className={`trip-type-option ${tripType === 'one-way' ? 'active' : ''}`}>
                <input
                  type="radio"
                  name="tripType"
                  value="one-way"
                  checked={tripType === 'one-way'}
                  onChange={(e) => setTripType(e.target.value)}
                />
                <span>One Way</span>
              </label>
              <label className={`trip-type-option ${tripType === 'round-trip' ? 'active' : ''}`}>
                <input
                  type="radio"
                  name="tripType"
                  value="round-trip"
                  checked={tripType === 'round-trip'}
                  onChange={(e) => setTripType(e.target.value)}
                />
                <span>Round Trip</span>
              </label>
              <label className={`trip-type-option ${tripType === 'day-trip' ? 'active' : ''}`}>
                <input
                  type="radio"
                  name="tripType"
                  value="day-trip"
                  checked={tripType === 'day-trip'}
                  onChange={(e) => setTripType(e.target.value)}
                />
                <span>Day Trip</span>
              </label>
              <label className={`trip-type-option ${tripType === 'trip-planner' ? 'active' : ''}`}>
                <input
                  type="radio"
                  name="tripType"
                  value="trip-planner"
                  checked={tripType === 'trip-planner'}
                  onChange={(e) => setTripType(e.target.value)}
                />
                <span>Trip Planner</span>
              </label>
            </div>
          </div>
        )}

        <div className="form-group">
          <label htmlFor="origins">Origin Airports (comma-separated)</label>
          <input
            type="text"
            id="origins"
            value={origins}
            onChange={(e) => setOrigins(e.target.value)}
            placeholder="e.g., DEN, LAX, SFO"
            required
          />
          <small>Enter multiple origin airports separated by commas</small>
        </div>

        <div className="form-group">
          <label htmlFor="destinations">Destination Airports</label>
          <div className="checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={anyDestination}
                onChange={(e) => {
                  setAnyDestination(e.target.checked);
                  if (e.target.checked) {
                    setDestinations('');
                  }
                }}
              />
              <span>Any Airport</span>
            </label>
          </div>
          {!anyDestination && (
            <>
              <input
                type="text"
                id="destinations"
                value={destinations}
                onChange={(e) => setDestinations(e.target.value)}
                placeholder="e.g., MCO, MIA, LAS"
                required={!anyDestination}
              />
              <small>Enter multiple destination airports separated by commas</small>
            </>
          )}
          {anyDestination && (
            <small className="any-destination-note">Will search all available destinations from your origin airports</small>
          )}
        </div>

        {searchMode === 'build-your-own' && (
          <>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="departureDate">Outbound Departure Date</label>
                <input
                  type="date"
                  id="departureDate"
                  value={departureDate}
                  onChange={(e) => setDepartureDate(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="returnDate">Desired Return Date</label>
                <input
                  type="date"
                  id="returnDate"
                  value={returnDate}
                  onChange={(e) => setReturnDate(e.target.value)}
                  required
                />
                <small>We'll show return flights on or near this date</small>
              </div>
            </div>
          </>
        )}

        {searchMode === 'package' && tripType !== 'trip-planner' && (
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="departureDate">
                {tripType === 'day-trip' ? 'Travel Date' : 'Departure Date'}
              </label>
              <input
                type="date"
                id="departureDate"
                value={departureDate}
                onChange={(e) => setDepartureDate(e.target.value)}
                required
              />
            </div>

            {tripType !== 'one-way' && (
              <div className="form-group">
                <label htmlFor="returnDate">
                  {tripType === 'day-trip' ? 'Return Date (same day)' : 'Return Date'}
                </label>
                <input
                  type="date"
                  id="returnDate"
                  value={tripType === 'day-trip' ? departureDate : returnDate}
                  onChange={(e) => setReturnDate(e.target.value)}
                  required
                  disabled={tripType === 'day-trip'}
                />
                {tripType === 'day-trip' && (
                  <small>Automatically set to same day as departure</small>
                )}
              </div>
            )}
          </div>
        )}

        {tripType === 'trip-planner' && (
          <>
            <div className="form-group">
              <label htmlFor="departureDate">Earliest Departure Date</label>
              <input
                type="date"
                id="departureDate"
                value={departureDate}
                onChange={(e) => setDepartureDate(e.target.value)}
                required
              />
              <small>We'll find flights on or after this date</small>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="tripLength">Trip Length</label>
                <input
                  type="number"
                  id="tripLength"
                  value={tripLength}
                  onChange={(e) => setTripLength(e.target.value)}
                  min="1"
                  placeholder="e.g., 3"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="tripLengthUnit">Unit</label>
                <select
                  id="tripLengthUnit"
                  value={tripLengthUnit}
                  onChange={(e) => setTripLengthUnit(e.target.value)}
                  className="unit-select"
                >
                  <option value="hours">Hours</option>
                  <option value="days">Days</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="maxTripDuration">Max Trip Duration (optional)</label>
                <input
                  type="number"
                  id="maxTripDuration"
                  value={maxTripDuration}
                  onChange={(e) => setMaxTripDuration(e.target.value)}
                  min="1"
                  placeholder="e.g., 5"
                />
                <small>Trips longer than this will be filtered out</small>
              </div>

              <div className="form-group">
                <label htmlFor="maxTripDurationUnit">Unit</label>
                <select
                  id="maxTripDurationUnit"
                  value={maxTripDurationUnit}
                  onChange={(e) => setMaxTripDurationUnit(e.target.value)}
                  className="unit-select"
                >
                  <option value="hours">Hours</option>
                  <option value="days">Days</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <div className="checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={nonstopPreferred}
                    onChange={(e) => setNonstopPreferred(e.target.checked)}
                  />
                  <span>Prefer non-stop flights (when available)</span>
                </label>
              </div>
              <small>We'll try to find non-stop options, but show connecting flights if needed</small>
            </div>
          </>
        )}

        <button type="submit" className="search-button" disabled={loading}>
          {loading ? 'Searching...' : 'Search Flights'}
        </button>
      </form>
    </div>
  );
}

export default SearchForm;
