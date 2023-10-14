from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render

from authapp.models import User
from moderation.models import Report
from .forms import CommentForm, CreateArticleForm
from .models import ArticleCategory, Article, Comment


class AuthorTestMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user == self.get_object().author


class BanTestMixin(UserPassesTestMixin):
    def test_func(self):
        self.permission_denied_message = 'Вы забанены'
        return not self.request.user.is_banned


def get_top10_articles():
    top10_articles = Article.objects.annotate(
        cnt=Count('likes')).order_by('-cnt')[:5]
    return top10_articles


class ArticlesView(ListView):
    model = Article
    ordering = '-created_date'
    paginate_by = 5
    template_name = 'mainapp/articles.html'
    context_object_name = 'articles'
    extra_context = {
        'title': 'Habr',
        'categories': ArticleCategory.objects.all(),
        'top10_articles': get_top10_articles(),
    }

    def get_queryset(self):
        queryset = super(ArticlesView, self).get_queryset().order_by(
            '-created_date')
        queryset = queryset.filter(is_published=True, is_banned=False)
        if 'pk' in self.kwargs:
            if self.kwargs['pk'] == 0:
                return queryset
            elif self.kwargs['pk'] != 0:
                queryset = queryset.filter(category_id__pk=self.kwargs['pk'])
                return queryset
        else:
            return queryset


@method_decorator(csrf_exempt, name='dispatch')
class ArticleView(DetailView):
    model = Article
    template_name = 'mainapp/article.html'
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super(ArticleView, self).get_context_data(**kwargs)
        context['title'] = 'Habr'
        context['categories'] = ArticleCategory.objects.all()
        context['form'] = CommentForm()
        comments = self.get_comments()
        context['comments'] = comments
        context['same_articles'] = self.get_same_articles()
        return context

    def get_comments(self):
        comments = Comment.objects.filter(article__pk=self.kwargs['pk'])
        for comment in comments:
            if comment.is_banned:
                comment.text = 'Комментарий заблокирован модератором'
        return comments

    def get_same_articles(self):

        category = self.object.category
        same_articles = self.model.objects.filter(
            category=category).annotate(cnt=Count('likes'))
        return same_articles.order_by('-cnt')[:5]


@method_decorator(csrf_exempt, name='dispatch')
class ArticleCreateView(LoginRequiredMixin, BanTestMixin, CreateView):
    model = Article
    template_name = 'mainapp/create_article.html'
    form_class = CreateArticleForm
    pk = None
    login_url = '/auth/login/'

    def form_valid(self, form):
        article = form.save(commit=False)
        article.author = self.request.user
        article.save()
        self.object = article
        self.pk = article.pk
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('mainapp:article', kwargs={'pk': self.pk})


@method_decorator(csrf_exempt, name='dispatch')
class ArticleUpdateView(LoginRequiredMixin, AuthorTestMixin, UpdateView):
    model = Article
    template_name = 'mainapp/create_article.html'
    form_class = CreateArticleForm
    pk = None
    login_url = '/auth/login/'
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse_lazy('mainapp:article', kwargs={'pk': self.pk})

    def form_valid(self, form):
        self.pk = self.object.pk
        return super(ArticleUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get('pk')
        content = super(ArticleUpdateView, self).get_context_data(**kwargs)
        content['title'] = 'Редактирование статьи'
        content['article'] = Article.objects.get(pk=pk)
        return content

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return Article.objects.get(pk=pk)


@method_decorator(csrf_exempt, name='dispatch')
class ArticleDeleteView(LoginRequiredMixin, AuthorTestMixin, DeleteView):
    model = Article
    login_url = '/auth/login/'
    success_url = reverse_lazy('mainapp:articles')

    def form_valid(self, form):
        self.object = self.get_object()
        if self.object.is_published:
            self.object.is_published = False
        else:
            self.object.is_published = True
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())


@method_decorator(csrf_exempt, name='dispatch')
class ArticlePublishView(LoginRequiredMixin, AuthorTestMixin, UpdateView):
    model = Article
    login_url = '/auth/login/'
    success_url = reverse_lazy('mainapp:articles')

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.is_published = True
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())


def about_us(request):
    title = 'о нас'
    content = {'title': title}

    return render(request, 'mainapp/about_us.html', content)


@method_decorator(csrf_exempt, name='dispatch')
class CommentView(LoginRequiredMixin, BanTestMixin, View):
    login_url = '/auth/login/'
    permission_denied_message = 'вы не авторизованны'

    def post(self, request, pk, *args, **kwargs):
        form = CommentForm(request.POST)
        article = Article.objects.get(pk=pk)

        if form.is_valid():
            text = form.cleaned_data['text']
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.article = article
            new_comment.save()

            comments = Comment.objects.filter(
                article=article).order_by('-created_at')
            context = {
                'article': article,
                'form': form,
                'comments': comments,
            }
            if '@moderator' in text:
                report = Report.create(object_pk=article, user=request.user)
                report.save()
        return HttpResponseRedirect(reverse('mainapp:article', kwargs={'pk': article.pk}))


@method_decorator(csrf_exempt, name='dispatch')
class CommentReplyView(LoginRequiredMixin, BanTestMixin, View):
    def post(self, request, article_pk, pk, *args, **kwargs):
        article = Article.objects.get(pk=article_pk)
        parent_comment = Comment.objects.get(pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.article = article
            new_comment.parent = parent_comment
            new_comment.save()
            if '@moderator' in text:
                report = Report.create(
                    object_pk=parent_comment, user=request.user)
                report.save()

        comments = Comment.objects.filter(
            article=article).order_by('-created_at')
        context = {
            'article': article,
            'form': form,
            'comments': comments,
        }
        return HttpResponseRedirect(reverse('mainapp:article', kwargs={'pk': article_pk}))


@method_decorator(csrf_exempt, name='dispatch')
class LikeSwitcher(LoginRequiredMixin, BanTestMixin, View):
    login_url = '/auth/login/'
    permission_denied_message = 'вы не авторизованны'

    def handle_no_permission(self):
        self.request.path = self.request.META['HTTP_REFERER'].replace(
            self.request.META['HTTP_ORIGIN'], '')
        if self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            try:

                _handle_no_permission = super(
                    LikeSwitcher, self).handle_no_permission()
                if _handle_no_permission.status_code == 302:
                    return JsonResponse({'url': _handle_no_permission.url}, status=302)
            except PermissionDenied:
                return JsonResponse({"error": self.permission_denied_message}, status=403)
        return super(LikeSwitcher, self).handle_no_permission()

    def post(self, request, model, pk, *args, **kwargs):
        models = {
            Article.__name__: Article,
            Comment.__name__: Comment,
            User.__name__: User,
        }
        is_liked = False
        model_to_liked = models[model].objects.get(pk=pk)
        for like in model_to_liked.likes.all():
            if like == request.user:
                is_liked = True
                break
        if is_liked:
            model_to_liked.likes.remove(request.user)
        else:
            model_to_liked.likes.add(request.user)
        next = request.POST.get('next', '/')
        if self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({"likes_count": model_to_liked.likes.count()}, status=200)

        else:
            return HttpResponseRedirect(next)


def help(request):
    title = 'Помощь'
    content = {'title': title}

    return render(request, 'mainapp/help.html', content)
