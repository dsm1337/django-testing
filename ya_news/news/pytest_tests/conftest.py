import pytest
from datetime import timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.mark.django_db
@pytest.fixture
def news():
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def multiple_news():
    all_news = (
        News(
            title=f'Новость {i}',
            text='Текст',
            date=(timezone.now() - timedelta(days=i))
        ) for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    News.objects.bulk_create(all_news)


@pytest.fixture
def id_news_for_args(news):
    return (news.id,)


@pytest.fixture
def comment(author, news, form_comment):
    return Comment.objects.create(
        news=news,
        text=form_comment['text'],
        author=author,
    )


@pytest.fixture
def multiple_comments(author, news):
    for i in range(10):
        comment = Comment.objects.create(
            news=news,
            text=f'Текст: {i}',
            author=author,
        )
        comment.created = timezone.now() + timedelta(days=i)
        comment.save()


@pytest.fixture
def id_comment_for_args(comment):
    return (comment.id,)


@pytest.fixture
def detail_url(id_news_for_args):
    return reverse('news:detail', args=id_news_for_args)


@pytest.fixture
def comment_url(detail_url):
    return detail_url + '#comments'


@pytest.fixture
def edit_url(id_comment_for_args):
    return reverse('news:edit', args=id_comment_for_args)


@pytest.fixture
def delete_url(id_comment_for_args):
    return reverse('news:delete', args=id_comment_for_args)


@pytest.fixture
def form_comment():
    return {
        'text': 'Текст Комментария'
    }


@pytest.fixture
def form_edit_comment():
    return {
        'text': 'Другой Текст Комментария'
    }


@pytest.fixture
def home_url():
    return reverse('news:home')
