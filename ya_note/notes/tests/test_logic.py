from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .conftest import (
    ADD_URL, BaseTestCase, get_edit_url, get_delete_url, SUCCESS_URL
)
User = get_user_model()


class TestNoteEditDelete(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.add_url = ADD_URL
        cls.edit_url = get_edit_url()
        cls.delete_url = get_delete_url()
        cls.form_data = {
            'title': 'Другой заголовок',
            'text': 'Другой текст',
            'slug': 'Another_slug'
        }
        cls.url_to_success = SUCCESS_URL

    def check_note_state(self, title, text, slug, author):
        curr_note = Note.objects.get(slug=slug)
        self.assertEqual(curr_note.text, text)
        self.assertEqual(curr_note.title, title)
        self.assertEqual(curr_note.slug, slug)
        self.assertEqual(curr_note.author, author)

    def test_anonymus_user_cant_create(self):
        amount_of_notes = Note.objects.count()
        self.client.post(self.add_url, data=self.form_data)
        self.assertEqual(Note.objects.count(), amount_of_notes)

    def test_user_can_create(self):
        amount_of_notes = Note.objects.count()
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), amount_of_notes + 1)
        self.check_note_state(
            title=self.form_data['title'],
            text=self.form_data['text'],
            slug=self.form_data['slug'],
            author=self.author
        )

    def test_user_cant_use_existed_slug(self):
        amount_of_notes = Note.objects.count()
        self.author_client.post(self.add_url, data=self.form_data)
        self.form_data['slug'] = self.note.slug
        self.assertFormError(
            self.author_client.post(
                self.add_url, data=self.form_data
            ).context['form'],
            'slug',
            f'{self.note.slug}{WARNING}'
        )
        self.assertEqual(Note.objects.count(), amount_of_notes + 1)
        self.check_note_state(
            title=self.note.title,
            text=self.note.text,
            slug=self.note.slug,
            author=self.note.author
        )

    def test_creation_note_without_slug(self):
        amount_of_notes = Note.objects.count()
        self.form_data.pop('slug')
        self.assertRedirects(
            self.author_client.post(self.add_url, data=self.form_data),
            SUCCESS_URL
        )
        self.assertEqual(Note.objects.count(), amount_of_notes + 1)
        last_added_object = Note.objects.order_by("id").last()
        self.assertEqual(
            last_added_object.slug,
            slugify(self.form_data['title'])
        )
        self.check_note_state(
            title=self.form_data['title'],
            text=self.form_data['text'],
            slug=last_added_object.slug,
            author=self.author
        )

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
        self.check_note_state(
            title=self.note.title,
            text=self.note.text,
            slug=self.note.slug,
            author=self.note.author
        )

    def test_author_can_edit(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.url_to_success)
        self.check_note_state(
            title=self.form_data['title'],
            text=self.form_data['text'],
            slug=self.form_data['slug'],
            author=self.author
        )

    def test_user_cant_edit_note_of_another_user(self):
        self.reader_client.post(self.edit_url, data=self.form_data)
        self.check_note_state(
            title=self.note.title,
            text=self.note.text,
            slug=self.note.slug,
            author=self.note.author
        )
