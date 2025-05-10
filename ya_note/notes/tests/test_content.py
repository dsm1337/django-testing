from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, reverse_lazy

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestHomePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Содержательный текст',
            slug='Note',
            author=cls.author
        )

    def test_note_in_list_for_different_users(self):
        url = reverse_lazy('notes:list')
        for current_user, expected_result in (
            (self.author, True),
            (self.reader, False)
        ):
            with self.subTest(current_user):
                self.client.force_login(current_user)
                self.assertEqual(
                    self.note in self.client.get(url).context['object_list'],
                    expected_result
                )

    def test_pages_contains_form(self):
        for name, args in (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        ):
            self.client.force_login(self.author)
            with self.subTest(name):
                context = self.client.get(reverse(name, args=args)).context
                self.assertIn('form', context)
                self.assertIsInstance(context['form'], NoteForm)
