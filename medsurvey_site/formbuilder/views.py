from django.shortcuts import render , redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.contrib.auth.decorators import login_required
from .forms import FormCreationForm, FormEditForm, QuestionForm
from .models import Form, Question
from django.urls import reverse
from django.contrib import messages


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

@login_required
def edit_questions(request, form_id):
    # Get the form instance to which these questions belong
    form_instance = get_object_or_404(Form, id=form_id)

    # Get all questions associated with this form, ordered by 'order' field
    questions = Question.objects.filter(form=form_instance).order_by('order')

    if request.method == 'POST':
        # Handle form submission for adding a new Question
        new_question_form = QuestionForm(request.POST)
        if new_question_form.is_valid():
            # Create the question but do not save to DB yet
            new_question = new_question_form.save(commit=False)
            # Associate the question with the current form
            new_question.form = form_instance
            new_question.save()
            messages.success(request, "Question added successfully.")
            return redirect(reverse('edit_questions', args=[form_id]))
        else:
            messages.error(request, "There was an error adding the question. Check the form fields.")
    else:
        new_question_form = QuestionForm()

    context = {
        'form': form_instance,
        'questions': questions,
        'question_form': new_question_form
    }
    return render(request, 'formbuilder/edit_questions.html', context)
