# Python imports
from typing import Dict, Final

# Seat related constants
DEFAULT_SEAT_CAPACITY: Final[int] = 100
MIN_SEATS_PER_BOOKING: Final[int] = 1
MAX_SEATS_PER_BOOKING: Final[int] = 10

# Time related constants
SHOW_DURATION_MINUTES: Final[int] = 180  # 3 hours
BOOKING_WINDOW_DAYS: Final[int] = 30  # Advance booking window
MIN_BOOKING_HOURS_BEFORE: Final[int] = 2  # Minimum hours before show for booking

# Cache keys and timeouts
MOVIE_CACHE_TIMEOUT: Final[int] = 3600  # 1 hour
SHOW_CACHE_TIMEOUT: Final[int] = 1800  # 30 minutes
SEAT_LAYOUT_CACHE_TIMEOUT: Final[int] = 3600  # 1 hour

# Pagination
DEFAULT_PAGE_SIZE: Final[int] = 10
MAX_PAGE_SIZE: Final[int] = 100

# Seat layout configuration
DEFAULT_SEAT_LAYOUT: Final[Dict[str, Dict[str, int]]] = {
    "PLATINUM": {"rows": 4, "columns": 10},
    "GOLD": {"rows": 6, "columns": 10},
    "SILVER": {"rows": 8, "columns": 10},
}

# Error Messages
ERROR_MESSAGES: Final[Dict[str, str]] = {
    "seats_unavailable": "The selected seats are not available",
    "invalid_seat_count": f"Number of seats must be between {MIN_SEATS_PER_BOOKING} and {MAX_SEATS_PER_BOOKING}",
    "show_full": "This show is fully booked",
    "past_show": "Cannot book tickets for past shows",
    "booking_window_expired": f"Booking must be done at least {MIN_BOOKING_HOURS_BEFORE} hours before show time",
    "invalid_date_range": "End date must be after start date",
}
