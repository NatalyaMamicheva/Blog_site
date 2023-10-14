from django.shortcuts import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
# from django_registration.backends.activation.views import RegistrationView
from django.contrib.auth.views import LoginView

from .models import User
from .forms import UserRegisterForm, UserProfileForm, UserLoginForm
from mainapp.models import Article, Comment


# CRUD - Create Read Update Delete
class UserDetailView(DetailView):
    model = User
    template_name = 'authapp/users-detail.html'

    def dispatch(self, request, *args, **kwargs):
        return super(UserDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        content = super().get_context_data(**kwargs)
        content['title'] = 'Профиль'
        content['user'] = self.request.user
        content['user_detail'] = self.get_object()
        content['rating'] = self.get_rating()
        content['published_articles'] = Article.objects.filter(
            author__id=self.get_object().id, is_published=True)
        content['draft_articles'] = Article.objects.filter(
            author__id=self.get_object().id, is_published=False)
        content['draftnull_articles'] = Article.objects.filter(
            author__id=self.get_object().id, is_published=None)

        if self.request.user.is_authenticated:
            content['user_check'] = User.objects.get(
                username=self.request.user)
            if content['user_check'].id == self.get_object().id:
                content['edit_visible'] = 'True'
            else:
                content['edit_visible'] = 'False'
        else:
            content['edit_visible'] = 'False'
        return content

    def get_rating(self):
        articles_likes = Article.objects.filter(
            author__id=self.get_object().id).count()
        comments_likes = Comment.objects.filter(
            author__id=self.get_object().id).count()
        rating = articles_likes + comments_likes
        return rating


class UserCreateView(CreateView):
    model = User
    template_name = 'authapp/users-create.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('mainapp:articles')


    def dispatch(self, request, *args, **kwargs):
        return super(UserCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        content = super().get_context_data(**kwargs)
        content['title'] = 'Регистрация'
        next = ''
        if self.request.GET:
            next = self.request.GET['next']
        if next != '':
            content['next'] = next
        return content



class UserUpdateView(UpdateView):
    model = User
    template_name = 'authapp/users-update-delete.html'
    form_class = UserProfileForm

    def get_context_data(self, **kwargs):
        content = super(UserUpdateView, self).get_context_data(**kwargs)
        content['title'] = 'Редактирование пользователя'
        content['user'] = User.objects.get(username=self.request.user)
        return content

    def get_object(self, queryset=None):
        return User.objects.get(username=self.request.user)

    def get_success_url(self):
        profile_id = User.objects.get(username=self.request.user).id
        return reverse_lazy('auth:users_detail', kwargs={'pk': profile_id})


class UserDeleteView(DeleteView):
    model = User
    template_name = 'authapp/users-update-delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = 0
        self.object.save()

    def get_object(self, queryset=None):
        return User.objects.get(username=self.request.user)

    def get_success_url(self):
        return reverse_lazy('auth:login')

class UserLoginView(LoginView):
    template_name = 'authapp/login.html'
    redirect_field_name = 'next'
    authentication_form = UserLoginForm
