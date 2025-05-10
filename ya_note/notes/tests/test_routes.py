from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

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

    def test_availability(self):
        urls = (
            'notes:home',
            'users:login',
            # ('users:logout', None),
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                self.assertEqual(
                    self.client.get(reverse(name)).status_code,
                    HTTPStatus.OK
                )

    def test__availability_for_user_required_pages(self):
        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
        )
        self.client.force_login(self.author)
        for name, args in urls:
            with self.subTest(name=name):
                self.assertEqual(
                    self.client.get(reverse(name, args=args)).status_code,
                    HTTPStatus.OK
                )

    def test_availability_for_owners_page(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = ('notes:edit', 'notes:detail', 'notes:delete')
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(user=user, name=name):
                    self.assertEqual(
                        self.client.get(
                            reverse(name, args=(self.note.slug,))
                        ).status_code,
                        status
                    )

    def test_anonymus_redirect(self):
        login_url = settings.LOGIN_URL
        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                self.assertRedirects(
                    self.client.get(url), f'{login_url}?next={url}'
                )
