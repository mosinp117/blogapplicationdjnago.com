from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .form import *

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('register_view')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('register_view')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "You have successfully registered! Please log in.")
        return redirect('login_view')

    return render(request, 'register.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "You have successfully signed in!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login_view')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login_view')


def home(request):
    context = {'blogs': BlogModel.objects.all()}
    return render(request, 'home.html', context)


def blog_detail(request, slug):
    context = {}
    try:
        blog_obj = BlogModel.objects.filter(slug=slug).first()
        context['blog_obj'] = blog_obj
    except Exception as e:
        print(e)
    return render(request, 'blog_detail.html', context)


def see_blog(request):
    context = {}

    try:
        blog_objs = BlogModel.objects.filter(user=request.user)
        context['blog_objs'] = blog_objs
    except Exception as e:
        print(e)

    return render(request, 'see_blog.html', context)


def add_blog(request):
    context = {'form': BlogForm}
    try:
        if request.method == 'POST':
            form = BlogForm(request.POST)
            image = request.FILES.get('image', '')
            title = request.POST.get('title')
            user = request.user

            if form.is_valid():
                content = form.cleaned_data['content']

            blog_obj = BlogModel.objects.create(
                user=user, title=title,
                content=content, image=image
            )
            messages.success(request, "Blog added successfully!")
            return redirect('/add-blog/')
    except Exception as e:
        print(e)

    return render(request, 'add_blog.html', context)


def blog_update(request, slug):
    context = {}
    try:
        blog_obj = BlogModel.objects.get(slug=slug)

        if blog_obj.user != request.user:
            messages.error(request, "You are not authorized to edit this blog.")
            return redirect('/')

        initial_dict = {'content': blog_obj.content}
        form = BlogForm(initial=initial_dict)
        if request.method == 'POST':
            form = BlogForm(request.POST)
            image = request.FILES['image']
            title = request.POST.get('title')
            user = request.user

            if form.is_valid():
                content = form.cleaned_data['content']

            blog_obj = BlogModel.objects.create(
                user=user, title=title,
                content=content, image=image
            )
            messages.success(request, "Blog updated successfully!")
            return redirect('/see-blog/')

        context['blog_obj'] = blog_obj
        context['form'] = form
    except Exception as e:
        print(e)

    return render(request, 'update_blog.html', context)


def blog_delete(request, id):
    try:
        blog_obj = BlogModel.objects.get(id=id)

        if blog_obj.user == request.user:
            blog_obj.delete()
            messages.success(request, "Blog deleted successfully!")
        else:
            messages.error(request, "You are not authorized to delete this blog.")

    except Exception as e:
        print(e)

    return redirect('/see-blog/')


def verify(request, token):
    try:
        profile_obj = Profile.objects.filter(token=token).first()

        if profile_obj:
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, "Your email has been verified! You can now log in.")
        else:
            messages.error(request, "Invalid or expired verification link.")

        return redirect('/login/')

    except Exception as e:
        print(e)

    return redirect('/')
