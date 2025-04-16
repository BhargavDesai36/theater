# Python imports
from typing import Any, Dict

# Django imports
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView

# External imports
from rest_framework import filters, status, viewsets
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
from .utils import (
    StandardResultsSetPagination,
    calculate_total_price,
    create_screen_with_seats,
    get_show_seat_layout,
    order_seat_types,
    validate_booking_request,
)


class ScreenViewSet(viewsets.ModelViewSet):
    serializer_class = ScreenSerializer
    http_method_names = ["get", "post", "delete"]
    permission_classes = [AdminPermission]
    queryset = Screen.objects.all()

    def get_queryset(self):
        return Screen.objects.all().prefetch_related("seat_screen")

    def list(self, request) -> Response:
        queryset = self.get_queryset()
        serializer = ScreenSerializer(queryset, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def create(self, request) -> Response:
        serializer = AddScreenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        screen_number = validated_data["screen_number"]
        seat_types = validated_data["seat_types"]

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
    pagination_class = StandardResultsSetPagination


class ShowDetailViewSet(viewsets.ModelViewSet):
    serializer_class = ShowDetailSerializer
    http_method_names = ["get", "post", "put", "delete"]
    permission_classes = [AdminPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["movie__title", "screen__screen_number"]
    ordering_fields = ["start_date", "start_time"]

    def get_queryset(self):
        """
        Get the list of show details with related data prefetched.

        Returns:
            QuerySet: Filtered and annotated show details
        """
        return (
            ShowDetail.objects.all()
            .prefetch_related(
                Prefetch(
                    "show_price_detail",
                    ShowSeatPrice.objects.all(),
                    to_attr="show_prices",
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
    def update(self, request, pk: int) -> Response:
        """
        Update a show detail.

        Args:
            request: The HTTP request
            pk (int): The primary key of the show detail

        Returns:
            Response: Updated show detail data

        Raises:
            ValidationError: If the data is invalid
        """
        try:
            instance = self.get_object()
            serializer = UpdateShowSerializer(data=request.data, instance=instance)
            serializer.is_valid(raise_exception=True)
            updated_show = serializer.save()
            return Response(ShowDetailSerializer(updated_show).data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update_price(self, request, show_id: int, show_price_id: int) -> Response:
        show_price = get_object_or_404(
            ShowSeatPrice, id=show_price_id, show_detail_id=show_id
        )

        price = float(request.data.get("price", 0))
        show_price.price = price
        show_price.save()
        return Response(
            {"message": "Price updated successfully", "price": price},
            status=status.HTTP_200_OK,
        )


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    http_method_names = ["get", "post", "delete"]
    permission_classes = [IsAuthenticated]
    queryset = Booking.objects.all()
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Booking.objects.all()

    def list(self, request) -> Response:
        queryset = (
            self.get_queryset()
            .filter(user=request.user.id)
            .prefetch_related("showtime")
        )

        serializer = BookingSerializer(queryset, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def booking(self, request: Request, show_id: int) -> Response:
        user = request.user
        show_detail = get_object_or_404(ShowDetail, id=show_id)

        serializer = BookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        seats = serializer.validated_data["seats"]
        show_date = serializer.validated_data["show_date"]

        validate_booking_request(seats, show_detail, show_date)

        total_price = calculate_total_price(seats, show_id)

        booking = Booking.objects.create(
            user=user, showtime=show_detail, total_amount=total_price
        )
        booking.seats.set(seats)

        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)


# Template Views
class HomeView(TemplateView):
    template_name = "movie/home.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        context["now_showing"] = Movie.objects.filter(
            showdetail__start_date__lte=today, showdetail__end_date__gte=today
        ).distinct()
        context["coming_soon"] = Movie.objects.filter(release_date__gt=today).order_by(
            "release_date"
        )[:5]
        return context


class MovieListView(ListView):
    model = Movie
    template_name = "movie/movie_list.html"
    context_object_name = "movies"
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(title__icontains=search)
        return queryset


class MovieDetailView(DetailView):
    model = Movie
    template_name = "movie/movie_detail.html"
    context_object_name = "movie"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        context["show_details"] = ShowDetail.objects.filter(
            movie=self.object, start_date__lte=today, end_date__gte=today
        ).select_related("screen")
        return context


@login_required
def select_seats(request, show_id):
    show = get_object_or_404(ShowDetail, id=show_id)
    seat_layout = get_show_seat_layout(show.screen.id)
    booked_seats = Booking.objects.filter(showtime=show).values_list(
        "seats__id", flat=True
    )

    return render(
        request,
        "movie/select_seats.html",
        {"show": show, "seat_layout": seat_layout, "booked_seats": booked_seats},
    )


@login_required
def book_seats(request, show_id):
    if request.method != "POST":
        return redirect("movie:movie_list")

    show = get_object_or_404(ShowDetail, id=show_id)
    selected_seats = request.POST.get("selected_seats", "").split(",")

    try:
        validate_booking_request(selected_seats, show, timezone.now().date())
        total_price = calculate_total_price(selected_seats, show_id)

        booking = Booking.objects.create(
            user=request.user, showtime=show, total_amount=total_price
        )
        booking.seats.set(selected_seats)

        messages.success(request, "Booking confirmed successfully!")
        return redirect("movie:booking_detail", booking.id)
    except Exception as e:
        messages.error(request, str(e))
        return redirect("movie:select_seats", show_id)


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "movie/booking_list.html"
    context_object_name = "bookings"
    paginate_by = 10

    def get_queryset(self):
        return (
            Booking.objects.filter(user=self.request.user)
            .select_related("showtime__movie", "showtime__screen")
            .prefetch_related("seats")
        )


class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "admin/dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect("movie:home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        context.update(
            {
                "total_movies": Movie.objects.count(),
                "active_shows": ShowDetail.objects.filter(
                    start_date__lte=today, end_date__gte=today
                ).count(),
                "total_screens": Screen.objects.count(),
                "todays_bookings": Booking.objects.filter(
                    created_at__date=today
                ).count(),
                "recent_movies": Movie.objects.order_by("-created_at")[:5],
                "recent_bookings": Booking.objects.select_related(
                    "user", "showtime__movie"
                ).order_by("-created_at")[:5],
            }
        )
        return context
