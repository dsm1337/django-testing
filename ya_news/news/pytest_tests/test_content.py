import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
@pytest.mark.usefixtures('multiple_news')
class TestHomePage:
    HOME_URL = reverse('news:home')

    def test_news_count(self, client):
        object_list = client.get(self.HOME_URL).context['object_list']
        news_count = object_list.count()
        assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE

    def test_news_ordering(self, client):
        all_dates = [
            news.date
            for news in client.get(self.HOME_URL).context['object_list']
        ]
        assert all_dates == sorted(all_dates, reverse=True)


@pytest.mark.django_db
@pytest.mark.usefixtures(
    'multiple_comments'
)
class TestComments:

    def test_comments_order(self, client, detail_url):
        context = client.get(detail_url).context
        assert 'news' in context
        all_timestamps = [
            comment.created for comment in context['news'].comment_set.all()
        ]
        assert all_timestamps == sorted(all_timestamps)

    @pytest.mark.parametrize(
        ('current_client', 'expected_result'),
        (
            (pytest.lazy_fixture('author_client'), True),
            (pytest.lazy_fixture('client'), False)
        )
    )
    def test_presence_of_form_for_diffrent_users(
        self, current_client, expected_result, detail_url
    ):
        response = current_client.get(detail_url)
        assert ('form' in response.context) == expected_result
        if expected_result:
            assert isinstance(response.context['form'], CommentForm)
