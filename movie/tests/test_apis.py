# External imports
from rest_framework import status

# App imports
from movie.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from movie.utils import StandardResultsSetPagination
from tests.test_helpers.constants import DEFAULT_DATABASE
from tests.test_helpers.testing import APIBaseTestCase

# Local imports
from .logger import TestingLogger as Logger


class ScreenAPITestCase(APIBaseTestCase):
    databases = [DEFAULT_DATABASE]

    def setUp(self) -> None:
        super().setUp()
        self.seed_database(DEFAULT_DATABASE)

    def test_create_screen_as_owner(self) -> None:
        """
        testcase for the adding screen.
        """

        # call create screen API
        headers = {"Authorization": f"Token {self.owner_token}"}
        response = self.client.post(
            "/api/v1/screen/",
            data={
                "screen_number": 2,
                "seat_types": [
                    {"seat_type": "PLATINUM", "rows": "5", "columns": "5", "order": 1},
                    {"seat_type": "GOLD", "rows": "5", "columns": "5", "order": 2},
                    {"seat_type": "SILVER", "rows": "5", "columns": "5", "order": 3},
                ],
            },
            headers=headers,
            format="json",
        )
        Logger.info(
            {
                "message": "create screen as owner",
                "response": response.content,
                "event": "test_create_screen_as_owner",
            }
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_201_CREATED)
        self.assertEqual(response["screen_number"], 2)
        self.assertEqual(response["total_seat"], 75)
        self.assertEqual(len(response["seat_type"]), 3)

        self.screen_id = response["id"]

    def test_create_screen_as_user_type(self) -> None:
        """
        testcase for the adding screen as user type.
        """
        # call create screen API
        headers = {"Authorization": f"Token {self.user_token}"}
        response = self.client.post(
            "/api/v1/screen/",
            {
                "screen_number": 2,
                "seat_types": [
                    {"seat_type": "PLATINUM", "rows": "5", "columns": "5", "order": 1}
                ],
            },
            headers=headers,
        )
        Logger.info(
            {
                "message": "create screen as user",
                "response": response.content,
                "event": "test_create_screen_as_user_type",
            }
        )
        status_code = response.status_code

        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )

    def test_list_screen_as_owner(self) -> None:
        """
        testcase for the list of screen.
        """
        headers = {"Authorization": f"Token {self.owner_token}"}
        # test get screen list API
        response = self.client.get("/api/v1/screen/", headers=headers)
        Logger.info(
            {
                "message": "get list of screen by owner",
                "response": response.content,
                "event": "test_list_screen_as_owner",
            }
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_200_OK)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]["screen_number"], 1)
        self.assertEqual(response[0]["total_seat"], 75)

    def test_list_screen_as_user_type(self) -> None:
        """
        testcase for the list of screen as user type.
        """
        headers = {"Authorization": f"Token {self.user_token}"}
        # test get screen list API
        response = self.client.get("/api/v1/screen/", headers=headers)
        Logger.info(
            {
                "message": "get list of screen by user",
                "response": response.content,
                "event": "test_list_screen_as_user_type",
            }
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_200_OK)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]["screen_number"], 1)
        self.assertEqual(response[0]["total_seat"], 75)

    def test_delete_screen_as_owner(self) -> None:
        """
        testcase for the delete screen.
        """
        self.test_create_screen_as_owner()
        headers = {"Authorization": f"Token {self.owner_token}"}
        response = self.client.delete(
            f"/api/v1/screen/{self.screen_id}/", headers=headers
        )
        Logger.info(
            {
                "message": "delete screen by owner",
                "response": response.content,
                "event": "test_delete_screen_as_owner",
            }
        )
        status_code = response.status_code

        self.assertEqual(status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_screen_as_user_type(self) -> None:
        """
        testcase for the delete screen as user type.
        """
        self.test_create_screen_as_owner()
        headers = {"Authorization": f"Token {self.user_token}"}
        response = self.client.delete(
            f"/api/v1/screen/{self.screen_id}/", headers=headers
        )
        Logger.info(
            {
                "message": "delete screen by user",
                "response": response.content,
                "event": "test_delete_screen_as_user_type",
            }
        )
        status_code = response.status_code

        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )


