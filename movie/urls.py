# Django imports
from django.urls import include, path

# External imports
from rest_framework.routers import DefaultRouter

# Local Imports
from .views import (
    AdminDashboardView,
    BookingDetailView,
    BookingListView,
    BookingViewSet,
    HomeView,
    MovieDetailView,
    MovieListView,
    MovieViewSet,
    ShowDetailViewSet,
    book_seats,
    select_seats,
)

app_name = "movie"

# API Router
router = DefaultRouter()
router.register(r"movies", MovieViewSet)
router.register(r"shows", ShowDetailViewSet)
router.register(r"bookings", BookingViewSet)

urlpatterns = [
    # API URLs
    path("api/", include(router.urls)),
    # Template URLs
    path("", HomeView.as_view(), name="home"),
    path("movies/", MovieListView.as_view(), name="movie_list"),
    path("movie/<uuid:pk>/", MovieDetailView.as_view(), name="movie_detail"),
    path("show/<int:show_id>/select-seats/", select_seats, name="select_seats"),
    path("show/<int:show_id>/book/", book_seats, name="book_seats"),
    path("bookings/", BookingListView.as_view(), name="booking_list"),
    path("booking/<int:pk>/", BookingDetailView.as_view(), name="booking_detail"),
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin_dashboard"),
]
