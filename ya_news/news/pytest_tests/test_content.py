import datetime

import pytest

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from news.models import Comment
from news.models import News

User = get_user_model()


@pytest.mark.django_db
def test_home_page_displays_up_to_10_news():
    for i in range(11):
        News.objects.create(title=f'Test News {i}',
                            text=f'This is test news {i}')
    client = Client()
    response = client.get(reverse('news:home'))
    assert response.status_code == 200
    assert len(response.context['news_feed']) == 10


@pytest.mark.django_db
def test_news_are_sorted_by_date_descending_on_home_page():
    news3 = News.objects.create(title='Test News 3',
                                text='This is test news 3')
    news2 = News.objects.create(title='Test News 2',
                                text='This is test news 2')
    news1 = News.objects.create(title='Test News 1',
                                text='This is test news 1')
    client = Client()
    response = client.get(reverse('news:home'))
    assert response.status_code == 200
    news_feed = response.context['news_feed']
    assert news_feed[0] == news3
    assert news_feed[1] == news2
    assert news_feed[2] == news1


@pytest.mark.django_db
def test_comments_are_sorted_by_created_ascending_on_news_detail_page():
    news = News.objects.create(title='Test News', text='This is a test news')
    comment1 = Comment.objects.create(news=news, text='Comment 1',
                                      created=datetime.datetime(2023, 1, 1, 12,
                                                                0, 0))
    comment2 = Comment.objects.create(news=news, text='Comment 2',
                                      created=datetime.datetime(2023, 1, 2, 12,
                                                                0, 0))
    comment3 = Comment.objects.create(news=news, text='Comment 3',
                                      created=datetime.datetime(2023, 1, 3, 12,
                                                                0, 0))

    client = Client()
    response = client.get(reverse('news:detail', kwargs={'pk': news.pk}))
    assert response.status_code == 200
    comments = response.context[
        'news'].comments.all()
    assert list(comments) == [comment1, comment2, comment3]


@pytest.mark.django_db
def test_comment_form_not_accessible_to_anonymous_user():
    User.objects.create_user(username='testuser', password='testpassword')
    news = News.objects.create(title='Test News', text='This is a test news')
    client = Client()
    response = client.get(reverse('news:detail', kwargs={'pk': news.pk}))
    assert response.status_code == 200
    assert 'form' not in response.context


@pytest.mark.django_db
def test_comment_form_accessible_to_authenticated_user():
    User.objects.create_user(username='testuser', password='testpassword')
    news = News.objects.create(title='Test News', text='This is a test news')
    client = Client()
    client.login(username='testuser', password='testpassword')
    response = client.get(reverse('news:detail', kwargs={'pk': news.pk}))
    assert response.status_code == 200
    assert 'form' in response.context