class MovieAPITestCase(APIBaseTestCase):
    databases = [DEFAULT_DATABASE]

    def setUp(self) -> None:
        super().setUp()
        self.seed_database(DEFAULT_DATABASE)

    def test_create_movie_as_owner(self) -> None:
        """
        testcase for the create of movie.
        """

        headers = {"Authorization": f"Token {self.owner_token}"}
        response = self.client.post(
            "/api/v1/movie/",
            {
                "title": "test movie",
                "description": "test movie",
                "release_date": "2020-01-01",
            },
            headers=headers,
        )
        Logger.info(
            {
                "message": "create movie by owner",
                "response": response.content,
                "event": "test_create_movie_as_owner",
            }
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_201_CREATED)
        self.assertEqual(response["title"], "test movie")
        self.assertEqual(response["description"], "test movie")
        self.assertEqual(response["release_date"], "2020-01-01")

        self.movie_id = response["id"]

    def test_create_movie_as_user_type(self) -> None:
        """
        testcase for the create of movie as user type.
        """
        headers = {"Authorization": f"Token {self.user_token}"}
        response = self.client.post(
            "/api/v1/movie/",
            {
                "title": "test movie",
                "description": "test movie",
                "release_date": "2020-01-01",
            },
            headers=headers,
        )
        Logger.info(
            {
                "message": "create movie by user",
                "response": response.content,
                "event": "test_create_movie_as_user_type",
            }
        )
        status_code = response.status_code

        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )

    def test_list_movie_as_owner(self) -> None:
        """
        testcase for the list of movie.
        """
        headers = {"Authorization": f"Token {self.owner_token}"}
        # test get movie list API
        response = self.client.get("/api/v1/movie/", headers=headers)
        Logger.info(
            {
                "message": "get list of movie by owner",
                "response": response.content,
                "event": "test_list_movie_as_owner",
            }
        )
        data, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)

    def test_list_movie_as_user_type(self) -> None:
        """
        testcase for the list of movie as user type.
        """
        headers = {"Authorization": f"Token {self.user_token}"}
        # test get movie list API
        response = self.client.get("/api/v1/movie/", headers=headers)
        Logger.info(
            {
                "message": "get list of movie by user",
                "response": response.content,
                "event": "test_list_movie_as_user_type",
            }
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_200_OK)
        self.assertEqual(len(response), 1)

    def test_update_movie_as_owner(self) -> None:
        """
        testcase for the update of movie.
        """
        headers = {"Authorization": f"Token {self.owner_token}"}
        response = self.client.put(
            f"/api/v1/movie/{self.movie.id}/",
            {
                "title": "updated movie",
                "description": "updated description",
                "release_date": "2020-01-01",
            },
            headers=headers,
        )
        Logger.info(
            {
                "message": "update movie by owner",
                "response": response.content,
                "event": "test_update_movie_as_owner",
            }
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_200_OK)
        self.assertEqual(response["title"], "updated movie")
        self.assertEqual(response["description"], "updated description")
        self.assertEqual(response["release_date"], "2020-01-01")
        self.assertEqual(response["id"], str(self.movie.id))

    def test_update_movie_as_user_type(self) -> None:
        """
        testcase for the update of movie as user type.
        """
        headers = {"Authorization": f"Token {self.user_token}"}
        response = self.client.put(
            f"/api/v1/movie/{self.movie.id}/",
            {
                "title": "updated movie",
                "description": "updated description",
                "release_date": "2020-01-01",
            },
            headers=headers,
        )
        Logger.info(
            {
                "message": "update movie by user",
                "response": response.content,
                "event": "test_update_movie_as_user_type",
            }
        )
        status_code = response.status_code

        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )

    def test_delete_movie_as_owner(self) -> None:
        """
        testcase for the delete of movie.
        """
        self.test_create_movie_as_owner()
        headers = {"Authorization": f"Token {self.owner_token}"}
        response = self.client.delete(
            f"/api/v1/movie/{self.movie_id}/", headers=headers
        )
        Logger.info(
            {
                "message": "delete movie by owner",
                "response": response.content,
                "event": "test_delete_movie_as_owner",
            }
        )
        status_code = response.status_code

        self.assertEqual(status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_movie_as_user_type(self) -> None:
        """
        testcase for the delete of movie as user type.
        """
        self.test_create_movie_as_owner()
        headers = {"Authorization": f"Token {self.user_token}"}
        response = self.client.delete(
            f"/api/v1/movie/{self.movie_id}/", headers=headers
        )
        Logger.info(
            {
                "message": "delete movie by user",
                "response": response.content,
                "event": "test_delete_movie_as_user_type",
            }
        )
        status_code = response.status_code

        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )


