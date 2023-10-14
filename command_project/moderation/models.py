from datetime import datetime
from django.db import models

from mainapp.models import Article, Comment
from authapp.models import User


class BannedObjects(models.Model):
    banned_by = models.ForeignKey(User, on_delete=models.CASCADE)
    banned_on = models.DateTimeField(blank=True, null=True)
    banned_article = models.ForeignKey(Article, on_delete=models.CASCADE,
                                       blank=True, null=True)
    banned_comment = models.ForeignKey(Comment, on_delete=models.CASCADE,
                                       blank=True, null=True)

    @classmethod
    def create(cls, object_pk, user):
        object_category = object_pk.__class__
        ban = cls(banned_by=user,
                  banned_on=datetime.now())
        if object_category == Article:
            ban.banned_article = object_pk
            return ban
        elif object_category == Comment:
            ban.banned_comment = object_pk
            return ban

    def get_object_name(self):
        if self.banned_article is not None:
            object_name = self.banned_article.title
            return object_name
        elif self.banned_comment is not None:
            object_name = self.banned_comment.title
            return object_name

    def get_object_author(self):
        if self.banned_article is not None:
            author = self.banned_article.author
            return author
        elif self.banned_comment is not None:
            author = self.banned_comment.author
            return author


class Report(models.Model):
    reported_article = models.ForeignKey(Article, on_delete=models.CASCADE,
                                         blank=True, null=True)
    reported_comment = models.ForeignKey(Comment, on_delete=models.CASCADE,
                                         blank=True, null=True)
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reported_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    @classmethod
    def create(cls, object_pk, user):
        object_category = object_pk.__class__
        report = cls(reported_by=user,
                     reported_on=datetime.now())
        if object_category == Article:
            report.reported_article = object_pk
            return report
        if object_category == Comment:
            report.reported_comment = object_pk
            return report

    def get_commented_article(self):
        if self.reported_comment is not None:
            commented_article = Article.objects.get(
                id=self.reported_comment.article_id)
            return commented_article









