"""
GoWild Pass Blackout Dates Configuration

This module defines blackout dates when GoWild passes cannot be used.
Based on Frontier Airlines GoWild pass terms and conditions.
"""
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

class GoWildBlackoutDates:
    """
    Manages GoWild pass blackout dates and restrictions.

    Frontier GoWild pass typically has blackout dates during:
    - Major holidays (Thanksgiving, Christmas, New Year's)
    - Peak travel periods (Spring Break, Summer peak)
    - Special event weekends
    """

    # Define blackout date ranges for 2025-2026
    # Format: (start_date, end_date, description)
    BLACKOUT_PERIODS_2025 = [
        # New Year's 2025
        ("2025-01-01", "2025-01-02", "New Year's Day"),

        # Martin Luther King Jr. Weekend
        ("2025-01-17", "2025-01-20", "MLK Weekend"),

        # Presidents Day Weekend
        ("2025-02-14", "2025-02-17", "Presidents Day Weekend"),

        # Spring Break (varies by region, using typical peak)
        ("2025-03-07", "2025-03-23", "Spring Break Peak"),

        # Easter Weekend
        ("2025-04-17", "2025-04-21", "Easter Weekend"),

        # Memorial Day Weekend
        ("2025-05-23", "2025-05-26", "Memorial Day Weekend"),

        # Summer Peak Travel
        ("2025-06-20", "2025-08-17", "Summer Peak Season"),

        # Labor Day Weekend
        ("2025-08-29", "2025-09-01", "Labor Day Weekend"),

        # Thanksgiving Week
        ("2025-11-22", "2025-11-30", "Thanksgiving Week"),

        # Christmas and New Year's
        ("2025-12-19", "2026-01-04", "Christmas & New Year's"),
    ]

    BLACKOUT_PERIODS_2026 = [
        # Martin Luther King Jr. Weekend
        ("2026-01-16", "2026-01-19", "MLK Weekend"),

        # Presidents Day Weekend
        ("2026-02-13", "2026-02-16", "Presidents Day Weekend"),

        # Spring Break
        ("2026-03-06", "2026-03-22", "Spring Break Peak"),

        # Easter Weekend
        ("2026-04-03", "2026-04-06", "Easter Weekend"),

        # Memorial Day Weekend
        ("2026-05-22", "2026-05-25", "Memorial Day Weekend"),

        # Summer Peak Travel
        ("2026-06-19", "2026-08-16", "Summer Peak Season"),

        # Labor Day Weekend
        ("2026-08-28", "2026-08-31", "Labor Day Weekend"),

        # Thanksgiving Week
        ("2026-11-21", "2026-11-29", "Thanksgiving Week"),

        # Christmas and New Year's
        ("2026-12-18", "2027-01-03", "Christmas & New Year's"),
    ]

    @classmethod
    def get_all_blackout_periods(cls) -> List[Tuple[datetime, datetime, str]]:
        """
        Get all blackout periods as datetime objects.

        Returns:
            List of tuples: (start_datetime, end_datetime, description)
        """
        all_periods = []

        for start_str, end_str, description in cls.BLACKOUT_PERIODS_2025 + cls.BLACKOUT_PERIODS_2026:
            start_date = datetime.strptime(start_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_str, '%Y-%m-%d')
            all_periods.append((start_date, end_date, description))

        return all_periods

    @classmethod
    def is_blackout_date(cls, date_to_check: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a given date falls within a blackout period.

        Args:
            date_to_check: Date string in 'YYYY-MM-DD' format

        Returns:
            Tuple of (is_blackout, reason)
            - is_blackout: True if date is in blackout period
            - reason: Description of blackout period (if applicable)
        """
        try:
            check_date = datetime.strptime(date_to_check, '%Y-%m-%d')
        except ValueError:
            return (False, None)

        for start_date, end_date, description in cls.get_all_blackout_periods():
            if start_date <= check_date <= end_date:
                return (True, description)

        return (False, None)

    @classmethod
    def is_flight_affected_by_blackout(cls, departure_date: str, return_date: Optional[str] = None) -> dict:
        """
        Check if a flight is affected by blackout dates.

        For round-trip flights, checks both departure and return dates.

        Args:
            departure_date: Departure date in 'YYYY-MM-DD' format
            return_date: Optional return date in 'YYYY-MM-DD' format

        Returns:
            Dictionary with blackout information:
            {
                'has_blackout': bool,
                'departure_blackout': bool,
                'return_blackout': bool,
                'departure_reason': str or None,
                'return_reason': str or None,
                'message': str
            }
        """
        result = {
            'has_blackout': False,
            'departure_blackout': False,
            'return_blackout': False,
            'departure_reason': None,
            'return_reason': None,
            'message': None
        }

        # Check departure date
        is_blackout, reason = cls.is_blackout_date(departure_date)
        if is_blackout:
            result['has_blackout'] = True
            result['departure_blackout'] = True
            result['departure_reason'] = reason

        # Check return date if provided
        if return_date:
            is_blackout, reason = cls.is_blackout_date(return_date)
            if is_blackout:
                result['has_blackout'] = True
                result['return_blackout'] = True
                result['return_reason'] = reason

        # Generate message
        if result['departure_blackout'] and result['return_blackout']:
            result['message'] = f"GoWild blackout: {result['departure_reason']} (departure) and {result['return_reason']} (return)"
        elif result['departure_blackout']:
            result['message'] = f"GoWild blackout: {result['departure_reason']}"
        elif result['return_blackout']:
            result['message'] = f"GoWild blackout: {result['return_reason']}"

        return result

    @classmethod
    def get_next_available_date(cls, start_date: str) -> Optional[str]:
        """
        Find the next available (non-blackout) date after the given date.

        Args:
            start_date: Starting date in 'YYYY-MM-DD' format

        Returns:
            Next available date as string, or None if not found within 90 days
        """
        try:
            current = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            return None

        # Search up to 90 days ahead
        for i in range(90):
            current += timedelta(days=1)
            date_str = current.strftime('%Y-%m-%d')
            is_blackout, _ = cls.is_blackout_date(date_str)
            if not is_blackout:
                return date_str

        return None

    @classmethod
    def get_blackout_periods_in_range(cls, start_date: str, end_date: str) -> List[dict]:
        """
        Get all blackout periods that fall within a date range.

        Args:
            start_date: Range start in 'YYYY-MM-DD' format
            end_date: Range end in 'YYYY-MM-DD' format

        Returns:
            List of blackout period dictionaries with start, end, and description
        """
        try:
            range_start = datetime.strptime(start_date, '%Y-%m-%d')
            range_end = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return []

        affected_periods = []

        for blackout_start, blackout_end, description in cls.get_all_blackout_periods():
            # Check if blackout period overlaps with range
            if blackout_start <= range_end and blackout_end >= range_start:
                affected_periods.append({
                    'start': blackout_start.strftime('%Y-%m-%d'),
                    'end': blackout_end.strftime('%Y-%m-%d'),
                    'description': description
                })

        return affected_periods
