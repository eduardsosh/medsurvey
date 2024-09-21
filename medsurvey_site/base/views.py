from django.shortcuts import render , redirect
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
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('Registration successful.'))
            return redirect('/')
        else:
            messages.error(request, _('Registration failed. Please correct the errors below.'))
    else:
        form = UserCreationForm()
    
    return render(request, 'auth/register.html', {'form': form})