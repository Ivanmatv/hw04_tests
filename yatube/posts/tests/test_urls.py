from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Ivan')
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    # Проверка доступа к общедоступным страницам
    def test_urls_exist_at_desired_locations(self):
        """Страницы доступны по указанным адресам для всех пользователей."""
        url_response_status_code = {
            '': HTTPStatus.OK.value,
            '/group/test-slug/': HTTPStatus.OK.value,
            '/profile/Ivan/': HTTPStatus.OK.value,
            f'/posts/{self.post.pk}/': HTTPStatus.OK.value,
            '/unexisting_page/': HTTPStatus.NOT_FOUND.value,
        }

        for url, status_code in url_response_status_code.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    # Проверяем доступность страниц для авторизованного пользователя
    def test_post_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get("/create/")
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    # Проверяем доступность страницы редактирования автору
    def test_post_edit_url_exists_at_desired_location(self):
        """Страница /posts/<post_id>/edit/ доступна автору публикации."""
        response = self.authorized_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    # Проверка редиректов для неавторизованного пользователя
    def test_urls_redirect_anonymous_on_login(self):
        """Страница перенаправит анонимного пользователя на страницу логина."""
        url_redirect_to_url = {
            '/auth/login/?next=/create/': '/create/',
            f'/auth/login/?next=/posts/{self.post.pk}/edit/':
            f'/posts/{self.post.pk}/edit/',
        }
        for redirect, url in url_redirect_to_url.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect)

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/Ivan/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
