from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus

from posts.models import Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Ivan')
        cls.user_noauthor = User.objects.create_user(username='Igor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        # Создаём третий клиент
        self.authorized_client_noauthor = Client()
        # Авторизуем не автора постов
        self.authorized_client_noauthor.force_login(self.user_noauthor)

    def test_create_post(self):
        post_create = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        created_post = Post.objects.latest('pk')

        self.assertEqual(Post.objects.count(), post_create + 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': created_post.author})
        )
        self.assertEqual(created_post.text, form_data['text'])
        self.assertEqual(created_post.group_id, form_data['group'])

    def test_guest_create_post(self):
        post_create = Post.objects.count()
        form_data = {
            'text': 'Текст от гостя',
            'group': self.group.id,
        }

        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), post_create)

    def test_post_edit_form(self):
        group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug2',
            description='Тестовое описание 2'
        )
        post_create = Post.objects.count()
        form_data = {
            'text': 'Пост изменён',
            'group': group_2.id,
        }
        response = self.authorized_client.post(reverse(
            'posts:post_edit', kwargs={'post_id': PostFormTests.post.pk}),
            data=form_data,
            follow=True
        )
        edited_post = Post.objects.latest('pk')

        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': PostFormTests.post.pk})
        )
        self.assertEqual(Post.objects.count(), post_create)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group_id, form_data['group'])

    def test_guest_post_edit(self):
        group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug2',
            description='Тестовое описание 2'
        )

        form_data = {
            'text': 'Текст от анонима',
            'group': group_2.id,
        }

        self.guest_client.post(
            reverse('posts:post_edit', kwargs={"post_id": self.post.pk}),
            data=form_data,
            follow=True
        )

        self.assertNotEqual(self.post.text, form_data['text'])
        self.assertNotEqual(self.post.group, form_data['group'])

    def test_authorized_client_noauthor_post_edit(self):
        group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug2',
            description='Тестовое описание 2'
        )
        form_data = {
            'text': 'Текст от не автора',
            'group': group_2.id,
        }

        self.authorized_client_noauthor.post(
            reverse(
                'posts:post_edit', kwargs={"post_id": self.post.pk}
            ),
            data=form_data,
            follow=True
        )

        self.assertNotEqual(self.post.text, form_data['text'])
        self.assertNotEqual(self.post.group, form_data['group'])
