# Python imports
from datetime import date, time
from typing import List, TypedDict

# Django imports
# External imports


class SeatTypeDict(TypedDict):
    seat_type: str
    rows: int
    columns: int
    order: int


class ShowPriceDict(TypedDict):
    price: float
    seat_type: str


class BookingRequestDict(TypedDict):
    seats: List[int]
    show_date: date


class ShowDetailDict(TypedDict):
    movie_id: str
    screen_id: int
    start_time: time
    end_time: time
    start_date: date
    end_date: date
    available_seats: int
    prices: List[ShowPriceDict]
