# Python imports
from typing import List

# App imports
from movie.models import Screen, ScreenSeatTypesMapping, Seat


def create_screen_with_seats(screen_number, seat_types: List[dict]) -> Screen:
    screen = Screen.objects.create(screen_number=screen_number)
    raws = 1
    total_seat = 0
    for seat_type in seat_types:
        screen_seat = ScreenSeatTypesMapping.objects.create(
            screen=screen, seat_type=seat_type["seat_type"]
        )

        type_raw = seat_type["rows"] + raws
        type_col = seat_type["columns"]
        for i in range(raws, type_raw):
            for j in range(type_col):
                Seat.objects.create(
                    seat_number=(str(i) + str(j)),
                    raw=raws + i,
                    col=j + 1,
                    type=screen_seat,
                )
        raws = type_raw
        total_seat += seat_type["rows"] * seat_type["columns"]

    screen.total_seat = total_seat
    screen.save()

    return screen


def order_seat_types(seat_types: List[dict]) -> List[dict]:
    seat_types_ordered = [{}] * len(seat_types)
    for seat_type in seat_types:
        seat_types_ordered[seat_type["order"] - 1] = seat_type
    return seat_types_ordered
