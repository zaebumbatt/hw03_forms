from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator

from .models import Post, Group, User
from .forms import PostForm

import datetime


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.text = form.cleaned_data['text']
            post.group = form.cleaned_data['group']
            post.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, "new.html", {"form": form})


def profile(request, username):
    user = User.objects.get(username=username)
    fullname = user.get_full_name()
    post_list = Post.objects.filter(author=user)
    posts_count = Post.objects.filter(author=user).count()
    paginator = Paginator(post_list, 1)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {'username': username, 'fullname': fullname, 'posts_count': posts_count,
                                            'page': page, 'paginator': paginator})


def post_view(request, username, post_id):
    user = User.objects.get(username=username)
    fullname = user.get_full_name()
    post = Post.objects.get(id=post_id)
    posts_count = Post.objects.filter(author=user).count()
    return render(request, 'post.html', {'username': username, 'fullname': fullname, 'posts_count': posts_count,
                                         'post': post})


@login_required
def post_edit(request, username, post_id):
    # тут тело функции. Не забудьте проверить,
    # что текущий пользователь — это автор записи.
    # В качестве шаблона страницы редактирования укажите шаблон создания новой записи
    # который вы создали раньше (вы могли назвать шаблон иначе)
    user = User.objects.get(username=username)
    post = Post.objects.get(id=post_id)
    if post.author == request.user:
        if request.method == "POST":
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = user
                post.id = post_id
                post.pub_date = datetime.datetime.now()
                post.text = form.cleaned_data['text']
                post.group = form.cleaned_data['group']
                post.save()
                return redirect('profile', username=user)
        else:
            form = PostForm(initial={'group': post.group, 'text': post.text})
    else:
        return redirect('index')
    return render(request, 'new.html', {'form': form})
