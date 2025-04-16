# Python imports
from datetime import datetime, timedelta
from typing import List, Tuple

# External imports
from rest_framework.authtoken.models import Token

# App imports
from movie.models import (
    BookedShowDetail,
    Movie,
    Screen,
    ScreenSeatTypesMapping,
    Seat,
    SeatType,
    ShowDetail,
    ShowSeatPrice,
)
from user.models import User


def new_user(
    database: str,
    email: str,
    user_type: str,
    password: str,
    first_name: str,
    last_name: str,
) -> Tuple[User, Token]:
    user = User.objects.using(database).create(
        email=email,
        user_type=user_type,
        username=email,
        first_name=first_name,
        last_name=last_name,
    )
    user.set_password(password)
    user.save()

    # get token
    token, _ = Token.objects.get_or_create(user=user)

    return user, token


def new_screen(database: str, screen_number: int, total_seat: int) -> Screen:
    return Screen.objects.using(database).create(
        screen_number=screen_number, total_seat=total_seat
    )


def new_screen_seat_types_mappings(
    database: str, seat_type: List[str], screen: Screen
) -> List[ScreenSeatTypesMapping]:
    return ScreenSeatTypesMapping.objects.using(database).bulk_create(
        ScreenSeatTypesMapping(seat_type=seat_type, screen=screen)
        for seat_type in seat_type
    )


def new_seats(
    database: str, rows: int, columns: int, types: ScreenSeatTypesMapping
) -> List[Seat]:
    seats = []
    for row in range(rows):
        type = types[row // 5]
        for column in range(1, 1 + columns):
            seats.append(
                Seat(
                    raw=row + 1,
                    col=column,
                    seat_number=str(row + 1) + str(column),
                    type=type,
                )
            )
    return Seat.objects.using(database).bulk_create(seats)


def new_movie(database: str, title: str, description: str, release_date: str) -> Movie:
    return Movie.objects.using(database).create(
        title=title, description=description, release_date=release_date
    )


def new_show_detail(
    database: str,
    movie: Movie,
    screen: Screen,
    start_time: str,
    end_time: str,
    end_date: str,
) -> ShowDetail:
    return ShowDetail.objects.using(database).create(
        movie=movie,
        screen=screen,
        start_time=start_time,
        end_time=end_time,
        available_seats=screen.total_seat,
        start_date=movie.release_date,
        end_date=end_date,
    )


def new_show_seat_price(
    database: str,
    show_detail: ShowDetail,
    seat_types: List[SeatType],
    prices: List[float],
) -> List[ShowSeatPrice]:
    return ShowSeatPrice.objects.using(database).bulk_create(
        ShowSeatPrice(
            show_detail=show_detail, seat_type=seat_types[index], price=prices[index]
        )
        for index in range(len(seat_types))
    )


def new_booked_show_detail(
    database: str, show_detail: ShowDetail
) -> List[BookedShowDetail]:
    booked_show = []
    start_date = datetime.strptime(show_detail.start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(show_detail.end_date, "%Y-%m-%d").date()

    for day in range((end_date - start_date).days + 1):
        booked_show.append(
            BookedShowDetail(
                show_detail=show_detail,
                show_date=start_date + timedelta(days=day),
                available_seats=show_detail.available_seats,
            )
        )
    return BookedShowDetail.objects.using(database).bulk_create(booked_show)
