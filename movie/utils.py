# Python imports
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Django imports
from django.core.cache import cache
from django.db.models import QuerySet
from django.utils import timezone

# External imports
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

# App imports
from movie.models import (
    Booking,
    Screen,
    ScreenSeatTypesMapping,
    Seat,
    ShowDetail,
)

# Local imports
from .constants import (
    DEFAULT_PAGE_SIZE,
    ERROR_MESSAGES,
    MAX_PAGE_SIZE,
    MAX_SEATS_PER_BOOKING,
    MIN_BOOKING_HOURS_BEFORE,
    MIN_SEATS_PER_BOOKING,
    SHOW_CACHE_TIMEOUT,
)
from .types import SeatTypeDict


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination class for consistent pagination across the application.

    Attributes:
        page_size (int): Number of items per page
        page_size_query_param (str): Query parameter to specify page size
        max_page_size (int): Maximum allowed page size
    """

    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = MAX_PAGE_SIZE

    def get_paginated_response(self, data: List[Any]) -> Response:
        """
        Customizes the pagination response format.

        Args:
            data: The paginated data

        Returns:
            Response: Formatted pagination response
        """
        return Response(
            {
                "total_pages": self.page.paginator.num_pages,
                "total_items": self.page.paginator.count,
                "current_page": self.page.number,
                "page_size": self.page_size,
                "results": data,
            }
        )


def create_screen_with_seats(
    screen_number: int, seat_types: List[SeatTypeDict]
) -> Screen:
    """
    Create a new screen with associated seats.

    Args:
        screen_number: The screen number to create
        seat_types: List of seat type configurations

    Returns:
        Screen: The created screen instance
    """
    screen = Screen.objects.create(screen_number=screen_number)
    rows = 1
    total_seat = 0

    for seat_type in seat_types:
        screen_seat = ScreenSeatTypesMapping.objects.create(
            screen=screen, seat_type=seat_type["seat_type"]
        )

        type_row = seat_type["rows"] + rows
        type_col = seat_type["columns"]

        for i in range(rows, type_row):
            for j in range(type_col):
                Seat.objects.create(
                    seat_number=f"{i}{j}",
                    row=rows + i,
                    col=j + 1,
                    type=screen_seat,
                )

        rows = type_row
        total_seat += seat_type["rows"] * seat_type["columns"]

    screen.total_seat = total_seat
    screen.save()

    return screen


def order_seat_types(seat_types: List[SeatTypeDict]) -> List[SeatTypeDict]:
    """
    Order seat types based on their order field.

    Args:
        seat_types: List of unordered seat type configurations

    Returns:
        List[SeatTypeDict]: Ordered list of seat type configurations
    """
    seat_types_ordered: List[SeatTypeDict] = [{}] * len(seat_types)  # type: ignore
    for seat_type in seat_types:
        seat_types_ordered[seat_type["order"] - 1] = seat_type
    return seat_types_ordered


def get_available_seats(show_id: int, show_date: datetime) -> QuerySet[Seat]:
    """
    Get available seats for a show on a specific date.

    Args:
        show_id: ID of the show
        show_date: Date of the show

    Returns:
        QuerySet[Seat]: QuerySet of available seats
    """
    cache_key = f"available_seats_{show_id}_{show_date.strftime('%Y%m%d')}"
    cached_seats = cache.get(cache_key)

    if cached_seats is not None:
        return cached_seats

    booked_seats = Booking.objects.filter(
        showtime_id=show_id, booked_show__show_date=show_date
    ).values_list("seats", flat=True)

    available_seats = Seat.objects.exclude(id__in=booked_seats)

    cache.set(cache_key, available_seats, SHOW_CACHE_TIMEOUT)
    return available_seats


def validate_booking_request(
    seats: List[int], show: ShowDetail, show_date: datetime
) -> None:
    """
    Validate a booking request.

    Args:
        seats: List of seat IDs to book
        show: ShowDetail instance
        show_date: Date of the show

    Raises:
        ValidationError: If the booking request is invalid
    """
    if not MIN_SEATS_PER_BOOKING <= len(seats) <= MAX_SEATS_PER_BOOKING:
        raise ValidationError(ERROR_MESSAGES["invalid_seat_count"])

    if show_date < timezone.now().date():
        raise ValidationError(ERROR_MESSAGES["past_show"])

    show_datetime = datetime.combine(show_date, show.start_time)
    if show_datetime - timezone.now() < timedelta(hours=MIN_BOOKING_HOURS_BEFORE):
        raise ValidationError(ERROR_MESSAGES["booking_window_expired"])

    available_seats = get_available_seats(show.id, show_date)
    if not all(
        seat_id in available_seats.values_list("id", flat=True) for seat_id in seats
    ):
        raise ValidationError(ERROR_MESSAGES["seats_unavailable"])


def get_show_seat_layout(screen_id: int) -> Dict[str, Any]:
    """
    Get the seat layout for a screen.

    Args:
        screen_id: ID of the screen

    Returns:
        Dict[str, Any]: Seat layout configuration
    """
    cache_key = f"seat_layout_{screen_id}"
    cached_layout = cache.get(cache_key)

    if cached_layout is not None:
        return cached_layout

    screen_seats = ScreenSeatTypesMapping.objects.filter(screen_id=screen_id)
    layout = {}

    for seat_type in screen_seats:
        seats = Seat.objects.filter(type=seat_type)
        max_row = seats.order_by("-row").first().row if seats.exists() else 0
        max_col = seats.order_by("-col").first().col if seats.exists() else 0

        layout[seat_type.seat_type] = {
            "rows": max_row,
            "columns": max_col,
            "seats": list(seats.values("id", "seat_number", "row", "col")),
        }

    cache.set(cache_key, layout)
    return layout


def calculate_total_price(seats: List[int], show_id: int) -> float:
    """
    Calculate total price for selected seats.

    Args:
        seats: List of seat IDs
        show_id: ID of the show

    Returns:
        float: Total price
    """
    seat_types = Seat.objects.filter(id__in=seats).values_list(
        "type__seat_type", flat=True
    )
    prices = ShowDetail.objects.get(id=show_id).show_price_detail.all()

    total = 0.0
    for seat_type in seat_types:
        price = next((p.price for p in prices if p.seat_type.seat_type == seat_type), 0)
        total += price

    return total
