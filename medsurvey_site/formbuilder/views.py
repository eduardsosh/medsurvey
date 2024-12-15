from django.shortcuts import render , redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.contrib.auth.decorators import login_required
from .forms import FormCreationForm, FormEditForm
from .models import Form


def index(request):
    return render(request, 'home.html')
    

@login_required
def create_form(request):
    if not hasattr(request.user, 'examiner'):
        return redirect('/')

    if request.method == 'POST':
        form = FormCreationForm(request.POST)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.author = request.user
            new_form.save()
            return redirect('/')
    else:
        form = FormCreationForm()

    return render(request, 'formbuilder/create_form.html', {'form': form})

@login_required
def view_created_forms(request):
    # Filter forms by the logged-in user
    user_forms = Form.objects.filter(author=request.user).order_by('-creation_date_time')
    return render(request, 'formbuilder/my_created_forms.html', {'forms': user_forms})


@login_required
def edit_form(request, pk):
    # Fetch the form instance that matches the pk and is authored by the current user
    form_instance = get_object_or_404(Form, pk=pk, author=request.user)

    if request.method == 'POST':
        # If data is submitted, bind it to the existing instance
        form = FormEditForm(request.POST, instance=form_instance)
        if form.is_valid():
            form.save()
            # Redirect to the list of user's forms (you must have 'my_forms' named URL configured)
            user_forms = Form.objects.filter(author=request.user).order_by('-creation_date_time')
            return render(request, 'formbuilder/my_created_forms.html', {'forms': user_forms})
    else:
        # If GET, display form populated with the current data
        form = FormEditForm(instance=form_instance)

    return render(request, 'formbuilder/edit_form_data.html', {'form': form})
