from django.conf import settings
import pytest

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_news_count(multiple_news, client, home_url):
    assert (
        client.get(home_url).context['object_list'].count()
        == settings.NEWS_COUNT_ON_HOME_PAGE
    )


def test_news_ordering(multiple_news, client, home_url):
    all_dates = [
        news.date
        for news in client.get(home_url).context['object_list']
    ]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(client, multiple_comments, detail_url):
    context = client.get(detail_url).context
    assert 'news' in context
    all_timestamps = [
        comment.created for comment in context['news'].comment_set.all()
    ]
    assert all_timestamps == sorted(all_timestamps)


def test_presence_of_form_for_author(
    author_client, detail_url, multiple_comments
):
    response = author_client.get(detail_url)
    assert isinstance(response.context.get('form'), CommentForm)


def test_presence_of_form_for_non_author(
    client, detail_url, multiple_comments
):
    assert 'form' not in client.get(detail_url).context
