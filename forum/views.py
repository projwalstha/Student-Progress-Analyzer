from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from forum.models import Forum, thread, Post,Comment
from Anlz_app.models import User
from .forms import PostForm, ThreadForm,ForumForm,CommentForm,ContactForm
from django.core.paginator import Paginator,InvalidPage,EmptyPage
# Create your views here.
def index(request):
    forums = Forum.objects.order_by('-created')
    forums = make_paginator(request,forums,20)
    context_dict = {'forums' : forums}
    return render (request, 'forum/index.html',context_dict)

def forum(request, pk):
    """
    Listing all threads in a forum with pk=pk.
    """
    forum = get_object_or_404(Forum, pk=pk)
    threads = thread.objects.filter(forum=pk).order_by('-created')
    threads =  make_paginator(request, threads, 20)
    context_dict = {'threads': threads, 'forum': forum}
    return render(request, 'forum/forum.html', context_dict)

def view_thread(request, pk):
    """
    List posts in this thread.
    """
    # get_object_or_404 ?? get_list_or_404?? Or just no error handling at all here???
    try:
        posts = Post.objects.filter(thread=pk).order_by('created')
    except:
        raise Http404

    posts = make_paginator(request, posts, 15)
    threads = get_object_or_404(thread, pk=pk)

    # Get all comments associated with posts in this thread.
    comments = [com for com in Comment.objects.all() if com.post.thread.pk == threads.pk]
    context_dict = {'posts': posts, 'thread': threads, 'comments': comments}
    return render(request, 'forum/thread.html', context_dict)


@login_required
def add_thread(request,pk):
    forum = get_object_or_404(Forum,pk=pk)
    if request.method == 'POST':
        threads = thread(forum = forum)
        form = ThreadForm(request.POST,instance=threads)
        if form.is_valid():
            threads = form.save(commit=False)
            # # user =request.User.get_username()
            threads.creator = request.user
            # print(request.User)
            threads.save()
            return redirect('forum:forum',pk=pk)
    else:
            form = ThreadForm()
    context_dict = {'form': form, 'forum':forum}
    return render(request,'forum/add_thread.html',context_dict)


@login_required
def add_post(request,pk):
    threads =get_object_or_404(thread,pk=pk)
    if request.method == 'POST':
        post = Post(thread=threads)
        form = PostForm(request.POST,instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.creator = request.user
            post.save()
            # profile = User.objects.get(username=post.creator)
            # profile.posts = profile.posts + 1
            # profile.save()
            return redirect('forum:thread',pk=pk)
        else:
            print(form.errors)
    else:
        form = PostForm()
    context_dict = {'form': form, 'thread': threads}
    return render(request, 'forum/add_post.html',context_dict)



def make_paginator(request, items, number):
    '''
    Make a paginator of number items of type 'item'
    '''
    paginator = Paginator(items, number)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        items = paginator.page(page)
    except(InvalidPage, EmptyPage):
        items = paginator.page(paginator.num_pages)

    return items

@login_required
def create_forum(request):
    if request.method == 'POST':
        form = ForumForm(request.POST)
        if form.is_valid():
            forum = form.save(commit=False)
            forum.creator = request.user
            forum.save()
            return redirect('forum:index')
        else:
            print(form.errors)
    else:
        form = ForumForm()
    return render(request,'forum/create_forum.html',{'forum':form})

@login_required
def comment(request,pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        comment = Comment(post=post)
        comment_form = CommentForm(request.POST, instance=comment)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.creator = request.user
            comment.save()
            return redirect('forum:thread',pk=post.thread_id)
    else:
            comment_form =CommentForm()
            context_dict = {'post':post ,'form':comment_form }
            return render(request,'forum/add_comment.html',context_dict)

@login_required
def edit_forum(request,pk):
    forum = get_object_or_404(Forum , pk=pk)
    if request.method == 'POST':
        form = ForumForm(request.POST, instance=forum)
        if form.is_valid():
            forum = form.save(commit=False)
            forum.creator = request.user
            forum.save()
            return redirect('forum:forum',pk=pk)
    else:
        form = ForumForm(instance=forum)
    context_dict = {'form':form,'forum':forum}
    return render(request,'forum/edit_forum.html',context_dict)


def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            messages.success(request, 'Your suggestion is submitted')
            return redirect('contact_us.html')
    else:
        form = ContactForm()
        return render(request,'contact_us.html',{'form':form})
