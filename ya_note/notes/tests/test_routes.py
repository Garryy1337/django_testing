from http import HTTPStatus
from django.test import Client
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class NoteTestCase(TestCase):
    """
    Тесты для модели Note.
    """
    def setUp(self):
        """
        Создание тестовых объектов.
        """
        self.client = Client()
        self.user = User.objects.create_user(username='testuser',
                                             password='testpassword')
        self.note = Note.objects.create(title='Test Note',
                                        text='Test Note Text',
                                        author=self.user)

    def test_anon_user_can_access_home_page(self):
        """
        Анонимный пользователь может получить доступ к домашней странице.
        """
        response = self.client.get(reverse('notes:home'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_user_can_access_notes_pages(self):
        """
        Аутентифицированный пользователь может
        получить доступ к страницам заметок.
        """
        self.client.login(username='testuser', password='testpassword')
        pages = ['notes:list', 'notes:add', 'notes:success']
        for page in pages:
            response = self.client.get(reverse(page))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anonymous_user_redirected_to_login_page(self):
        """
        Анонимный пользователь перенаправляется на страницу входа.
        """
        response = self.client.get(reverse('notes:list'))
        urls = ['notes:list', 'notes:add', 'notes:success']
        for url in urls:
            response = self.client.get(reverse(url))
            self.assertEqual(response.status_code, HTTPStatus.FOUND)
            self.assertEqual(response.url, reverse(
                'users:login') + '?next=' + reverse(url))

    def test_note_detail_page_redirects_to_login_for_unauthorized_user(self):
        """
        Страница деталей заметки перенаправляет
          на страницу входа для неавторизованного пользователя.
        """
        note = Note.objects.create(
            title='Another Note',
            text='Another Note Text',
            author=User.objects.create_user(username='anotheruser',
                                            password='testpassword')
        )
        response = self.client.get(reverse('notes:detail', args=[note.slug]))
        self.assertRedirects(response,
                             reverse('users:login') + '?next=' + reverse(
                                 'notes:detail', args=[note.slug]))
