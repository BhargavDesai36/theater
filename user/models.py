# Django imports
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeLogMixin(models.Model):
    """
    TimeLogMixin: it is abstract model which adds basic fields on every model.

    Fields:
        is_active (boolean): It defines the model data is active or not.
        modified_at (datetime): It defines the model data modified at.
        created_at (datetime): It defines the model data created at.
    """

    is_active = models.BooleanField(default=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class UserTypes(models.TextChoices):
    OWNER = "OWNER", _("Owner")
    MANAGER = "MANAGER", _("Manager")
    USER = "USER", _("User")

    UNKNOWN = "UNKNOWN", _("Unknown")


class User(AbstractUser, TimeLogMixin):
    """
    User: it is the custom user model using the Django's built-in auth app.

    Fields:
        user_type (UserTypes): It defines the user type.
        email (string): Email field of Django's built-in auth app.
        otp (string): OTP field of Django's built-in auth app.
        otp_expiration (datetime): OTP expiration field of Django's built-in auth app.
    """

    user_type = models.CharField(
        max_length=10, choices=UserTypes.choices, default=UserTypes.USER
    )
    email = models.EmailField(_("email address"), unique=True, db_index=True)

    # Reset password
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiration = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (
            "email",
            "username",
        )

    def __str__(self) -> str:
        return self.email
