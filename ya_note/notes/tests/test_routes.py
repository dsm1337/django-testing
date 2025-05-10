from http import HTTPStatus

from django.conf import settings

from .conftest import (
    ADD_URL, BaseTestCase, get_edit_url, get_delete_url, get_detail_url,
    HOME_URL, LIST_URL, LOGIN_URL, SIGNUP_URL, SUCCESS_URL
)


class TestRoutes(BaseTestCase):

    def test_availability(self):
        urls_client_status = (
            (HOME_URL, self.client, HTTPStatus.OK),
            (LOGIN_URL, self.client, HTTPStatus.OK),
            (SIGNUP_URL, self.client, HTTPStatus.OK),
            (ADD_URL, self.author_client, HTTPStatus.OK),
            (LIST_URL, self.author_client, HTTPStatus.OK),
            (SUCCESS_URL, self.author_client, HTTPStatus.OK),
            (ADD_URL, self.author_client, HTTPStatus.OK),
            (get_edit_url(), self.author_client, HTTPStatus.OK),
            (get_delete_url(), self.author_client, HTTPStatus.OK),
            (get_detail_url(), self.author_client, HTTPStatus.OK),
            (get_edit_url(), self.reader_client, HTTPStatus.NOT_FOUND),
            (get_delete_url(), self.reader_client, HTTPStatus.NOT_FOUND),
            (get_detail_url(), self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for name, current_client, expected_status in urls_client_status:
            with self.subTest(name=name):
                self.assertEqual(
                    current_client.get(name).status_code,
                    expected_status
                )

    def test_anonymus_redirect(self):
        login_url = settings.LOGIN_URL
        urls = (ADD_URL, get_edit_url(), get_delete_url(), get_detail_url(),
                LIST_URL, SUCCESS_URL)
        for name in urls:
            with self.subTest(name=name):
                self.assertRedirects(
                    self.client.get(name), f'{login_url}?next={name}'
                )
