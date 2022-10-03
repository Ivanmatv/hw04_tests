from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        verbose_name = 'Формы полей'
        fields = ('text', 'group')
        lable = {
            'text': 'Текст поста',
            'group': 'Группа',
        }
        help_texts = {
            'group': 'Выберите группу',
            'text': 'Введите сообщение',
        }
