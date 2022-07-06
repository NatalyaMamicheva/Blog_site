from django.contrib import admin
from .models import Article, ArticleCategory, Comment
from authapp.models import User

admin.site.register(Article)
admin.site.register(ArticleCategory)
admin.site.register(Comment)
admin.site.register(User)