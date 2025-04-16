# Python imports
from datetime import timedelta

# Django imports
from django.test import override_settings
from django.utils import timezone

# External imports
from rest_framework.exceptions import ValidationError

# App imports
from movie.constants import (
    ERROR_MESSAGES,
    MAX_SEATS_PER_BOOKING,
)
from movie.utils import (
    calculate_total_price,
    get_available_seats,
    get_show_seat_layout,
    validate_booking_request,
)
from tests.test_helpers.constants import DEFAULT_DATABASE
from tests.test_helpers.testing import APIBaseTestCase

# Local imports
from .logger import TestingLogger as Logger


class UtilsTestCase(APIBaseTestCase):
    databases = [DEFAULT_DATABASE]

    def setUp(self) -> None:
        super().setUp()
        self.seed_database(DEFAULT_DATABASE)

    def test_calculate_total_price(self) -> None:
        seats = self.seats[:2]
        seat_ids = [seat.id for seat in seats]

        total_price = calculate_total_price(seat_ids, self.show_detail.id)

        Logger.info(
            {
                "message": "calculate total price",
                "total_price": total_price,
                "event": "test_calculate_total_price",
            }
        )

        expected_price = sum(
            price.price
            for price in self.show_seat_prices
            for seat in seats
            if seat.type.seat_type == price.seat_type.seat_type
        )

        self.assertEqual(total_price, expected_price)

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_get_available_seats(self) -> None:
        show_date = timezone.now().date()

        available_seats = get_available_seats(self.show_detail.id, show_date)

        Logger.info(
            {
                "message": "get available seats",
                "seats_count": len(available_seats),
                "event": "test_get_available_seats",
            }
        )

        self.assertEqual(available_seats.count(), len(self.seats))

        self.create_test_booking(self.seats[:2])

        available_seats = get_available_seats(self.show_detail.id, show_date)
        self.assertEqual(available_seats.count(), len(self.seats) - 2)

    def test_validate_booking_request_valid(self) -> None:
        seats = self.seats[:2]
        seat_ids = [seat.id for seat in seats]
        show_date = timezone.now().date() + timedelta(days=1)

        validate_booking_request(seat_ids, self.show_detail, show_date)

        Logger.info(
            {
                "message": "validate booking request - valid case",
                "event": "test_validate_booking_request_valid",
            }
        )

    def test_validate_booking_request_invalid_seat_count(self) -> None:
        seats = self.seats[: MAX_SEATS_PER_BOOKING + 1]
        seat_ids = [seat.id for seat in seats]
        show_date = timezone.now().date() + timedelta(days=1)

        with self.assertRaises(ValidationError) as context:
            validate_booking_request(seat_ids, self.show_detail, show_date)

        Logger.info(
            {
                "message": "validate booking request - invalid seat count",
                "error": str(context.exception),
                "event": "test_validate_booking_request_invalid_seat_count",
            }
        )

        self.assertEqual(str(context.exception), ERROR_MESSAGES["invalid_seat_count"])

    def test_validate_booking_request_past_date(self) -> None:
        seats = self.seats[:2]
        seat_ids = [seat.id for seat in seats]
        show_date = timezone.now().date() - timedelta(days=1)

        with self.assertRaises(ValidationError) as context:
            validate_booking_request(seat_ids, self.show_detail, show_date)

        Logger.info(
            {
                "message": "validate booking request - past date",
                "error": str(context.exception),
                "event": "test_validate_booking_request_past_date",
            }
        )

        self.assertEqual(str(context.exception), ERROR_MESSAGES["past_show"])

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_get_show_seat_layout(self) -> None:
        layout = get_show_seat_layout(self.screen.id)

        Logger.info(
            {
                "message": "get show seat layout",
                "layout": layout,
                "event": "test_get_show_seat_layout",
            }
        )

        self.assertIn("PLATINUM", layout)
        self.assertIn("GOLD", layout)
        self.assertIn("SILVER", layout)

        for seat_type in layout.values():
            self.assertIn("rows", seat_type)
            self.assertIn("columns", seat_type)
            self.assertIn("seats", seat_type)

        cached_layout = get_show_seat_layout(self.screen.id)
        self.assertEqual(layout, cached_layout)

    def create_test_booking(self, seats):
        # App imports
        from movie.models import Booking

        booking = Booking.objects.create(
            user=self.user,
            showtime=self.show_detail,
            booked_show=self.booked_show_detail,
        )
        booking.seats.set(seats)
        return booking
