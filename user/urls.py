# Django imports
from django.urls import include, path

# External imports
from rest_framework.routers import SimpleRouter

# Local imports
# Local Imports
from .views import SigninViewSet, SignupViewSet

router = SimpleRouter()
router.register("signup", SignupViewSet, basename="signup")

urlpatterns = [
    path("", include(router.urls)),
    path("login/", SigninViewSet.as_view({"post": "login"}), name="login"),
    path(
        "reset/password/",
        SigninViewSet.as_view({"post": "reset_password"}),
        name="reset_password",
    ),
    path(
        "reset/request/",
        SigninViewSet.as_view({"post": "reset_request"}),
        name="reset_request",
    ),
]
