from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse, reverse_lazy

from notes.models import Note

HOME_URL = reverse_lazy('notes:home')
LIST_URL = reverse_lazy('notes:list')
ADD_URL = reverse_lazy('notes:add')
SUCCESS_URL = reverse_lazy('notes:success')
LOGIN_URL = reverse_lazy('users:login')
SIGNUP_URL = reverse_lazy('users:signup')

DEFAULT_SLUG = 'Note'


def get_detail_url(slug=DEFAULT_SLUG):
    return reverse('notes:detail', args=(slug,))


def get_edit_url(slug=DEFAULT_SLUG):
    return reverse('notes:edit', args=(slug,))


def get_delete_url(slug=DEFAULT_SLUG):
    return reverse('notes:delete', args=(slug,))


User = get_user_model()


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Содержательный текст',
            slug=DEFAULT_SLUG,
            author=cls.author
        )
