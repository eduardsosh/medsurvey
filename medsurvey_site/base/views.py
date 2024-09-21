from django.shortcuts import render , redirect
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.utils import timezone
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage

# Create your views here.

def index(request):
    return render(request, 'home.html')
    

@login_required
def log_out(request):
    logout(request)
    return redirect('/')