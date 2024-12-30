from django.shortcuts import render , redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpRequest, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .forms import FormCreationForm, FormEditForm, QuestionForm, EditQuestionForm, AddParticipantForm
from .models import Form, Question, UserForms, Submission, Answer
from base.models import User, UserAdditionalData
from django.urls import reverse
from django.contrib import messages
from django.db.models import Max
from django.utils.translation import gettext_lazy as _
from .decorators import examiner_required


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

@examiner_required
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

@examiner_required
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

@login_required
def view_my_assigned_forms(request):
    user = request.user
    if hasattr(request.user, 'examiner'):
        messages.warning(request, _("Examiners can not fill out forms"))
        return redirect('/')
    
    my_forms = Form.objects.filter(userforms__user=user)
    
    context = {
        'forms': my_forms
    }
    
    return render(request, "formbuilder/view_my_assigned_forms.html", context=context)
    


@login_required
@examiner_required
def view_participants(request, form_id):
    """
    View to let form author to view form's participants.\n
    Also possibility to add users to a form by their personal code.
    """
    form_instance = Form.objects.get(id=form_id)
    assigned_users = User.objects.filter(userforms__form=form_instance)

    if request.method == 'POST':
        form = AddParticipantForm(request.POST)
        if form.is_valid():
            personal_code = form.cleaned_data['personal_code']
            
            try:
                additional_data = UserAdditionalData.objects.get(personal_code=personal_code)
                user_to_add = additional_data.base_user

                already_participant = UserForms.objects.filter(user=user_to_add, form=form_instance).exists()

                if already_participant:
                    messages.warning(request, _("User is already a participant in this form."))
                else:
                    UserForms.objects.create(user=user_to_add, form=form_instance)
                    messages.success(request, _("Participant added successfully!"))
                
                return redirect('view_participants', form_id=form_instance.id)
            
            except UserAdditionalData.DoesNotExist:
                messages.error(request, _("No user found with the given personal code."))
    else:
        form = AddParticipantForm()
    
    context = {
        'participants' : assigned_users,
        'add_participant_form' : form,
    }
    return(render(request, 'formbuilder/view_participants.html', context=context))



@login_required
def fill_form_view(request, form_id):
    # 1) Get the form
    form_obj = get_object_or_404(Form, id=form_id)

    # (Optional) Check if the user is allowed to fill out this form
    # For example, if you only want users who have a record in UserForms:
    if not UserForms.objects.filter(user=request.user, form=form_obj).exists():
        messages.error(request, "You are not a participant in this form.")
        return redirect("home")  # or wherever you want to redirect

    # 2) Get all the questions for this form, ordered by 'order' if desired
    questions = Question.objects.filter(form=form_obj).order_by('order')

    if request.method == "POST":
        # 3) Create a new Submission object for this user
        submission = Submission.objects.create(
            form=form_obj,
            user=request.user
        )

        # 4) For each question, read the user’s answer from POST data
        for question in questions:
            field_name = f"question_{question.id}"

            # Because of multiple choice or single choice, the user input might differ
            # We'll handle each question type separately or with one approach
            user_answer = ""

            if question.type == Question.QuestionType.TEXT_FIELD:
                # Single line text
                user_answer = request.POST.get(field_name, "")

            elif question.type == Question.QuestionType.TEXT_AREA:
                # Multi-line text
                user_answer = request.POST.get(field_name, "")

            elif question.type == Question.QuestionType.CHOICE:
                # Single choice: user_answer is a single string
                # e.g., "Yes" or "No"
                user_answer = request.POST.get(field_name, "")

            elif question.type == Question.QuestionType.MCHOICE:
                # Multiple choice: user_answer is a list, e.g. ["Option1", "Option2"]
                # We'll join them into a single string, or store JSON, etc.
                user_selections = request.POST.getlist(field_name)
                user_answer = ", ".join(user_selections)

            # 5) Create an Answer record
            Answer.objects.create(
                user=request.user,
                submission=submission,
                field=question,
                answer=user_answer
            )

        messages.success(request, "Thank you! Your responses have been saved.")
        return redirect("/")  # Or somewhere else

    else:
        # 6) Render the form for the user to fill out
        return render(request, "formbuilder/fill_form.html", {
            "form_obj": form_obj,
            "questions": questions
        })

