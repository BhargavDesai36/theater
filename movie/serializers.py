# Python imports
from datetime import timedelta
from typing import Any, Dict, List

# External imports
from rest_framework import serializers

# Local imports
from .models import (
    BookedShowDetail,
    Booking,
    Movie,
    Screen,
    ScreenSeatTypesMapping,
    Seat,
    ShowDetail,
    ShowSeatPrice,
)
from .types import SeatTypeDict


class SeatTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreenSeatTypesMapping
        fields = ["id", "seat_type"]


class ScreenSerializer(serializers.ModelSerializer):
    seat_type = SeatTypeSerializer(many=True, source="seat_screen")

    class Meta:
        model = Screen
        fields = ["id", "screen_number", "total_seat", "seat_type"]

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if data.get("total_seat", 0) < 0:
            raise serializers.ValidationError("Total seats cannot be negative")
        return data


class SeatSerializer(serializers.Serializer):
    rows = serializers.IntegerField()
    columns = serializers.IntegerField()
    order = serializers.IntegerField()
    seat_type = serializers.CharField()


class AddScreenSerializer(serializers.Serializer):
    screen_number = serializers.IntegerField()
    seat_types = serializers.ListField(child=serializers.DictField(), allow_empty=False)

    def validate_seat_types(self, value: List[Dict[str, Any]]) -> List[SeatTypeDict]:
        for seat_type in value:
            if not all(
                k in seat_type for k in ("seat_type", "rows", "columns", "order")
            ):
                raise serializers.ValidationError(
                    "Each seat type must contain seat_type, rows, columns, and order"
                )
        return value


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["id", "title", "description", "release_date"]
        read_only_fields = ("id",)


class UpdateShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowDetail
        fields = [
            "id",
            "movie",
            "start_time",
            "end_time",
            "screen",
            "available_seats",
            "start_date",
            "end_date",
        ]
        read_only_fields = ("id",)
        extra_kwargs = {
            "movie": {"required": False},
            "start_time": {"required": False},
            "end_time": {"required": False},
            "screen": {"required": False},
            "available_seats": {"required": False},
            "start_date": {"required": False},
            "end_date": {"required": False},
        }


class ShowPricesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSeatPrice
        fields = ["id", "seat_type", "price"]
        read_only_fields = ("id",)


class BookedShowDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookedShowDetail
        fields = ["id", "show_date", "available_seats", "show_detail"]


class ShowDetailSerializer(serializers.ModelSerializer):
    show_prices = ShowPricesSerializer(many=True)
    booked_show = BookedShowDetailSerializer(many=True, required=False)
    available_seats = serializers.IntegerField(
        source="screen.total_seat", required=False
    )
    title = serializers.CharField(source="movie.title", required=False)
    screen_number = serializers.CharField(source="screen.screen_number", required=False)
    seats = serializers.SerializerMethodField()
    prices = serializers.ListField(child=serializers.DictField(), required=False)

    class Meta:
        model = ShowDetail
        fields = [
            "id",
            "movie",
            "start_time",
            "end_time",
            "screen",
            "available_seats",
            "start_date",
            "end_date",
            "show_prices",
            "title",
            "screen_number",
            "seats",
            "booked_show",
            "prices",
        ]
        read_only_fields = ("id", "title", "screen_number")

    def get_seats(self, obj) -> list:
        if isinstance(obj, ShowDetail):
            booked_seat = Booking.objects.filter(showtime__id=obj.id).values_list(
                "seats", flat=True
            )
            seats = (
                Seat.objects.filter(type__screen=obj.screen)
                .values("seat_number", "type__seat_type", "id")
                .exclude(id__in=booked_seat)
            )
            return seats
        return None

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if data.get("start_date") > data.get("end_date"):
            raise serializers.ValidationError("End date must be after start date")
        return data

    def save(self) -> dict:
        validated_data = self.validated_data.copy()
        screen = validated_data["screen"]
        available_seats = screen.total_seat
        show_prices = validated_data.pop("show_prices")

        show_detail = ShowDetail.objects.create(
            **validated_data, available_seats=available_seats
        )

        for show_price in show_prices:
            ShowSeatPrice.objects.create(show_detail=show_detail, **show_price)

        show_start_date = show_detail.start_date
        show_end_date = show_detail.end_date

        for day in range((show_end_date - show_start_date).days + 1):
            BookedShowDetail.objects.create(
                show_detail=show_detail,
                show_date=show_start_date + timedelta(days=day),
                available_seats=available_seats,
            )

        return self.validated_data


class UserShowDetailSerializer(serializers.ModelSerializer):
    available_seats = serializers.IntegerField(
        source="screen.total_seat", required=False
    )
    title = serializers.CharField(source="movie.title", required=False)
    screen_number = serializers.CharField(source="screen.screen_number", required=False)

    class Meta:
        model = ShowDetail
        fields = [
            "id",
            "movie",
            "start_time",
            "end_time",
            "screen",
            "available_seats",
            "start_date",
            "end_date",
            "title",
            "screen_number",
        ]
        read_only_fields = ("id", "title", "screen_number")


class BookingSerializer(serializers.ModelSerializer):
    show_time = UserShowDetailSerializer(required=False, source="showtime")
    show_date = serializers.DateField(required=False)

    class Meta:
        model = Booking
        fields = "__all__"

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not data.get("seats"):
            raise serializers.ValidationError("Seats are required")
        return data
