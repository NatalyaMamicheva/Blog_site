from django.core.management.base import BaseCommand

from mainapp.models import ArticleCategory, Article, Comment
from authapp.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):

        User.objects.all().delete()
        User.objects.create_superuser('admin', 'django@geekshop.local', '123', first_name='NatalyaM')
        User.objects.create_user('test', 'test@geekshop.local', '123', first_name='Natali')
        _user = User.objects.get(first_name='Natali')

        categories = ['Дизайн', 'Веб-разработка', 'Мобильная разработка', 'Маркетинг']

        ArticleCategory.objects.all().delete()
        for category in categories:
            new_category = ArticleCategory.objects.create(name=category)
            new_category.save()

        Article.objects.all().delete()
        Comment.objects.all().delete()
        for i in categories:
            for j in range(20):
                category_name = i
                _category = ArticleCategory.objects.get(name=category_name)
                new_article = Article.objects.create(author=_user,
                                                     title=f'test {i} / {j}',
                                                     article_text='СТАТЬЯ '*20,
                                                     category=_category,
                                                     is_published=True,
                                                     )
                new_article.save()
                for _ in range(5):
                    article = new_article
                    author = _user
                    text = 'КОММЕНТАРИЙ ' * 10
                    comment = Comment.objects.create(article=article,
                                                     author=author,
                                                     text=text
                                                     )
                    for _ in range(2):
                        text = 'комментарий к комментарию'
                        Comment.objects.create(article=article,
                                               author=author,
                                               text=text,
                                               parent=comment,
                                               )

