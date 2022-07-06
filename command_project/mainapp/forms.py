from django import forms
from .models import Article, Comment


class CreateArticleForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput(), required=False)

    class Meta:
        model = Article
        fields = ['title', 'category', 'image', 'article_text', 'is_published']
        labels = {
            'title': 'Введите заголовок',
            'article_text': "Ваши мысли тут",
            'is_published': 'Опубликовать сразу?'
        }

    def __init__(self, *args, **kwargs):
        super(CreateArticleForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': 'Введите комментарий'}

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
