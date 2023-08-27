from django.shortcuts import render
from .models import User
from django.shortcuts import render, redirect
import requests
import json
from .forms import *
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
import uuid
from .filters import *
from django.urls import reverse
from django.core.paginator import Paginator


# DECORATORS

def login_success(request):
    user = request.user
    if user.is_authenticated:
        if user.is_admin:
            return redirect("list_report")
    return redirect("home")

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin:
            return view_func(request, *args, **kwargs)
        else:
            return render(request, '403.html', status=403)
    return wrapper

def page_not_found(request, exception):
    return render(request, '404.html', status=404)

@login_required(login_url='login')
@admin_required
def homeView(request):
    context = {
        'content': 'content', 
    }
    return render(request, 'home.html', context)

# USERS

@login_required(login_url='login')
@admin_required
def refreshUsersList(request):
    
    usernames = User.objects.values_list('username', flat=True)
    
    API_Users = 'https://api.ldap.groupe-hasnaoui.com/get/users?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE'
    GROUP_Users = 'https://api.ldap.groupe-hasnaoui.com/get/users/group/PUMA-PRD?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE'

    response = requests.get(API_Users)
    response_ = requests.get(GROUP_Users)

    if response.status_code == 200 and response_.status_code == 200:
        data = json.loads(response.content)
        group_users = json.loads(response_.content)['members']

        new_users_list = [user for user in data['users'] if user['fullname'] in group_users and user['AD2000'] not in usernames]

        for user in new_users_list:
            user = User(username= user['AD2000'], password='password', fullname=user['fullname'], is_admin=False, first_name= user['fname'], email= user['mail'], last_name = user['lname'])
            user.save()
    else:
        print('Error: could not fetch data from API')

    cache_param = str(uuid.uuid4())
    url_path = reverse('users')
    redirect_url = f'{url_path}?cache={cache_param}'

    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def editUserView(request, id):
    user = User.objects.get(id=id)
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('users')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)

    context = {'form': form, 'user_to_edit': user}

    return render(request, 'edit_user.html', context)

@login_required(login_url='login')
@admin_required
def deleteUserView(request, id):
    user = User.objects.get(id=id)
    user.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse(request.GET.get('redirect_url', 'users').strip('/'))

    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def listUsersView(request):

    users = User.objects.exclude(username='admin').order_by('id')
    filteredData = UserFilter(request.GET, queryset=users)
    users = filteredData.qs

    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'page': page, 'filtredData': filteredData,
    }
    return render(request, 'users_list.html', context)

@login_required(login_url='login')
@admin_required
def userDetailsView(request, id):
    user = User.objects.get(id=id)
    context = {
        'user_details': user,
    }
    return render(request, 'user_details.html', context)


# AUTHENTIFICATION

class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = CustomLoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse_lazy('home'))
        return super().dispatch(request, *args, **kwargs)

def logoutView(request):
    logout(request)
    return redirect('login')
