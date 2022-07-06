from django.db.models import Q
from django.views.generic import ListView
from mainapp.models import Article, ArticleCategory


class SearchArticleList(ListView):
    model = Article
    paginate_by = 100
    template_name = 'searchapp/search_article_results.html'
    extra_context = {
        'title': 'Habr',
        'categories': ArticleCategory.objects.all(),
    }

    def get_context_data(self, **kwargs):
        context = super(SearchArticleList, self).get_context_data(**kwargs)

        q = self.request.GET.get('search')
        sort = self.request.GET.getlist('sort')
        context['search_name'] = q
        if q:

            queryset = Article.objects.filter(Q(title__icontains=q.capitalize()) | Q(title__icontains=q.lower())
                                        | Q(title__icontains=q.upper()) | Q(article_text__icontains=q.capitalize())
                                        | Q(article_text__icontains=q.lower()) | Q(article_text__icontains=q.upper()))

            if sort:
                queryset = queryset.order_by(*sort)
            else:
                queryset.order_by('-likes')

            context['articles'] = queryset

        return context


