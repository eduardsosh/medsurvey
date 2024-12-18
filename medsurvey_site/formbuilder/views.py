from django.shortcuts import render , redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpRequest, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .forms import FormCreationForm, FormEditForm, QuestionForm, EditQuestionForm
from .models import Form, Question, UserForms
from django.urls import reverse
from django.contrib import messages
from django.db.models import Max
from django.utils.translation import gettext_lazy as _


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
            return redirect('edit_questions', form_id=new_form.id)
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

    return render(request, 'formbuilder/edit_form_data.html', {'form': form, 'form_instance': form_instance})

def delete_form(request, form_id):
    if request.method == 'POST':
        form = get_object_or_404(Form, id=form_id)
        if form.author == request.user:
            form.delete()
        else:
            return HttpResponseForbidden("You do not have permission to delete this form.")

        return redirect(reverse('view_created_forms'))

@login_required
def edit_questions(request, form_id):
    # Get the form instance to which these questions belong
    form_instance = get_object_or_404(Form, id=form_id)

    # Get all questions associated with this form, ordered by 'order' field
    questions = Question.objects.filter(form=form_instance).order_by('order')

    if request.method == 'POST':
        # Handle form submission for adding a new Question
        new_question_form = QuestionForm(request.POST, form=form_instance)
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

"""
def edit_question_data(request, question_id):
    question_instance = get_object_or_404(Question)
    parent_form = question_instance.form
    if request.method == 'POST':
        # If data is submitted, bind it to the existing instance
        form = EditQuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('edit_questions', form_id=parent_form.id)
    else:
        # If GET, display form populated with the current data
        form = FormEditForm(instance=form_instance)
"""
@login_required
def delete_question(request, question_id):
    question_to_delete = get_object_or_404(Question, id=question_id)
    current_form = question_to_delete.form

    subsequent_questions = Question.objects.filter(order__gt=question_to_delete.order).order_by('order')

    # Step 3: Update the order of subsequent questions
    for question in subsequent_questions:
        question.order -= 1
        question.save()

    # Step 4: Delete the question
    question_to_delete.delete()

    # Redirect back to the questions list or some other page
    return redirect('edit_questions', form_id=current_form.id)


def move_question_up(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    form = question.form
    
    if question.order <= 1:
        messages.warning(request, _("This question is already at the top."))
        return redirect('edit_questions', form_id=form.id)
    
    # Find the question with the immediate lower order
    try:
        above_question = Question.objects.get(form=form, order=question.order - 1)
    except Question.DoesNotExist:
        messages.error(request, _("Cannot move the question up."))
        return redirect('edit_questions', form_id=form.id)
    
    # Swap the order values
    question.order, above_question.order = above_question.order, question.order
    question.save()
    above_question.save()
    
    messages.success(request, _("Question moved up successfully."))
    return redirect('edit_questions', form_id=form.id)

def move_question_down(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    form = question.form
    
    # Determine the maximum order value within the form
    max_order = Question.objects.filter(form=form).aggregate(max_order=Max('order'))['max_order']
    if question.order >= max_order:
        messages.warning(request, _("This question is already at the bottom."))
        return redirect('edit_questions', form_id=form.id)
    
    # Find the question with the immediate higher order
    try:
        below_question = Question.objects.get(form=form, order=question.order + 1)
    except Question.DoesNotExist:
        messages.error(request, _("Cannot move the question down."))
        return redirect('edit_questions', form_id=form.id)
    
    # Swap the order values
    question.order, below_question.order = below_question.order, question.order
    question.save()
    below_question.save()
    
    messages.success(request, _("Question moved down successfully."))
    return redirect('edit_questions', form_id=form.id)