class ScreenSeatTypeAPITestCase(APIBaseTestCase):
    databases = [DEFAULT_DATABASE]

    def setUp(self) -> None:
        super().setUp()
        self.seed_database(DEFAULT_DATABASE)

    def test_create_screen_seat_type_as_owner(self) -> None:
        """
        testcase for the create of screen seat type.
        """
        headers = {"Authorization": f"Token {self.owner_token}"}
        response = self.client.post(
            "/api/v1/show/detail/",
            data={
                "movie": self.movie.id,
                "start_time": "09:00",
                "end_time": "12:00",
                "screen": self.screen.id,
                "start_date": "2030-12-01",
                "end_date": "2030-12-31",
                "show_prices": [
                    {"seat_type": self.screen_seat_types[2].id, "price": 200},
                    {"seat_type": self.screen_seat_types[1].id, "price": 150},
                    {"seat_type": self.screen_seat_types[0].id, "price": 120},
                ],
            },
            headers=headers,
            format="json",
        )
        Logger.info(
            {
                "message": "create screen_seat_type as owner ",
                "response": response.content,
                "event": "test_create_screen_seat_type_as_owner",
            }
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_201_CREATED)
        self.assertEqual(response["movie"], str(self.movie.id))
        self.assertEqual(response["start_time"], "09:00:00")
        self.assertEqual(response["end_time"], "12:00:00")
        self.assertEqual(response["screen"], self.screen.id)
        self.assertEqual(response["start_date"], "2030-12-01")
        self.assertEqual(response["end_date"], "2030-12-31")
        self.assertEqual(len(response["show_prices"]), 3)

    def test_create_screen_seat_type_as_user_type(self) -> None:
        """
        testcase for the create of screen seat type as user type.
        """
        headers = {"Authorization": f"Token {self.user_token}"}
        response = self.client.post(
            "/api/v1/show/detail/",
            {
                "movie": self.movie.id,
                "start_time": "09:00",
                "end_time": "12:00",
                "screen": self.screen.id,
                "start_date": "2030-12-01",
                "end_date": "2030-12-31",
                "show_prices": [
                    {"seat_type": self.screen_seat_types[2].id, "price": 200}
                ],
            },
            headers=headers,
        )
        Logger.info(
            {
                "message": "create screen_seat_type as user ",
                "response": response.content,
                "event": "test_create_screen_seat_type_as_user_type",
            }
        )
        status_code = response.status_code

        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )

    def test_list_show_as_owner(self) -> None:
        """
        testcase for the list of show.
        """
        headers = {"Authorization": f"Token {self.owner_token}"}
        # test get show list API
        response = self.client.get("/api/v1/show/list/", headers=headers)
        Logger.info(
            {
                "message": "get list of show as owner ",
                "response": response.content,
                "event": "test_list_show_as_owner",
            }
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_200_OK)

    def test_list_show_as_user_type(self) -> None:
        """
        testcase for the list of show as user type.
        """
        headers = {"Authorization": f"Token {self.user_token}"}
        # test get show list API
        response = self.client.get("/api/v1/show/list/", headers=headers)
        Logger.info(
            {
                "message": "get list of show as user ",
                "response": response.content,
                "event": "test_list_show_as_user_type",
            }
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_200_OK)

    def test_update_show_seat_price_as_owner(self) -> None:
        """
        testcase for the update of show seat price.
        """
        headers = {"Authorization": f"Token {self.owner_token}"}
        response = self.client.put(
            f"/api/v1/show/{self.show_detail.id}/price/{self.show_seat_prices[0].id}/",
            {"price": 220},
            headers=headers,
        )
        Logger.info(
            {
                "message": "update show seat_price as owner ",
                "response": response.content,
                "event": "test_update_show_seat_price_as_owner",
            }
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_200_OK)
        self.assertEqual(response["message"], "Price updated successfully")
        self.assertEqual(int(response["price"]), 220)

    def test_update_show_seat_price_as_user_type(self) -> None:
        """
        testcase for the update of show seat price as user type.
        """
        headers = {"Authorization": f"Token {self.user_token}"}
        response = self.client.put(
            f"/api/v1/show/{self.show_detail.id}/price/{self.show_seat_prices[0].id}/",
            {"price": 220},
            headers=headers,
        )
        Logger.info(
            {
                "message": "update show seat_price as user ",
                "response": response.content,
                "event": "test_update_show_seat_price_as_user_type",
            }
        )
        status_code = response.status_code

        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )

    def test_update_show_detail_as_owner(self) -> None:
        """
        testcase for the update of show detail.
        """
        headers = {"Authorization": f"Token {self.owner_token}"}
        response = self.client.put(
            f"/api/v1/show/detail/{self.show_detail.id}/",
            {
                "movie": self.movie.id,
                "start_time": "09:00",
                "end_time": "12:00",
                "screen": self.screen.id,
                "start_date": "2031-12-01",
                "end_date": "2031-12-31",
            },
            headers=headers,
        )
        Logger.info(
            {
                "message": "update show_detail as owner ",
                "response": response.content,
                "event": "test_update_show_detail_as_owner",
            }
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_200_OK)
        self.assertEqual(response["movie"], str(self.movie.id))
        self.assertEqual(response["start_time"], "09:00:00")
        self.assertEqual(response["end_time"], "12:00:00")
        self.assertEqual(response["screen"], self.screen.id)
        self.assertEqual(response["start_date"], "2031-12-01")
        self.assertEqual(response["end_date"], "2031-12-31")

    def test_update_show_detail_as_user_type(self) -> None:
        """
        testcase for the update of show detail as user type.
        """
        headers = {"Authorization": f"Token {self.user_token}"}
        response = self.client.put(
            f"/api/v1/show/detail/{self.show_detail.id}/",
            {
                "movie": self.movie.id,
                "start_time": "09:00",
                "end_time": "12:00",
                "screen": self.screen.id,
                "start_date": "2031-12-01",
                "end_date": "2031-12-31",
            },
            headers=headers,
        )
        Logger.info(
            {
                "message": "update show_detail as user ",
                "response": response.content,
                "event": "test_update_show_detail_as_user_type",
            }
        )
        status_code = response.status_code

        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )

    def test_delete_show_as_owner(self) -> None:
        """
        testcase for the delete of show.
        """
        self.test_create_screen_seat_type_as_owner()
        headers = {"Authorization": f"Token {self.owner_token}"}
        response = self.client.delete(
            f"/api/v1/show/detail/{self.show_detail.id}/", headers=headers
        )
        Logger.info(
            {
                "message": "delete show as owner ",
                "response": response.content,
                "event": "test_delete_show_as_owner",
            }
        )
        status_code = response.status_code

        self.assertEqual(status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_show_as_user_type(self) -> None:
        """
        testcase for the delete of show as user type.
        """
        self.test_create_screen_seat_type_as_owner()
        headers = {"Authorization": f"Token {self.user_token}"}
        response = self.client.delete(
            f"/api/v1/show/detail/{self.show_detail.id}/", headers=headers
        )
        Logger.info(
            {
                "message": "delete show as user ",
                "response": response.content,
                "event": "test_delete_show_as_user_type",
            }
        )
        status_code = response.status_code

        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )


