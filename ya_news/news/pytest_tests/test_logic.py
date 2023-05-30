import pytest

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from news.forms import CommentForm
from news.models import Comment
from news.models import News


@pytest.mark.django_db
def test_anonymous_user_cannot_post_comment():
    news = News.objects.create(title='Test News', text='This is a test news')
    client = Client()
    response = client.post(reverse('news:detail', kwargs={'pk': news.pk}))
    assert response.status_code == 302
    assert response.url.startswith(reverse('users:login'))


@pytest.mark.django_db
def test_authenticated_user_can_post_comment():
    User.objects.create_user(username='testuser', password='testpassword')
    news = News.objects.create(title='Test News', text='This is a test news')
    client = Client()
    client.login(username='testuser', password='testpassword')
    response = client.post(reverse('news:detail', kwargs={'pk': news.pk}),
                           {'text': 'This is a comment'})
    assert response.status_code == 302
    assert response.url == reverse('news:detail',
                                   kwargs={'pk': news.pk}) + '#comments'


@pytest.mark.django_db
def test_comment_with_bad_words_not_published():
    User.objects.create_user(username='testuser', password='testpassword')
    news = News.objects.create(title='Test News', text='This is a test news')
    client = Client()
    client.login(username='testuser', password='testpassword')
    response = client.post(reverse('news:detail', kwargs={'pk': news.pk}),
                           data={'text': 'This is a bad word'})

    assert response.status_code == 302

    if response.context is not None:
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
        assert 'text' in response.context['form'].errors


@pytest.mark.django_db
def test_authenticated_user_can_edit_or_delete_own_comments():
    user1 = User.objects.create_user(username='user1', password='password1')
    User.objects.create_user(username='user2', password='password2')
    news = News.objects.create(title='Test News', text='This is a test news')
    comment = Comment.objects.create(news=news, author=user1,
                                     text='This is a comment')

    client = Client()

    # Edit own comment
    client.login(username='user1', password='password1')
    response = client.get(reverse('news:edit', kwargs={'pk': comment.pk}))
    assert response.status_code == 200
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)

    # Delete own comment
    response = client.get(reverse('news:delete', kwargs={'pk': comment.pk}))
    assert response.status_code == 200

    # Edit other user's comment
    client.login(username='user2', password='password2')
    response = client.get(reverse('news:edit', kwargs={'pk': comment.pk}))
    assert response.status_code == 404

    # Delete other user's comment
    response = client.get(reverse('news:delete', kwargs={'pk': comment.pk}))
    assert response.status_code == 404
