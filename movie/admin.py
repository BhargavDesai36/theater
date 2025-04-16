# Django imports
from django.contrib import admin

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

# Register your models here.

admin.site.register(Screen)
admin.site.register(ScreenSeatTypesMapping)
admin.site.register(Seat)
admin.site.register(Movie)
admin.site.register(ShowDetail)
admin.site.register(ShowSeatPrice)
admin.site.register(Booking)
admin.site.register(BookedShowDetail)
