from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .models import *

from .filters import PostFilter
from .forms import PostForm, CommentForm
from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import FormMixin


class PostsList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'posts.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'posts'
    paginate_by = 2

    # Переопределяем функцию получения списка объявлений
    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список объявлений
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        return context


class PostDetail(FormMixin, DetailView):
    # Модель всё та же, но мы хотим получать информацию по отдельному объявлению
    model = Post
    # Используем другой шаблон — post.html
    template_name = 'post.html'
    # Название объекта, в котором будет выбранное пользователем объявление
    context_object_name = 'post'

    form_class = CommentForm

    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.object.id})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.article = self.get_object()
        self.object.author = self.request.user
        self.object.save()
        return super().form_valid(form)


class PostCreate(PermissionRequiredMixin, CreateView):
    # Предоставление прав
    permission_required = 'posts.add_post'
    # Указываем нашу разработанную форму
    form_class = PostForm
    # модель объявлений
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'post_edit.html'


class PostUpdate(PermissionRequiredMixin, UpdateView):
    # Предоставление прав
    permission_required = 'posts.change_post'
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'


def image_upload_view(request):
    """Process images uploaded by users"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Get the current instance object to display in the template
            img_obj = form.instance
            return render(request, 'post.html', {'form': form, 'img_obj': img_obj})
    else:
        form = PostForm()
    return render(request, 'post.html', {'form': form})







