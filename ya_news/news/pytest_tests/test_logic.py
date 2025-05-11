from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


FORM = {'text': 'Текст комментария'}


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
    form_with_bad_word = FORM.copy()
    form_with_bad_word['text'] = f'Текст {bad_word} еще текст'
    assertFormError(
        author_client.post(
            detail_url, data=form_with_bad_word
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
    curr_comment = Comment.objects.get(pk=comment.id)
    assert curr_comment.text == comment.text
    assert curr_comment.author == comment.author
    assert curr_comment.news == comment.news


def test_author_can_edit_comment(
    author_client, edit_url, comment_url, comment
):
    form_edit = FORM.copy()
    form_edit['text'] = 'Абсолютно другой текст'
    assertRedirects(
        author_client.post(edit_url, data=form_edit), comment_url
    )
    curr_comment = Comment.objects.get(pk=comment.id)
    assert curr_comment.text == form_edit['text']
    assert curr_comment.author == comment.author
    assert curr_comment.news == comment.news


def test_user_cant_edit_comment_of_another_user(
    not_author_client, edit_url, comment
):
    form_edit = FORM.copy()
    form_edit['text'] = 'Абсолютно другой текст'
    response = not_author_client.post(edit_url, data=form_edit)
    assert response.status_code == HTTPStatus.NOT_FOUND
    curr_comment = Comment.objects.get(pk=comment.id)
    assert curr_comment.text == comment.text
    assert curr_comment.author == comment.author
    assert curr_comment.news == comment.news
