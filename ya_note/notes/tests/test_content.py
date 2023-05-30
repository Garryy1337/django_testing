from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse_lazy

from notes.models import Note
from notes.views import NoteCreate, NoteUpdate


class NoteTestCase(TestCase):
    """
    Тесты для модели Note.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='user1',
                                             password='password1')
        cls.user2 = User.objects.create_user(username='user2',
                                             password='password2')
        cls.note1 = Note.objects.create(title='Note 1', text='Note 1 Text',
                                        author=cls.user1)
        cls.note2 = Note.objects.create(title='Note 2', text='Note 2 Text',
                                        author=cls.user2)

    def assertFormOnPage(self, response, form_class):
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], form_class)

    def test_note_in_object_list_for_authenticated_user(self):
        """
        Проверка, что заметка пользователя отображается в списке заметок.
        """
        self.client.force_login(self.user1)
        response = self.client.get(reverse_lazy('notes:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.note1.title)

    def test_note_not_in_object_list_for_other_user(self):
        """
       Проверка, что заметка другого пользователя не отображается
         в списке заметок.
        """
        self.client.force_login(self.user1)
        response = self.client.get(reverse_lazy('notes:list'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.note2.title)

    def test_note_form_in_note_create_page(self):
        """
        Проверка, что форма создания заметки отображается
          на странице создания заметки.
        """
        self.client.force_login(self.user1)
        response = self.client.get(reverse_lazy('notes:add'))
        self.assertFormOnPage(response, NoteCreate.form_class)

    def test_note_form_in_note_update_page(self):
        """
        Проверка, что форма редактирования заметки отображается
          на странице редактирования заметки.
        """
        self.client.force_login(self.user1)
        response = self.client.get(reverse_lazy(
            'notes:edit', args=[self.note1.slug]))
        self.assertFormOnPage(response, NoteUpdate.form_class)
