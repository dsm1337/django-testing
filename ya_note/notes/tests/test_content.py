from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from .conftest import ADD_URL, BaseTestCase, get_edit_url, LIST_URL

User = get_user_model()


class TestHomePage(BaseTestCase):

    def test_note_in_list_for_author(self):
        notes = self.author_client.get(LIST_URL).context['object_list']
        self.assertIn(
            self.note, notes
        )
        note_from_context = notes.get(pk=self.note.pk)
        self.assertEqual(self.note.title, note_from_context.title)
        self.assertEqual(self.note.text, note_from_context.text)
        self.assertEqual(self.note.slug, note_from_context.slug)
        self.assertEqual(self.note.author, note_from_context.author)

    def test_note_in_list_for_reader(self):
        self.assertNotIn(
            self.note, self.reader_client.get(LIST_URL).context['object_list']
        )

    def test_pages_contains_form(self):
        for name in (ADD_URL, get_edit_url()):
            with self.subTest(name):
                context = self.author_client.get(name).context
                self.assertIn('form', context)
                self.assertIsInstance(context['form'], NoteForm)
