# Django imports
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Local imports
from .models import User


class UserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("User Types", {"fields": ("user_type",)}),
        ("Reset Password", {"fields": ("otp", "otp_expiration")}),
    )


admin.site.register(User, UserAdmin)