class BookTicketAPITestCase(APIBaseTestCase):
    databases = [DEFAULT_DATABASE]

    def setUp(self) -> None:
        super().setUp()
        self.seed_database(DEFAULT_DATABASE)

    def test_create_book_ticket_as_owner(self) -> None:
        """
        testcase for the create of book ticket.
        """
        headers = {"Authorization": f"Token {self.owner_token}"}
        response = self.client.post(
            f"/api/v1/show/detail/{self.show_detail.id}/book/",
            {"seats": [self.seats[0].id, self.seats[1].id]},
            headers=headers,
        )
        Logger.info(
            {
                "message": "create book_ticket as owner ",
                "response": response.content,
                "event": "test_create_book_ticket_as_owner",
            }
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response["seats"]), 2)

    def test_create_book_ticket_as_user_type(self) -> None:
        """
        testcase for the create of book ticket as user type.
        """
        headers = {"Authorization": f"Token {self.user_token}"}
        response = self.client.post(
            f"/api/v1/show/detail/{self.show_detail.id}/book/",
            {"seats": [self.seats[0].id, self.seats[1].id]},
            headers=headers,
        )
        Logger.info(
            {
                "message": "create book_ticket as user ",
                "response": response.content,
                "event": "test_create_book_ticket_as_user_type",
            }
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response["seats"]), 2)

    def test_list_booked_ticket_as_owner(self) -> None:
        """
        testcase for the list of booked ticket.
        """
        headers = {"Authorization": f"Token {self.owner_token}"}
        # test get booked ticket list API
        response = self.client.get("/api/v1/booking/", headers=headers)
        Logger.info(
            {
                "message": "get list of booked ticket as owner",
                "response": response.content,
                "event": "test_list_booked_ticket_as_owner",
            }
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_200_OK)

    def test_list_booked_ticket_as_user_type(self) -> None:
        """
        testcase for the list of booked ticket as user type.
        """
        headers = {"Authorization": f"Token {self.user_token}"}
        # test get booked ticket list API
        response = self.client.get("/api/v1/booking/", headers=headers)
        Logger.info(
            {
                "message": "get list of booked ticket as user",
                "response": response.content,
                "event": "test_list_booked_ticket_as_user_type",
            }
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_200_OK)


