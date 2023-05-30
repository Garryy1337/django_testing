import pytest

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse_lazy

from news.models import Comment
from news.models import News


@pytest.mark.django_db
def test_anonymous_user_can_access_home_page():
    client = Client()
    response = client.get(reverse_lazy('news:home'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_anonymous_user_can_access_news_detail_page():
    news = News.objects.create(title='Test News', text='This is a test news')
    client = Client()
    response = client.get(reverse_lazy('news:detail', kwargs={'pk': news.pk}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_comment_author_can_access_edit_comment_page():
    user = User.objects.create_user(username='testuser',
                                    password='testpassword')
    news = News.objects.create(title='Test News', text='This is a test news')
    comment = Comment.objects.create(news=news, author=user,
                                     text='Test comment')
    client = Client()
    client.login(username='testuser', password='testpassword')
    response = client.get(reverse_lazy('news:edit', kwargs={'pk': comment.pk}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_comment_author_can_access_delete_comment_page():
    user = User.objects.create_user(username='testuser',
                                    password='testpassword')
    news = News.objects.create(title='Test News', text='This is a test news')
    comment = Comment.objects.create(news=news, author=user,
                                     text='Test comment')
    client = Client()
    client.login(username='testuser', password='testpassword')
    response = client.get(
        reverse_lazy('news:delete', kwargs={'pk': comment.pk}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_anonymous_user_redirected_to_login_page_when_accessing_edit_page():
    news = News.objects.create(title='Test News', text='This is a test news')
    comment = Comment.objects.create(news=news, author=None,
                                     text='Test comment')
    client = Client()
    response = client.get(reverse_lazy('news:edit', kwargs={'pk': comment.pk}))
    assert response.status_code == 302
    assert response.url == '/auth/login/?next=' + \
           reverse_lazy('news:edit',
                        kwargs={
                            'pk': comment.pk})


@pytest.mark.django_db
def test_anonymous_user_redirected_to_login_page_when_delete_comment_page():
    news = News.objects.create(title='Test News', text='This is a test news')
    comment = Comment.objects.create(news=news, author=None,
                                     text='Test comment')
    client = Client()
    response = client.get(
        reverse_lazy('news:delete', kwargs={'pk': comment.pk}))
    assert response.status_code == 302
    assert response.url == '/auth/login/?next=' + \
           reverse_lazy('news:delete',
                        kwargs={
                            'pk': comment.pk})


@pytest.mark.django_db
def test_user_cannot_access_edit_or_delete_comment_page_of_other_users():
    user1 = User.objects.create_user(username='testuser1',
                                     password='testpassword')
    user2 = User.objects.create_user(username='testuser2',
                                     password='testpassword')
    news = News.objects.create(title='Test News', text='This is a test news')
    comment = Comment.objects.create(news=news, author=user1,
                                     text='Test comment')
    client = Client()
    client.force_login(user2)
    response_edit = client.get(reverse_lazy(
        'news:edit', kwargs={'pk': comment.pk}))
    response_delete = client.get(reverse_lazy(
        'news:delete', kwargs={'pk': comment.pk}))
    assert response_edit.status_code == 404
    assert response_delete.status_code == 404


@pytest.mark.django_db
def test_user_cannot_access_delete_comment_page_of_other_users():
    user1 = User.objects.create_user(username='testuser1',
                                     password='testpassword')
    user2 = User.objects.create_user(username='testuser2',
                                     password='testpassword')
    news = News.objects.create(title='Test News', text='This is a test news')
    comment = Comment.objects.create(news=news, author=user1,
                                     text='Test comment')
    client = Client()
    client.force_login(user2)
    response = client.get(reverse_lazy(
        'news:delete', kwargs={'pk': comment.pk}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_registration_login_logout_pages_accessible_to_anonymous_user():
    client = Client()
    response = client.get(reverse_lazy('users:signup'))
    assert response.status_code == 200

    response = client.get(reverse_lazy('users:login'))
    assert response.status_code == 200

    response = client.get(reverse_lazy('users:logout'), follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == []
