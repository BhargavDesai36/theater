# Python imports
from datetime import timedelta

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


class SeatTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreenSeatTypesMapping
        fields = ["id", "seat_type"]


class ScreenSerializer(serializers.ModelSerializer):
    seat_type = SeatTypeSerializer(many=True, source="seat_screen")

    class Meta:
        model = Screen
        fields = ["id", "screen_number", "total_seat", "seat_type"]


class SeatSerializer(serializers.Serializer):
    rows = serializers.IntegerField()
    columns = serializers.IntegerField()
    order = serializers.IntegerField()
    seat_type = serializers.CharField()


class AddScreenSerializer(serializers.Serializer):
    screen_number = serializers.IntegerField()
    seat_types = SeatSerializer(many=True)


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

    def validate(self, attrs) -> dict:
        start_time = attrs["start_time"]
        end_time = attrs["end_time"]

        start_date = attrs["start_date"]
        end_date = attrs["end_date"]

        if start_time >= end_time:
            raise serializers.ValidationError("Start time must be before end time")

        if start_date >= end_date:
            raise serializers.ValidationError("Start date must be before end date")

        # check in ShowDetail if any other show is ongoing in same time and same screen
        show_detail = ShowDetail.objects.filter(
            start_time__range=(start_time, end_time),
            end_time__range=(start_time, end_time),
            start_date__range=(start_date, end_date),
            end_date__range=(start_date, end_date),
            screen=attrs["screen"],
        )
        if show_detail:
            raise serializers.ValidationError(
                "Another show is ongoing in same time and same screen"
            )
        return attrs

    def save(self) -> dict:
        validated_data = self.validated_data.copy()
        screen = validated_data["screen"]
        available_seats = screen.total_seat
        show_prices = validated_data.pop("show_prices")

        # create show detail
        show_detail = ShowDetail.objects.create(
            **validated_data, available_seats=available_seats
        )

        # set show price for each type of seats
        for show_price in show_prices:
            ShowSeatPrice.objects.create(show_detail=show_detail, **show_price)

        # get start and end day from show detail
        show_start_date = show_detail.start_date
        show_end_date = show_detail.end_date

        # create booked show detail for each day
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
        fields = ["seats", "show_time", "show_date"]
        read_only_fields = ("id", "show_time")
