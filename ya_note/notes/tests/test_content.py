from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.views import NoteCreate
from notes.views import NoteUpdate


class NoteTestCase(TestCase):
    """
    Тесты для модели Note.
    """
    def setUp(self):
        """
        Создание пользователей и заметок для тестирования.
        """
        self.user1 = User.objects.create_user(username='user1',
                                              password='password1')
        self.user2 = User.objects.create_user(username='user2',
                                              password='password2')
        self.note1 = Note.objects.create(title='Note 1', text='Note 1 Text',
                                         author=self.user1)
        self.note2 = Note.objects.create(title='Note 2', text='Note 2 Text',
                                         author=self.user2)

    def test_note_in_object_list_for_authenticated_user(self):
        """
        Проверка, что заметка пользователя отображается в списке заметок.
        """
        self.client.login(username='user1', password='password1')
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.note1.title)

    def test_note_not_in_object_list_for_other_user(self):
        """
        Проверка, что заметка другого пользователя
          не отображается в списке заметок.
        """
        self.client.login(username='user1', password='password1')
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.note2.title)

    def test_note_form_in_note_create_page(self):
        """
        Проверка, что форма создания заметки отображается
          на странице создания заметки.
        """
        self.client.login(username='user1', password='password1')
        response = self.client.get(reverse('notes:add'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], NoteCreate.form_class)

    def test_note_form_in_note_update_page(self):
        """
        Проверка, что форма редактирования заметки отображается
          на странице редактирования заметки.
        """
        self.client.login(username='user1', password='password1')
        response = self.client.get(
            reverse('notes:edit', args=[self.note1.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], NoteUpdate.form_class)
