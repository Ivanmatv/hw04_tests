from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required


from .forms import PostForm
from .models import Post, Group, User

NUM_PUB: int = 10


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, NUM_PUB)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, NUM_PUB)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=author)
    post_count = user_posts.count()
    paginator = Paginator(user_posts, NUM_PUB)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = f'Профаил пользователя {username}'
    context = {
        'title': title,
        'post_count': post_count,
        'author': author,
        'page_obj': page_obj,
        'username': username,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    author_post = post.author
    post_count = Post.objects.filter(author=author_post).count()
    title = f'Пост {post.text[0:30]}'
    context = {
        'post': post,
        'post_count': post_count,
        'title': title,
        'author_post': author_post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect(f'/profile/{form.author.username}/')
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post.pk)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.pk)
    return render(request, 'posts/create_post.html', {'form': form})
