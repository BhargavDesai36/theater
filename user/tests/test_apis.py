# External imports
from rest_framework import status
from rest_framework.reverse import reverse

# App imports
from tests.test_helpers.constants import DEFAULT_DATABASE
from tests.test_helpers.testing import APIBaseTestCase

# Local imports
from .logger import TestingLogger as Logger


class AuthAPITestCase(APIBaseTestCase):
    databases = [DEFAULT_DATABASE]

    def setUp(self) -> None:
        super().setUp()
        self.seed_database(DEFAULT_DATABASE)

    def test_user_signup(self) -> None:
        """
        testcase for user signup
        """

        response = self.client.post(
            "/api/v1/signup/",
            {
                "first_name": "test",
                "last_name": "test",
                "email": "test@gmail.com",
                "password": "test",
                "confirm_password": "test",
            },
        )
        Logger.info(
            {
                "message": "user signup",
                "response": response.content,
                "event": "test_user_signup",
            }
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_201_CREATED)
        self.assertEqual(response["first_name"], "test")
        self.assertEqual(response["last_name"], "test")
        self.assertEqual(response["email"], "test@gmail.com")
        # TODO(bhargav): add user type in the response
        # self.assertEqual(response["user_type"], "User")

    def test_user_login(self) -> None:
        """
        testcase for user login
        """
        response = self.client.post(
            reverse("login"),
            {
                "email": "user@gmail.com",
                "password": "user",
            },
        )
        Logger.info(
            {
                "message": "user login",
                "response": response.content,
                "event": "test_user_login",
            }
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_200_OK)
        self.assertEqual(response["data"]["email"], "user@gmail.com")
        self.assertEqual(response["data"]["first_name"], "user")
        self.assertEqual(response["data"]["last_name"], "user")

        # TODO(bhargav): add user type in the response
        # self.assertEqual(response["data"]["user_type"], "User")

    def test_reset_password(self) -> None:
        """
        testcase for user reset password
        """

        self.user.otp = 123
        self.otp_expiration = "2030-12-01 12:00:00"
        self.user.save()

        response = self.client.post(
            reverse("reset_password"),
            {
                "email": "user@gmail.com",
                "otp": 123,
                "password": "user_new",
                "confirm_password": "user_new",
            },
        )
        Logger.info(
            {
                "message": "reset password",
                "response": response.content,
                "event": "test_reset_password",
            }
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_200_OK)
        self.assertEqual(response["message"], "password reset")

        # check password reset properly
        response = self.client.post(
            reverse("login"),
            {
                "email": "user@gmail.com",
                "password": "user_new",
            },
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_200_OK)
        self.assertEqual(response["data"]["email"], "user@gmail.com")

    def test_reset_password_invalid_otp(self) -> None:
        """
        testcase for user reset password with invalid otp
        """

        response = self.client.post(
            reverse("reset_password"),
            {
                "email": "user@gmail.com",
                "otp": 123,
                "password": "user_new",
                "confirm_password": "user_new",
            },
        )
        Logger.info(
            {
                "message": "reset password with invalid otp",
                "response": response.content,
                "event": "test_reset_password_invalid_otp",
            }
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response["error"], "invalid or expired OTP")

    def test_reset_password_invalid_email(self) -> None:
        """
        testcase for user reset password with invalid email
        """

        response = self.client.post(
            reverse("reset_password"),
            {
                "email": "invalid@gmail.com",
                "otp": 123,
                "password": "user_new",
                "confirm_password": "user_new",
            },
        )
        Logger.info(
            {
                "message": "reset password with invalid email",
                "response": response.content,
                "event": "test_reset_password_invalid_email",
            }
        )
        response, status_code = response.json(), response.status_code

        self.assertEqual(status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response["detail"], "Not found.")
