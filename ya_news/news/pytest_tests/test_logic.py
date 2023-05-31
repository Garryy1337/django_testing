import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from http import HTTPStatus

from news.forms import CommentForm
from news.models import Comment
from news.models import News


@pytest.mark.django_db
def test_anonymous_user_cannot_post_comment():
    """
    Тест проверяет, что анонимный пользователь
      не может оставлять комментарии к новостям.

    """
    news = News.objects.create(title='Test News', text='This is a test news')
    client = Client()
    response = client.post(reverse('news:detail', kwargs={'pk': news.pk}))
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.startswith(reverse('users:login'))


@pytest.mark.django_db
def test_authenticated_user_can_post_comment():
    """
    Тест проверяет, что аутентифицированный
    пользователь может оставлять комментарии к новостям.

    """
    User.objects.create_user(username='testuser', password='testpassword')
    news = News.objects.create(title='Test News', text='This is a testnews')
    num_comments_before = Comment.objects.filter(news=news).count()
    client = Client()
    client.login(username='testuser', password='testpassword')
    response = client.post(reverse('news:detail', kwargs={'pk': news.pk}),
                           {'text': 'This is a comment'})
    assert response.status_code == HTTPStatus.FOUND
    num_comments_after = Comment.objects.filter(news=news).count()
    assert num_comments_after == num_comments_before + 1


@pytest.mark.django_db
def test_comment_with_bad_words_not_published():
    """
    Тест проверяет, что комментарий с неприемлемыми
      словами не может быть опубликован.

    """
    User.objects.create_user(username='testuser', password='testpassword')
    news = News.objects.create(title='Test News', text='This is a test news')
    client = Client()
    client.login(username='testuser', password='testpassword')
    response = client.post(reverse('news:detail', kwargs={'pk': news.pk}),
                           data={'text': 'This is a bad word'})

    assert response.status_code == HTTPStatus.FOUND

    if response.context is not None:
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
        assert 'text' in response.context['form'].errors


@pytest.mark.django_db
def test_authenticated_user_can_edit_or_delete_own_comments():
    """
    Тест проверяет, что аутентифицированный пользователь
    может редактировать и удалять свои собственные комментарии.

    """
    user1 = User.objects.create_user(username='user1', password='password1')
    User.objects.create_user(username='user2', password='password2')
    news = News.objects.create(title='Test News', text='This is a test news')
    comment = Comment.objects.create(news=news, author=user1,
                                     text='This is a comment')

    client = Client()

    client.login(username='user1', password='password1')
    response = client.get(reverse('news:edit', kwargs={'pk': comment.pk}))
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)

    response = client.get(reverse('news:delete', kwargs={'pk': comment.pk}))
    assert response.status_code == HTTPStatus.OK

    client.login(username='user2', password='password2')
    response = client.get(reverse('news:edit', kwargs={'pk': comment.pk}))
    assert response.status_code == HTTPStatus.NOT_FOUND

    response = client.get(reverse('news:delete', kwargs={'pk': comment.pk}))
    assert response.status_code == HTTPStatus.NOT_FOUND
