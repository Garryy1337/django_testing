import pytest
import datetime
from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from news.models import Comment
from news.models import News

User = get_user_model()


@pytest.fixture
def create_news():
    """
    Фикстура для создания трех тестовых новостей.

    Возвращает кортеж из трех объектов модели News.
    """
    news3 = News.objects.create(
        title='Тестовая новость 3', text='Это тестовая новость 3')
    news2 = News.objects.create(
        title='Тестовая новость 2', text='Это тестовая новость 2')
    news1 = News.objects.create(
        title='Тестовая новость 1', text='Это тестовая новость 1')
    return news1, news2, news3


@pytest.fixture
def create_news_db():
    """
    Фикстура для создания новости в базе данных.

    Возвращает функцию, которая принимает два аргумента: title и text,
    и создает новую запись в базе данных модели News с указанными значениями.
    """
    def _create_news(title, text):
        return News.objects.create(title=title, text=text)

    return _create_news


@pytest.mark.django_db
def test_home_page_displays_up_to_10_news(create_news_db):
    """Проверка, что домашняя страница отображает до 10 новостей."""
    # Создаем 11 новостей
    for i in range(11):
        create_news_db(f'Test News {i}', f'This is test news {i}')
    client = Client()
    response = client.get(reverse('news:home'))
    assert response.status_code == HTTPStatus.OK
    assert len(response.context['news_feed']) == 10


@pytest.mark.django_db
def test_news_are_sorted_by_date_descending_on_home_page(create_news):
    """
    Тест проверяет, что на главной странице новости
      отсортированы по дате в порядке убывания.
    """
    news1, news2, news3 = create_news
    client = Client()
    response = client.get(reverse('news:home'))
    assert response.status_code == HTTPStatus.OK
    news_feed = response.context['news_feed']
    assert news_feed[0] == news3
    assert news_feed[1] == news2
    assert news_feed[2] == news1


@pytest.mark.django_db
def test_comments_are_sorted_by_created_ascending_on_news_detail_page():
    """
    Тест проверяет, что на странице деталей новости комментарии
      отсортированы по дате создания в порядке возрастания.
    """
    news = News.objects.create(title='Test News', text='This is a test news')
    # Создаем комментарии с датами в обратном порядке
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
    assert response.status_code == HTTPStatus.OK
    comments = response.context['news'].comments.all()
    assert list(comments) == [comment1, comment2, comment3]


@pytest.mark.django_db
def test_comment_form_not_accessible_to_anonymous_user():
    """
    Тест проверяет, что форма комментариев
      не доступна для неавторизованного пользователя.
    """
    news = News.objects.create(title='Test News', text='This is a test news')
    client = Client()
    response = client.get(reverse('news:detail', kwargs={'pk': news.pk}))
    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context
    assert 'form_comment' not in response.context


@pytest.mark.django_db
def test_comment_form_accessible_to_authenticated_user():
    """
    Тест проверяет, что форма комментариев доступна
      для авторизованного пользователя.
    """
    user = User.objects.create_user(
        username='testuser', password='testpassword')
    news = News.objects.create(title='Test News', text='This is a testnews')
    user = Client()
    user.login(username='testuser', password='testpassword')
    response = user.get(reverse('news:detail', kwargs={'pk': news.pk}))
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
