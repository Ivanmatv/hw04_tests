from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from posts.forms import PostForm


User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Ivan')
        Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=Group.objects.create(
                title='Тестовая группа',
                slug='test-slug',
                description='Тестовое описание',
                id=30
            )
        )
        cls.form = PostForm()

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
            text='Тестовый пост',
            slug='test-slug'
        ).exist())

    def test_post_edit_form(self):
        post_create = Post.objects.count()
        form_data = {
            'text': 'Пост изменён',
            'group': Post.group,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.group.id}'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.post.id}'}
            )
        )
        self.assertEqual(Post.objects.count(), post_create)
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            group=form_data['group'],
        ).exist())
