from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('id_news_for_args')),
        ('users:login', None),
        ('users:signup', None),
    )
)
def test_pages_availability(name, client, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    ('parametrized_client', 'expected_result'),
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    (
        'news:edit', 'news:delete'
    )
)
def test_availability_for_comment_edit_and_delete(
        parametrized_client, expected_result, name, id_comment_for_args
):
    url = reverse(name, args=id_comment_for_args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_result


@pytest.mark.parametrize(
    'name',
    (
        'news:edit', 'news:delete'
    )
)
def test_redirect_for_anonymous_client(name, id_comment_for_args, client):
    login_url = reverse('users:login')
    url = reverse(name, args=id_comment_for_args)
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
