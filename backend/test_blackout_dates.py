"""
Test script for GoWild blackout dates functionality
"""
from gowild_blackout import GoWildBlackoutDates
from datetime import datetime, timedelta

def test_blackout_dates():
    """Test various blackout date scenarios"""

    print("=" * 60)
    print("GoWild Blackout Dates Testing")
    print("=" * 60)

    # Test 1: Christmas blackout period
    print("\n1. Testing Christmas Blackout (Dec 25, 2025):")
    result = GoWildBlackoutDates.is_flight_affected_by_blackout('2025-12-25', '2025-12-28')
    print(f"   Has blackout: {result['has_blackout']}")
    print(f"   Message: {result['message']}")

    # Test 2: Non-blackout date
    print("\n2. Testing Non-Blackout Date (Oct 15, 2025):")
    result = GoWildBlackoutDates.is_flight_affected_by_blackout('2025-10-15', '2025-10-20')
    print(f"   Has blackout: {result['has_blackout']}")
    print(f"   Message: {result.get('message', 'No blackout - GoWild eligible!')}")

    # Test 3: Summer peak blackout
    print("\n3. Testing Summer Peak Blackout (July 4, 2025):")
    result = GoWildBlackoutDates.is_flight_affected_by_blackout('2025-07-04', '2025-07-10')
    print(f"   Has blackout: {result['has_blackout']}")
    print(f"   Message: {result['message']}")

    # Test 4: Thanksgiving week
    print("\n4. Testing Thanksgiving Week (Nov 27, 2025):")
    result = GoWildBlackoutDates.is_flight_affected_by_blackout('2025-11-27')
    print(f"   Has blackout: {result['has_blackout']}")
    print(f"   Message: {result['message']}")

    # Test 5: Memorial Day Weekend
    print("\n5. Testing Memorial Day Weekend (May 24, 2025):")
    result = GoWildBlackoutDates.is_flight_affected_by_blackout('2025-05-24', '2025-05-26')
    print(f"   Has blackout: {result['has_blackout']}")
    print(f"   Message: {result['message']}")

    # Test 6: Get all blackout periods
    print("\n6. All Blackout Periods for 2025:")
    periods = GoWildBlackoutDates.get_blackout_periods_in_range('2025-01-01', '2025-12-31')
    for period in periods:
        print(f"   - {period['start']} to {period['end']}: {period['description']}")

    # Test 7: Find next available date
    print("\n7. Find Next Available Date After Christmas:")
    next_date = GoWildBlackoutDates.get_next_available_date('2025-12-25')
    print(f"   Next available: {next_date}")

    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)

if __name__ == '__main__':
    test_blackout_dates()
