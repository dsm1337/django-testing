from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Заголовок заметки'
    NOTE_TEXT = 'Текст заметки'
    SLUG = 'qq'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='Тимур Леонов')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.NOTE_TITLE, 'text': cls.NOTE_TEXT, 'slug': cls.SLUG
        }

    def test_anonymus_user_cant_create(self):
        self.client.post(self.url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_can_create(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(
            (note.title, note.text, note.slug, note.author),
            (self.NOTE_TITLE, self.NOTE_TEXT, self.SLUG, self.user)
        )

    def test_user_cant_use_existed_slug(self):
        self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            self.auth_client.post(self.url, data={
                'title': 'Другой заголовок',
                'text': 'Другой текст',
                'slug': self.SLUG
            }).context['form'],
            'slug',
            f'{self.SLUG}{WARNING}'
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_creation_note_without_slug(self):
        self.form_data.pop('slug')
        self.assertRedirects(
            self.auth_client.post(self.url, data=self.form_data),
            reverse('notes:success')
        )
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(
            Note.objects.get().slug, slugify(self.form_data['title'])
        )


class TestNoteEditDelete(TestCase):
    NOTE_TITLE = 'Заголовок заметки'
    NOTE_TEXT = 'Текст заметки'
    SLUG = 'qq'
    NOTE_EDIT_ADDITION = '1'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Тимур Леонов')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.SLUG,
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.SLUG,))
        cls.delete_url = reverse('notes:delete', args=(cls.SLUG,))
        cls.form_data = {
            'title': cls.NOTE_TITLE + cls.NOTE_EDIT_ADDITION,
            'text': cls.NOTE_TEXT + cls.NOTE_EDIT_ADDITION,
            'slug': cls.SLUG + cls.NOTE_EDIT_ADDITION
        }
        cls.url_to_success = reverse('notes:success')

    def test_author_can_delete(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.url_to_success)
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND
        )
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_comment_of_another_user(self):
        self.assertEqual(
            self.reader_client.delete(self.delete_url).status_code,
            HTTPStatus.NOT_FOUND
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.url_to_success)
        self.note.refresh_from_db()
        self.assertEqual(
            (self.note.title, self.note.text, self.note.slug),
            (self.form_data['title'], self.form_data['text'],
             self.form_data['slug'])
        )

    def test_user_cant_edit_comment_of_another_user(self):
        self.reader_client.post(self.edit_url, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(
            (self.note.title, self.note.text, self.note.slug),
            (self.NOTE_TITLE, self.NOTE_TEXT, self.SLUG)
        )
