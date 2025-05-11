from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse, reverse_lazy

from notes.models import Note


DEFAULT_SLUG = 'Note'


HOME_URL = reverse_lazy('notes:home')
LIST_URL = reverse_lazy('notes:list')
ADD_URL = reverse_lazy('notes:add')
SUCCESS_URL = reverse_lazy('notes:success')
LOGIN_URL = reverse_lazy('users:login')
SIGNUP_URL = reverse_lazy('users:signup')
DETAIL_URL = reverse('notes:detail', args=(DEFAULT_SLUG,))
EDIT_URL = reverse('notes:edit', args=(DEFAULT_SLUG,))
DELETE_URL = reverse('notes:delete', args=(DEFAULT_SLUG,))
REDIRECT_ADD_URL = f'{LOGIN_URL}?next={ADD_URL}'
REDIRECT_EDIT_URL = f'{LOGIN_URL}?next={EDIT_URL}'
REDIRECT_DELETE_URL = f'{LOGIN_URL}?next={DELETE_URL}'
REDIRECT_DETAIL_URL = f'{LOGIN_URL}?next={DETAIL_URL}'
REDIRECT_LIST_URL = f'{LOGIN_URL}?next={LIST_URL}'
REDIRECT_SUCCESS_URL = f'{LOGIN_URL}?next={SUCCESS_URL}'

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
        cls.add_url = ADD_URL
        cls.edit_url = EDIT_URL
        cls.delete_url = DELETE_URL
        cls.form_data = {
            'title': 'Другой заголовок',
            'text': 'Другой текст',
            'slug': 'Another_slug'
        }
        cls.url_to_success = SUCCESS_URL
