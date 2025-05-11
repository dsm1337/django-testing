from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .conftest import (
    BaseTestCase, SUCCESS_URL
)
User = get_user_model()


class TestNoteEditDelete(BaseTestCase):

    def test_anonymus_user_cant_create(self):
        all_notes = set(Note.objects.all())
        self.client.post(self.add_url, data=self.form_data)
        self.assertSetEqual(set(Note.objects.all()), all_notes)

    def test_user_can_create(self):
        all_notes = set(Note.objects.all())
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        notes_difference = set(Note.objects.all()) - all_notes
        self.assertEqual(len(notes_difference), 1)
        added_note = notes_difference.pop()
        self.assertEqual(added_note.title, self.form_data['title'])
        self.assertEqual(added_note.text, self.form_data['text'])
        self.assertEqual(added_note.slug, self.form_data['slug'])
        self.assertEqual(added_note.author, self.author)

    def test_user_cant_use_existed_slug(self):
        Note.objects.create(
            title=self.form_data['title'],
            text=self.form_data['text'],
            slug=self.form_data['slug'],
            author=self.author
        )
        all_notes = set(Note.objects.all())
        self.form_data['slug'] = self.note.slug
        self.assertFormError(
            self.author_client.post(
                self.add_url, data=self.form_data
            ).context['form'],
            'slug',
            f'{self.note.slug}{WARNING}'
        )
        notes_difference = set(Note.objects.all()) - all_notes
        self.assertEqual(len(notes_difference), 0)
        curr_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(curr_note.text, self.note.text)
        self.assertEqual(curr_note.title, self.note.title)
        self.assertEqual(curr_note.slug, self.note.slug)
        self.assertEqual(curr_note.author, self.note.author)

    def test_creation_note_without_slug(self):
        all_notes = set(Note.objects.all())
        self.form_data.pop('slug')
        self.assertRedirects(
            self.author_client.post(self.add_url, data=self.form_data),
            SUCCESS_URL
        )
        notes_difference = set(Note.objects.all()) - all_notes
        self.assertEqual(len(notes_difference), 1)
        added_note = notes_difference.pop()
        self.assertEqual(added_note.title, self.form_data['title'])
        self.assertEqual(added_note.text, self.form_data['text'])
        self.assertEqual(added_note.slug, slugify(self.form_data['title']))
        self.assertEqual(added_note.author, self.author)

    def test_author_can_delete(self):
        amount_of_notes = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.url_to_success)
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND
        )
        self.assertEqual(Note.objects.count(), amount_of_notes - 1)
        self.assertFalse(Note.objects.filter(pk=self.note.id).exists())

    def test_user_cant_delete_note_of_another_user(self):
        self.assertEqual(
            self.reader_client.delete(self.delete_url).status_code,
            HTTPStatus.NOT_FOUND
        )
        self.assertEqual(Note.objects.count(), 1)
        self.assertTrue(Note.objects.filter(pk=self.note.id).exists())
        curr_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(curr_note.text, self.note.text)
        self.assertEqual(curr_note.title, self.note.title)
        self.assertEqual(curr_note.slug, self.note.slug)
        self.assertEqual(curr_note.author, self.note.author)

    def test_author_can_edit(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.url_to_success)
        edit_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(edit_note.title, self.form_data['title'])
        self.assertEqual(edit_note.text, self.form_data['text'])
        self.assertEqual(edit_note.slug, self.form_data['slug'])
        self.assertEqual(edit_note.author, self.note.author)

    def test_user_cant_edit_note_of_another_user(self):
        self.reader_client.post(self.edit_url, data=self.form_data)
        curr_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(curr_note.text, self.note.text)
        self.assertEqual(curr_note.title, self.note.title)
        self.assertEqual(curr_note.slug, self.note.slug)
        self.assertEqual(curr_note.author, self.note.author)
