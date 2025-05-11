from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from .conftest import ADD_URL, BaseTestCase, EDIT_URL, LIST_URL

User = get_user_model()


class TestHomePage(BaseTestCase):

    def test_note_in_list_for_author(self):
        notes = self.author_client.get(LIST_URL).context['object_list']
        self.assertIn(
            self.note, notes
        )
        note = notes.get(pk=self.note.pk)
        self.assertEqual(self.note.title, note.title)
        self.assertEqual(self.note.text, note.text)
        self.assertEqual(self.note.slug, note.slug)
        self.assertEqual(self.note.author, note.author)

    def test_note_in_list_for_reader(self):
        self.assertNotIn(
            self.note, self.reader_client.get(LIST_URL).context['object_list']
        )

    def test_pages_contains_form(self):
        for url in (ADD_URL, EDIT_URL):
            with self.subTest(url):
                context = self.author_client.get(url).context
                self.assertIn('form', context)
                self.assertIsInstance(context['form'], NoteForm)
