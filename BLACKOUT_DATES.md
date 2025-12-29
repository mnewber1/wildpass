# GoWild Blackout Dates Feature

## Overview

WildPass now includes automatic detection and warnings for GoWild Pass blackout dates. This feature helps users avoid attempting to book flights during periods when GoWild passes cannot be used.

## Features

### Backend Implementation

#### 1. Blackout Dates Configuration (`backend/gowild_blackout.py`)

A comprehensive module that manages GoWild blackout dates:

- **Predefined Blackout Periods**: Configured for 2025-2026
  - New Year's Day
  - MLK Weekend
  - Presidents Day Weekend
  - Spring Break Peak (March)
  - Easter Weekend
  - Memorial Day Weekend
  - Summer Peak Season (June 20 - August 17)
  - Labor Day Weekend
  - Thanksgiving Week
  - Christmas & New Year's (December 19 - January 4)

- **Key Functions**:
  - `is_blackout_date(date)`: Check if a specific date is in a blackout period
  - `is_flight_affected_by_blackout(departure, return)`: Check if flight dates are affected
  - `get_next_available_date(date)`: Find the next available non-blackout date
  - `get_blackout_periods_in_range(start, end)`: Get all blackout periods in a date range

#### 2. API Integration

**Updated Files**:
- `backend/amadeus_api.py`: Flight data now includes blackout information
- `backend/app.py`: Mock data generation includes blackout checks

**Response Format**:
```json
{
  "blackout_dates": {
    "has_blackout": true,
    "departure_blackout": true,
    "return_blackout": false,
    "departure_reason": "Summer Peak Season",
    "return_reason": null,
    "message": "GoWild blackout: Summer Peak Season"
  }
}
```

### Frontend Implementation

#### 1. Visual Indicators

**FlightCard Component** ([src/components/FlightCard.js](src/components/FlightCard.js)):

- **Blackout Badge**: Red warning badge replaces green GoWild badge when blackout detected
  - Shows "⚠️ Blackout" with pulsing animation
  - Tooltip displays blackout period details

- **Warning Banner**: Prominent warning message for affected flights
  - Red gradient background
  - Clear explanation of blackout restriction
  - Details about which dates are affected

#### 2. Styling

**New CSS Classes** ([src/components/FlightCard.css](src/components/FlightCard.css)):

- `.blackout-badge`: Red warning badge with pulse animation
- `.blackout-warning`: Warning banner with gradient background
- `.warning-icon`: Large warning emoji
- `.warning-content`: Formatted warning text

## Blackout Periods for 2025

| Period | Dates | Description |
|--------|-------|-------------|
| New Year's | Jan 1-2 | New Year's Day |
| MLK Weekend | Jan 17-20 | Martin Luther King Jr. Weekend |
| Presidents Day | Feb 14-17 | Presidents Day Weekend |
| Spring Break | Mar 7-23 | Spring Break Peak Season |
| Easter | Apr 17-21 | Easter Weekend |
| Memorial Day | May 23-26 | Memorial Day Weekend |
| Summer Peak | Jun 20 - Aug 17 | Summer Peak Travel Season |
| Labor Day | Aug 29 - Sep 1 | Labor Day Weekend |
| Thanksgiving | Nov 22-30 | Thanksgiving Week |
| Christmas/New Year's | Dec 19 - Jan 4 | Christmas & New Year's |

## Testing

### Run Blackout Date Tests

```bash
cd backend
python3 test_blackout_dates.py
```

This will test:
- Christmas blackout detection
- Non-blackout date handling
- Summer peak period
- Thanksgiving week
- Memorial Day weekend
- All 2025 blackout periods
- Next available date finder

### Example Test Output

```
============================================================
GoWild Blackout Dates Testing
============================================================

1. Testing Christmas Blackout (Dec 25, 2025):
   Has blackout: True
   Message: GoWild blackout: Christmas & New Year's (departure) and Christmas & New Year's (return)

2. Testing Non-Blackout Date (Oct 15, 2025):
   Has blackout: False
   Message: No blackout - GoWild eligible!

...
```

## User Experience

### For GoWild Pass Holders

1. **Search Results**: Flights during blackout periods show red warning badge
2. **Clear Warnings**: Detailed message explains why GoWild pass can't be used
3. **Date Awareness**: Users can see all blackout periods before searching
4. **Smart Planning**: Helps users choose alternative dates

### Visual Flow

```
Regular GoWild Flight:
[DEN ⇄ MCO] 🎫 GoWild   $199  →  Shows as "GoWild Pass + taxes"

Blackout Period Flight:
[DEN ⇄ MCO] ⚠️ Blackout  $199  →  Shows warning banner with details
```

## Implementation Details

### Backend Architecture

```
FlightSearch Request
    ↓
Amadeus API / Mock Data
    ↓
For each flight:
  1. Parse departure/return dates
  2. Check against blackout periods
  3. Add blackout_dates object to response
    ↓
Return enriched flight data
```

### Frontend Logic

```javascript
// In FlightCard.js
{flight.blackout_dates?.has_blackout && flight.gowild_eligible && (
  <div className="blackout-warning">
    <span>⚠️</span>
    <div>
      <strong>GoWild Pass Blackout Period</strong>
      <p>{flight.blackout_dates.message}</p>
    </div>
  </div>
)}
```

## Configuration

### Adding New Blackout Periods

Edit `backend/gowild_blackout.py`:

```python
BLACKOUT_PERIODS_2026 = [
    ("2026-07-04", "2026-07-06", "Independence Day Weekend"),
    # Add more periods...
]
```

### Customizing Blackout Rules

The `GoWildBlackoutDates` class can be extended to:
- Add route-specific blackouts
- Implement dynamic blackout date fetching
- Add special event blackouts
- Configure regional blackout variations

## API Changes

### Flight Response Schema (Updated)

```json
{
  "origin": "DEN",
  "destination": "MCO",
  "departure_date": "2025-12-25",
  "price": 199.00,
  "gowild_eligible": true,
  "blackout_dates": {
    "has_blackout": true,
    "departure_blackout": true,
    "return_blackout": true,
    "departure_reason": "Christmas & New Year's",
    "return_reason": "Christmas & New Year's",
    "message": "GoWild blackout: Christmas & New Year's (departure) and Christmas & New Year's (return)"
  }
}
```

## Future Enhancements

- [ ] Dynamic blackout date updates from Frontier API
- [ ] User notifications for blackout periods in saved searches
- [ ] Calendar view showing blackout dates
- [ ] Alternative date suggestions when blackout detected
- [ ] Route-specific blackout periods
- [ ] Integration with email alerts for blackout changes

## Files Modified

### Backend
- ✅ `backend/gowild_blackout.py` (new)
- ✅ `backend/amadeus_api.py`
- ✅ `backend/app.py`
- ✅ `backend/test_blackout_dates.py` (new)

### Frontend
- ✅ `src/components/FlightCard.js`
- ✅ `src/components/FlightCard.css`

### Documentation
- ✅ `README.md`
- ✅ `BLACKOUT_DATES.md` (this file)

## Support

For questions or issues with blackout date detection:
1. Run `python3 test_blackout_dates.py` to verify configuration
2. Check console logs for blackout date calculations
3. Review `gowild_blackout.py` for date range definitions

---

**Note**: Blackout dates are based on typical Frontier GoWild pass restrictions and should be verified against current Frontier Airlines terms and conditions.
