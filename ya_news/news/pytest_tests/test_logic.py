from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


FORM = {'text': 'Текст комментария'}
EDIT_FORM = {'text': 'Другой Текст комментария'}


def check_comment_state(expected_comment, text=None):
    curr_comment = Comment.objects.get()
    assert (
        curr_comment.text
        == text if text is not None else expected_comment.text
    )
    assert curr_comment.author == expected_comment.author
    assert curr_comment.news == expected_comment.news


def test_anonymous_user_cant_create_comment(
    client, news, detail_url
):
    client.post(detail_url, data=FORM)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author, author_client, news, detail_url, comment_url
):
    assertRedirects(
        author_client.post(detail_url, data=FORM),
        comment_url
    )
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == FORM['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize(
    'bad_word',
    BAD_WORDS
)
def test_user_cant_use_bad_words(author_client, detail_url, bad_word):
    FORM['text'] = f'Текст {bad_word} еще текст'
    assertFormError(
        author_client.post(
            detail_url, data=FORM
        ).context['form'],
        'text',
        WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
    author_client, delete_url, detail_url, comment_url
):
    response = author_client.delete(delete_url)
    assertRedirects(response, comment_url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
    not_author_client, delete_url, detail_url, comment_url, comment
):
    assert (
        not_author_client.delete(delete_url).status_code
        == HTTPStatus.NOT_FOUND
    )
    assert Comment.objects.count() == 1
    check_comment_state(comment)


def test_author_can_edit_comment(
    author_client, edit_url, comment_url, comment
):
    assertRedirects(
        author_client.post(edit_url, data=EDIT_FORM), comment_url
    )
    check_comment_state(comment, EDIT_FORM['text'])


def test_user_cant_edit_comment_of_another_user(
    not_author_client, edit_url, comment
):
    response = not_author_client.post(edit_url, data=EDIT_FORM)
    assert response.status_code == HTTPStatus.NOT_FOUND
    curr_comment = Comment.objects.get()
    assert curr_comment.text != EDIT_FORM['text']
    check_comment_state(comment)
