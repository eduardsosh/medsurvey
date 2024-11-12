from django.shortcuts import render , redirect
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'home.html')
    

@login_required
def create_form(request):
    # If the user belongs to examiner group then show the form creator page
    if request.user.groups.filter(name='examiner').exists():
        return render(request, 'create_form.html')
    else:
        return redirect('/')
