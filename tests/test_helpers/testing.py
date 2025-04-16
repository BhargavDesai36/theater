# External imports
from rest_framework.test import APITestCase

# App imports
from user.models import UserTypes

# Local imports
from .logger import testing_logger as logger
from .model_factory import (
    new_booked_show_detail,
    new_movie,
    new_screen,
    new_screen_seat_types_mappings,
    new_seats,
    new_show_detail,
    new_show_seat_price,
    new_user,
)


class APIBaseTestCase(APITestCase):
    def setUp(self) -> None:
        self.database = None

    def seed_database(self, db: str):
        if self.database is not None:
            raise Exception(
                f"This will overwrite the member variables for db={self.database}"
            )

        self.database = db
        logger.info({"message": f"populating db={db} with seed data"})

        self.seed_users(db)
        self.seed_screens(db)
        self.seed_screen_seat_types(db)
        self.seed_seats(db)
        self.seed_movies(db)
        self.seed_show_details(db)
        self.seed_show_seat_prices(db)
        self.seed_booked_show_details(db)

    def seed_users(self, db: str) -> None:
        logger.info({"message": "populating test db with users"})
        self.owner, self.owner_token = new_user(
            database=db,
            email="owner@gmail.com",
            user_type=UserTypes.OWNER,
            password="owner",
            first_name="owner",
            last_name="owner",
        )

        self.manager, self.manager_token = new_user(
            database=db,
            email="manager@gmail.com",
            user_type=UserTypes.MANAGER,
            password="manager",
            first_name="manager",
            last_name="manager",
        )

        self.user, self.user_token = new_user(
            database=db,
            email="user@gmail.com",
            user_type=UserTypes.USER,
            password="user",
            first_name="user",
            last_name="user",
        )

    def seed_screens(self, db: str) -> None:
        logger.info({"message": "populating test db with screen"})
        self.screen = new_screen(database=db, screen_number=1, total_seat=75)

    def seed_screen_seat_types(self, db: str) -> None:
        logger.info({"message": "populating test db with screen seat types"})
        self.screen_seat_types = new_screen_seat_types_mappings(
            database=db, seat_type=["SILVER", "GOLD", "PLATINUM"], screen=self.screen
        )

    def seed_seats(self, db: str) -> None:
        logger.info({"message": "populating test db with seats"})
        self.seats = new_seats(
            database=db, rows=15, columns=5, types=self.screen_seat_types
        )

    def seed_movies(self, db: str) -> None:
        logger.info({"message": "populating test db with movies"})
        self.movie = new_movie(
            database=db,
            title="test movie",
            description="test movie",
            release_date="2030-12-01",
        )

    def seed_show_details(self, db: str) -> None:
        logger.info({"message": "populating test db with show details"})
        self.show_detail = new_show_detail(
            database=db,
            movie=self.movie,
            screen=self.screen,
            start_time="12:00",
            end_time="13:00",
            end_date="2030-12-01",
        )

    def seed_show_seat_prices(self, db: str) -> None:
        logger.info({"message": "populating test db with show seat prices"})
        self.show_seat_prices = new_show_seat_price(
            database=db,
            show_detail=self.show_detail,
            seat_types=self.screen_seat_types,
            prices=[120, 160, 200],
        )

    def seed_booked_show_details(self, db: str) -> None:
        logger.info({"message": "populating test db with booked show details"})
        self.booked_show_detail = new_booked_show_detail(
            database=db, show_detail=self.show_detail
        )
