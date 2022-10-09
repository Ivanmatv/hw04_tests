from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        lable = {
            'Названия'
            'text': 'Текст поста',
            'group': 'Группа',
        }
        help_texts = {
            'Текс подсказки'
            'group': 'Выберите группу',
            'text': 'Введите сообщение',
        }
