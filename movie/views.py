# Django imports
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

# External imports
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# App imports
from theater.permissions import AdminPermission

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
from .serializers import (
    AddScreenSerializer,
    BookingSerializer,
    MovieSerializer,
    ScreenSerializer,
    ShowDetailSerializer,
    UpdateShowSerializer,
)
from .utils import create_screen_with_seats, order_seat_types


class ScreenViewSet(viewsets.ModelViewSet):
    serializer_class = ScreenSerializer
    http_method_names = ["get", "post", "delete"]
    permission_classes = [AdminPermission]
    queryset = Screen.objects.all()

    def list(self, request) -> Response:
        queryset = Screen.objects.all().prefetch_related("seat_screen")
        serializer = ScreenSerializer(queryset, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def create(self, request) -> Response:
        serializer = AddScreenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        screen_number = serializer.validated_data["screen_number"]
        seat_types = serializer.validated_data["seat_types"]

        seat_types_ordered = order_seat_types(seat_types)
        screen = create_screen_with_seats(
            screen_number=screen_number, seat_types=seat_types_ordered
        )

        seats = ScreenSeatTypesMapping.objects.filter(screen=screen.id).values_list(
            "seat_type", flat=True
        )
        screen.seat_type = seats
        serializer = ScreenSerializer(screen)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = MovieSerializer
    http_method_names = ["get", "post", "put", "delete"]
    permission_classes = [AdminPermission]
    queryset = Movie.objects.all()


class ShowDetailViewSet(viewsets.ModelViewSet):
    serializer_class = ShowDetailSerializer
    http_method_names = ["get", "post", "put", "delete"]
    permission_classes = [AdminPermission]
    queryset = (
        ShowDetail.objects.all()
        .prefetch_related(
            Prefetch(
                "show_price_detail", ShowSeatPrice.objects.all(), to_attr="show_prices"
            ),
        )
        .prefetch_related(
            Prefetch(
                "booked_show_detail",
                BookedShowDetail.objects.all(),
                to_attr="booked_show",
            )
        )
    )

    @transaction.atomic
    def update(self, request, pk) -> Response:
        serializer = UpdateShowSerializer(data=request.data, instance=self.get_object())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def update_price(self, request, show_id: int, show_price_id: int) -> Response:
        show_price = get_object_or_404(
            ShowSeatPrice, id=show_price_id, show_detail_id=show_id
        )

        show_price.price = request.data.get("price", 0)
        show_price.save()
        return Response(
            {"message": "Price updated successfully", "price": show_price.price},
            status=status.HTTP_200_OK,
        )


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    http_method_names = ["get", "post", "delete"]
    permission_classes = [IsAuthenticated]
    queryset = Booking.objects.all()

    def list(self, request) -> Response:
        queryset = Booking.objects.filter(user=request.user.id).prefetch_related(
            "showtime"
        )
        serializer = BookingSerializer(queryset, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def booking(self, request, show_id: int) -> Response:
        user = request.user
        booked_show = get_object_or_404(BookedShowDetail, id=show_id)
        show_detail = booked_show.show_detail

        serializer = BookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get booked seat list
        booked_seats = (
            Booking.objects.filter(
                booked_show=booked_show,
                showtime=show_detail,
            )
            .values_list("seats", flat=True)
            .distinct()
        )

        # get booked seat
        seats = serializer.validated_data["seats"]
        seat_list = [seat.id for seat in seats]
        seat_check = Seat.objects.filter(id__in=seat_list).values_list("id", flat=True)

        # check if any seat is already booked
        if bool(set(seat_check).intersection(set(booked_seats))):
            return Response(
                {"message": "Seat is already booked"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total_seat = len(seats)
        show_date = booked_show.show_date

        # check if show date is valid
        if not show_date:
            return Response(
                {"message": "Show date is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # check if show date is valid
        if show_detail.start_date > show_date or show_detail.end_date < show_date:
            return Response(
                {"message": "Show date is invalid"}, status=status.HTTP_400_BAD_REQUEST
            )

        # check if seats are available
        if (
            show_detail.available_seats <= 0
            and total_seat > show_detail.available_seats
        ):
            return Response(
                {"message": "No seats available"}, status=status.HTTP_400_BAD_REQUEST
            )

        # check if show is available
        booked_show_check = BookedShowDetail.objects.filter(
            show_detail=show_detail, show_date=show_date
        )
        if not booked_show_check:
            return Response(
                {"message": "No show available"}, status=status.HTTP_400_BAD_REQUEST
            )

        booked_show.available_seats -= total_seat
        booked_show.save()

        # book a ticket for a user
        booked_ticket = Booking.objects.create(
            user=user,
            showtime=show_detail,
            booked_show=booked_show,
        )
        booked_ticket.seats.set(seats)
        booked_ticket.save()

        booking_data = BookingSerializer(booked_ticket).data
        return Response(booking_data, status=status.HTTP_201_CREATED)
