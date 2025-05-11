from http import HTTPStatus

from .conftest import (
    ADD_URL, BaseTestCase, EDIT_URL, DELETE_URL, DETAIL_URL,
    HOME_URL, LIST_URL, LOGIN_URL, SIGNUP_URL, SUCCESS_URL,
    REDIRECT_ADD_URL, REDIRECT_EDIT_URL, REDIRECT_DELETE_URL,
    REDIRECT_DETAIL_URL, REDIRECT_LIST_URL, REDIRECT_SUCCESS_URL
)


class TestRoutes(BaseTestCase):

    def test_availability(self):
        urls_client_status = (
            (HOME_URL, self.client, HTTPStatus.OK),
            (LOGIN_URL, self.client, HTTPStatus.OK),
            (SIGNUP_URL, self.client, HTTPStatus.OK),
            (ADD_URL, self.client, HTTPStatus.FOUND),
            (LIST_URL, self.client, HTTPStatus.FOUND),
            (SUCCESS_URL, self.client, HTTPStatus.FOUND),
            (EDIT_URL, self.client, HTTPStatus.FOUND),
            (DELETE_URL, self.client, HTTPStatus.FOUND),
            (DETAIL_URL, self.client, HTTPStatus.FOUND),
            (ADD_URL, self.author_client, HTTPStatus.OK),
            (LIST_URL, self.author_client, HTTPStatus.OK),
            (SUCCESS_URL, self.author_client, HTTPStatus.OK),
            (EDIT_URL, self.author_client, HTTPStatus.OK),
            (DELETE_URL, self.author_client, HTTPStatus.OK),
            (DETAIL_URL, self.author_client, HTTPStatus.OK),
            (EDIT_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (DELETE_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (DETAIL_URL, self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for name, current_client, expected_status in urls_client_status:
            with self.subTest(
                name=name, client=current_client, status=expected_status
            ):
                self.assertEqual(
                    current_client.get(name).status_code,
                    expected_status
                )

    def test_anonymus_redirect(self):
        urls_redirect = (
            (ADD_URL, REDIRECT_ADD_URL),
            (EDIT_URL, REDIRECT_EDIT_URL),
            (DELETE_URL, REDIRECT_DELETE_URL),
            (DETAIL_URL, REDIRECT_DETAIL_URL),
            (LIST_URL, REDIRECT_LIST_URL),
            (SUCCESS_URL, REDIRECT_SUCCESS_URL),
        )
        for url, redirect in urls_redirect:
            with self.subTest(name=url, redirect=redirect):
                self.assertRedirects(
                    self.client.get(url), redirect
                )
