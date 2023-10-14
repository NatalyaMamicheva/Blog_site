from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView
from datetime import datetime

from authapp.models import User
from mainapp.models import Article, Comment
from .models import BannedObjects, Report


class ModeratorPage(ListView):
    model = BannedObjects
    ordering = '-banned_on'
    paginate_by = 100
    template_name = 'moderation/mod_page.html'
    context_object_name = 'banned_objects'

    extra_context = {
        'title1': "Список заблокированных вами объектов:",
        'title2': "Статьи",
        'title3': "Комментарии",
        'title4': "Пользователи"
    }

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['article_list'] = BannedObjects.objects.all().filter(
            banned_comment=None, banned_by=self.request.user)
        context['comment_list'] = BannedObjects.objects.all().filter(
            banned_article=None, banned_by=self.request.user)
        context['reported_articles'] = Report.objects.all().filter(
            reported_comment=None, is_active=True).order_by('-reported_on')
        context['reported_comments'] = Report.objects.all().filter(
            reported_article=None, is_active=True).order_by('-reported_on')
        return context


class Ban(View):
    def post(self, request, model, pk, *args, **kwargs):
        models = {
            'article': Article,
            'comment': Comment,
            'user': User
        }

        if model == 'user':
            if request.user.is_staff:
                _object = User.objects.get(pk=pk)
                _object.blocked_time = datetime.now()
                _object.save()

        elif model is not 'user':
            _object = models[model].objects.get(pk=pk)
            object_author = _object.author

            if not _object.is_banned and request.user.is_staff:

                _object.is_banned = True
                _object.save()

                object_author.blocked_time = datetime.now()
                object_author.save()

                if model == 'article':
                    banned_article = BannedObjects.create(object_pk=_object,
                                                          user=request.user)
                    banned_article.save()

                elif model == 'comment':
                    banned_comment = BannedObjects.create(object_pk=_object,
                                                          user=request.user)
                    banned_comment.save()

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


class Unban(View):
    def post(self, request, model, pk, *args, **kwargs):
        if model == 'user':
            if request.user.is_staff:
                _object = User.objects.get(id=pk)
                _object.blocked_time = None
                _object.save()

        elif model is not 'user':
            if request.user.is_staff:
                _object = BannedObjects.objects.get(id=pk)
                if _object.banned_article is not None:
                    article = Article.objects.get(id=_object.banned_article_id)
                    article.is_banned = False
                    article.save()
                elif _object.banned_comment is not None:
                    comment = Comment.objects.get(id=_object.banned_comment_id)
                    comment.is_banned = False
                    comment.save()
                _object.delete()

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


def mute_report(request, pk):
    if request.user.is_staff:
        object = Report.objects.get(id=pk)
        object.is_active = False
        object.save()
    return HttpResponseRedirect(request.path_info)


def change_moderator_status(request, pk):
    if request.user.is_superuser:
        user = User.objects.get(id=pk)
        if not user.is_staff:
            user.is_staff = True
            user.save()
            return redirect('/')
        elif user.is_staff:
            user.is_staff = False
            user.save()
            return redirect('/')
    else:
        return HttpResponseRedirect(request.path_info)
