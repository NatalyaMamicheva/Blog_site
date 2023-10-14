from django.urls import path

from searchapp.views import SearchArticleList

app_name = 'search'

urlpatterns = [
    path('search/articles', SearchArticleList.as_view(), name='search_article_results'),
]