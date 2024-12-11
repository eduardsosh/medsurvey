from django.shortcuts import render , redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.utils import timezone
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _
from .forms import CustomUserCreationForm, CustomUserEditForm
from .models import UserAdditionalData, User

# Create your views here.

def index(request):
    return render(request, 'home.html')
    

@login_required
def log_out(request):
    logout(request)
    return redirect('/')

@csrf_protect
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('Registration successful.'))
            return redirect('/')
        else:
            messages.error(request, _('Registration failed. Please correct the errors below.'))
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'auth/register.html', {'form': form})

@login_required
def view_user_data(request):
    additional_data_object = UserAdditionalData.objects.get(base_user=request.user)
    context = {
        'user' : request.user,
        'additional_data': additional_data_object
    }
    return render(request, 'profile.html', context)

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to profile page after saving
    else:
        form = CustomUserEditForm(instance=user)

    return render(request, 'edit_profile.html', {'form': form})