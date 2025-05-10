from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects

URLS = {
    'home': pytest.lazy_fixture('home_url'),
    'detail': pytest.lazy_fixture('detail_url'),
    'edit': pytest.lazy_fixture('edit_url'),
    'delete': pytest.lazy_fixture('delete_url'),
    'login': reverse('users:login'),
    'signup': reverse('users:signup'),
}


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name, parametrized_client, expected_response',
    (
        (URLS['home'], pytest.lazy_fixture('client'), HTTPStatus.OK),
        (URLS['detail'], pytest.lazy_fixture('client'), HTTPStatus.OK),
        (URLS['login'], pytest.lazy_fixture('client'), HTTPStatus.OK),
        (URLS['signup'], pytest.lazy_fixture('client'), HTTPStatus.OK),
        (URLS['edit'], pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (URLS['edit'], pytest.lazy_fixture('not_author_client'),
         HTTPStatus.NOT_FOUND),
        (URLS['delete'], pytest.lazy_fixture('not_author_client'),
         HTTPStatus.NOT_FOUND),
        (URLS['delete'], pytest.lazy_fixture('author_client'), HTTPStatus.OK),
    )
)
def test_pages_availability(name, parametrized_client, expected_response):
    assert (
        parametrized_client.get(name).status_code == expected_response
    )


@pytest.mark.parametrize(
    'name',
    (
        URLS['edit'], URLS['delete']
    )
)
def test_redirect_for_anonymous_client(name, client):
    assertRedirects(client.get(name), f'{URLS['login']}?next={name}')
