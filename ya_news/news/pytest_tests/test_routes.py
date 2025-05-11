from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


HOME_URL = pytest.lazy_fixture('home_url')
DETAIL_URL = pytest.lazy_fixture('detail_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
DELETE_URL = pytest.lazy_fixture('delete_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')
REDIRECT_EDIT_URL = pytest.lazy_fixture('redirect_edit_url')
REDIRECT_DELETE_URL = pytest.lazy_fixture('redirect_delete_url')


CLIENT = pytest.lazy_fixture('client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name, parametrized_client, expected_response',
    (
        (HOME_URL, CLIENT, HTTPStatus.OK),
        (DETAIL_URL, CLIENT, HTTPStatus.OK),
        (LOGIN_URL, CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, CLIENT, HTTPStatus.OK),
        (DELETE_URL, CLIENT, HTTPStatus.FOUND),
        (EDIT_URL, CLIENT, HTTPStatus.FOUND),
        (EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (EDIT_URL, NOT_AUTHOR_CLIENT,
         HTTPStatus.NOT_FOUND),
        (DELETE_URL, NOT_AUTHOR_CLIENT,
         HTTPStatus.NOT_FOUND),
        (DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
    )
)
def test_pages_availability(name, parametrized_client, expected_response):
    assert (
        parametrized_client.get(name).status_code == expected_response
    )


@pytest.mark.parametrize(
    ('name', 'redirect'),
    (
        (EDIT_URL, REDIRECT_EDIT_URL),
        (DELETE_URL, REDIRECT_DELETE_URL)
    )
)
def test_redirect_for_anonymous_client(name, client, redirect):
    assertRedirects(client.get(name), redirect)