class PaginationTestCase(APIBaseTestCase):
    databases = [DEFAULT_DATABASE]

    def setUp(self) -> None:
        super().setUp()
        self.seed_database(DEFAULT_DATABASE)
        self.pagination = StandardResultsSetPagination()

    def test_pagination_default_size(self) -> None:
        """Test default pagination size."""
        headers = {"Authorization": f"Token {self.owner_token}"}

        for i in range(DEFAULT_PAGE_SIZE + 5):
            self.client.post(
                "/api/v1/movie/",
                {
                    "title": f"test movie {i}",
                    "description": f"test movie {i}",
                    "release_date": "2020-01-01",
                },
                headers=headers,
            )

        response = self.client.get("/api/v1/movie/", headers=headers)
        Logger.info(
            {
                "message": "get paginated movie list",
                "response": response.content,
                "event": "test_pagination_default_size",
            }
        )

        data = response.json()
        self.assertEqual(len(data["results"]), DEFAULT_PAGE_SIZE)
        self.assertEqual(data["current_page"], 1)
        self.assertTrue(data["total_items"] > DEFAULT_PAGE_SIZE)

    def test_pagination_custom_size(self) -> None:
        """Test custom page size."""
        headers = {"Authorization": f"Token {self.owner_token}"}
        custom_size = 5

        for i in range(custom_size + 3):
            self.client.post(
                "/api/v1/movie/",
                {
                    "title": f"test movie {i}",
                    "description": f"test movie {i}",
                    "release_date": "2020-01-01",
                },
                headers=headers,
            )

        response = self.client.get(
            f"/api/v1/movie/?page_size={custom_size}", headers=headers
        )
        Logger.info(
            {
                "message": "get paginated movie list with custom size",
                "response": response.content,
                "event": "test_pagination_custom_size",
            }
        )

        data = response.json()
        self.assertEqual(len(data["results"]), custom_size)
        self.assertEqual(data["page_size"], custom_size)

    def test_pagination_max_size_limit(self) -> None:
        """Test pagination max size limit."""
        headers = {"Authorization": f"Token {self.owner_token}"}
        over_max_size = MAX_PAGE_SIZE + 10

        for i in range(over_max_size):
            self.client.post(
                "/api/v1/movie/",
                {
                    "title": f"test movie {i}",
                    "description": f"test movie {i}",
                    "release_date": "2020-01-01",
                },
                headers=headers,
            )

        response = self.client.get(
            f"/api/v1/movie/?page_size={over_max_size}", headers=headers
        )
        Logger.info(
            {
                "message": "get paginated movie list with over max size",
                "response": response.content,
                "event": "test_pagination_max_size_limit",
            }
        )

        data = response.json()
        self.assertEqual(len(data["results"]), MAX_PAGE_SIZE)
        self.assertEqual(data["page_size"], MAX_PAGE_SIZE)
