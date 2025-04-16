# Python imports
import uuid

# Django imports
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

# App imports
from user.models import User


class Screen(models.Model):
    """
    Screen: It stores the screen detail

    Fields:
        screen_number (int): It stores the screen number
        total_seat (int): It stores the total seat
    """

    screen_number = models.IntegerField(null=False, db_index=True)
    total_seat = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["screen_number"]
        verbose_name = "Screen"
        verbose_name_plural = "Screens"

    def clean(self):
        if self.total_seat is not None and self.total_seat < 0:
            raise ValidationError("Total seats cannot be negative")

    def __str__(self) -> str:
        return f"{self.screen_number} - {self.total_seat}"


class SeatType(models.TextChoices):
    """Seat types available in the theater"""

    PLATINUM = "PLATINUM", _("Platinum")
    GOLD = "GOLD", _("Gold")
    SILVER = "SILVER", _("Silver")

    UNKNOWN = "UNKNOWN", _("Unknown")


class ScreenSeatTypesMapping(models.Model):
    """
    SeatPrice: It stores the seat price

    Fields:
        seat_type (SeatType): It stores the seat type
        screen (Screen): It stores the screen
    """

    seat_type = models.CharField(
        max_length=10, choices=SeatType.choices, default=SeatType.SILVER
    )
    screen = models.ForeignKey(
        Screen,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="seat_screen",
    )

    def __str__(self) -> str:
        return f"{self.seat_type}"


class Seat(models.Model):
    """
    Seat: It stores the seat detail

    Fields:
        seat_number (int): It stores the seat number
        seat_price (SeatPrice): It stores the seat price
        row (int): It stores the row number of seat
        col (int): It stores the col number of seat
    """

    seat_number = models.CharField(max_length=10, db_index=True)
    row = models.CharField(max_length=3)
    col = models.CharField(max_length=3)
    type = models.ForeignKey(
        ScreenSeatTypesMapping,
        on_delete=models.CASCADE,
        related_name="seat_type_screen",
    )

    class Meta:
        ordering = ["row", "col"]
        unique_together = ["row", "col", "type"]

    def __str__(self) -> str:
        return f"{self.seat_number}"


class Movie(models.Model):
    """
    Movie: It stores movie detail which released or going to release.

    Fields:
        id (string): Unique identifier for the movie data
        title (string): Movie title
        description (string): Movie description
        release_date (date): Movie release date
    """

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()

    def __str__(self) -> str:
        return self.title


class ShowDetail(models.Model):
    """
    ShowDetail: It stores movie show detail

    Fields:
        movie (Movie): It stores movie
        start_time (datetime): It stores start time
        end_time (datetime): It stores end time
        screen (Screen): It stores screen
        available_seats (int): It stores available seats
        start_date (date): It stores start date
        end_date (date): It stores end date
    """

    movie = models.ForeignKey(
        Movie, related_name="showtime_movie", on_delete=models.CASCADE
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    screen = models.ForeignKey(
        Screen, related_name="showtime_screen", on_delete=models.CASCADE
    )
    available_seats = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self) -> str:
        return f"{self.movie.title} at {self.start_time}"


class ShowSeatPrice(models.Model):
    """
    ShowSeatPrice: It stores show seat price

    Fields:
        show_detail (ShowDetail): It stores show detail
        seat_type (SeatType): It stores seat type
        price (float): It stores price
    """

    show_detail = models.ForeignKey(
        ShowDetail, on_delete=models.CASCADE, related_name="show_price_detail"
    )
    seat_type = models.ForeignKey(
        ScreenSeatTypesMapping, on_delete=models.CASCADE, related_name="seat_price"
    )
    price = models.FloatField()

    def __str__(self) -> str:
        return f"{self.show_detail} - {self.seat_type} -> {self.price}"


class BookedShowDetail(models.Model):
    """
    BookedShowDetail: It stores booked show detail

    Fields:
        show_detail (ShowDetail): It stores show detail
        show_date (date): It stores show date
        available_seats (int): It stores available seats
    """

    show_detail = models.ForeignKey(
        ShowDetail, on_delete=models.CASCADE, related_name="booked_show_detail"
    )
    show_date = models.DateField()
    available_seats = models.IntegerField()


class Booking(models.Model):
    """
    Booking: It stores booking detail

    Fields:
        user (User): It stores user
        showtime (ShowDetail): It stores showtime
        booked_show (BookedShowDetail): It stores booked show
        seats (Seat): It stores seats
    """

    user = models.ForeignKey(
        User, related_name="booking_user", on_delete=models.CASCADE
    )
    showtime = models.ForeignKey(
        ShowDetail,
        on_delete=models.CASCADE,
        related_name="booking_showtime",
        null=True,
        blank=True,
    )
    booked_show = models.ForeignKey(
        BookedShowDetail,
        on_delete=models.CASCADE,
        related_name="booking_booked_show",
        null=True,
        blank=True,
    )
    seats = models.ManyToManyField(Seat, related_name="booking_seats")

    def __str__(self) -> str:
        return f"{self.user.username} - {self.showtime}"
