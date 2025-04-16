# Django imports
from django.urls import include, path

# External imports
from rest_framework.routers import SimpleRouter

# Local imports
# Local Imports
from .views import (
    BookingViewSet,
    MovieViewSet,
    ScreenViewSet,
    ShowDetailViewSet,
)

router = SimpleRouter()
router.register("screen", ScreenViewSet, basename="screen")
router.register("movie", MovieViewSet, basename="movie")
router.register("show/detail", ShowDetailViewSet, basename="show-detail")
router.register("booking", BookingViewSet, basename="book-detail")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "show/<int:show_id>/price/<int:show_price_id>/",
        ShowDetailViewSet.as_view({"put": "update_price"}),
        name="update-price",
    ),
    path("show/list/", ShowDetailViewSet.as_view({"get": "list"}), name="show-list"),
    path(
        "show/<int:pk>/detail/",
        ShowDetailViewSet.as_view({"get": "retrieve"}),
        name="show-detail",
    ),
    path(
        "show/detail/<int:show_id>/book/",
        BookingViewSet.as_view({"post": "booking"}),
        name="book-ticket",
    ),
]
