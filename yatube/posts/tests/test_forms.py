from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Ivan')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            id=30,
        )

    def setUp(self):
        self.authorized_client = Client()

    def test_create_post(self):
        post_create = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'slug': 'test-slug',
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), post_create)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Post.objects.filter(
            author=self.user,
            text='Тестовый пост',
            group=self.group,
            id=30,
        ).exists())

    def test_post_edit_form(self):
        post_create = Post.objects.count()
        form_data = {
            'text': 'Пост изменён',
            'slug': 'test-slug',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, '/auth/login/?next=/posts/30/edit/'
        )
        self.assertEqual(Post.objects.count(), post_create)
