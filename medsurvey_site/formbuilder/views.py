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
from django.utils.timezone import now
from datetime import datetime, timedelta

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
    # If this user is an examiner, they should not fill out forms
    if hasattr(user, 'examiner'):
        messages.warning(request, _("Examiners can not fill out forms"))
        return redirect('/')
    
    assigned_forms = Form.objects.filter(userforms__user=user)

    # Build a list of dictionaries, each containing the form and info about access
    form_info_list = []
    for form in assigned_forms:
        denial_reason_or_false = deny_access_to_form(user, form.id)
        
        if denial_reason_or_false is False:
            # Means the user can fill out the form
            can_fill = True
            error_code = ""
        else:
            # Means the user cannot fill out the form; store the reason
            can_fill = False
            error_code = denial_reason_or_false
        
        form_info_list.append({
            'form': form,
            'can_fill': can_fill,
            'error_code': error_code,
        })

    # Pass this list to your template
    context = {
        'forms': form_info_list
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
        'form' : form_instance,
        'add_participant_form' : form,
    }
    return(render(request, 'formbuilder/view_participants.html', context=context))




def deny_access_to_form(user_id, form_id):
    """Check if a user can fill out a form that has periodicty"""
    form_obj = get_object_or_404(Form, id=form_id)
    next_submission_time = None
    today = now().date()

    if form_obj.end_date:
        if form_obj.end_date < today:
            return _("You cannot fill this form, it has ended!")
        
    if form_obj.start_date:
        if form_obj.start_date > today:
            return _("You cannot fill this form, it has not started yet!")

    
    if form_obj.interval is not None:
        if form_obj.interval == Form.Regularity.EVERY_DAY:
            filter_date = today
            filter_field = "timestamp__date"
            next_submission_time = today + timedelta(days=1)  # Next day

        elif form_obj.interval == Form.Regularity.EVERY_WEEK:
            start_of_week = today - timedelta(days=today.weekday())  # Monday of this week
            filter_date = start_of_week
            filter_field = "timestamp__date__gte"
            next_submission_time = start_of_week + timedelta(days=7)  # Next week Monday

        elif form_obj.interval == Form.Regularity.EVERY_MONTH:
            filter_date = today.replace(day=1)  # First day of the current month
            filter_field = "timestamp__date__gte"
            if today.month == 12:  # Handle December (next month is January)
                next_submission_time = today.replace(year=today.year + 1, month=1, day=1)
            else:
                next_submission_time = today.replace(month=today.month + 1, day=1)  # First day of next month

        # Check if a submission already exists for the period
        already_submitted = Submission.objects.filter(
            form_id=form_id,
            user=user_id
        ).filter(**{filter_field: filter_date}).exists()

        if already_submitted:
            return _(f"Already submitted! Next available date {next_submission_time}")
    else:
        return False
    

@login_required
def fill_form_view(request, form_id):
    form_obj = get_object_or_404(Form, id=form_id)

    deny_to_fill = deny_access_to_form(request.user, form_id)
    if deny_to_fill:
        messages.error(request, deny_to_fill)
        return redirect("my-forms") 
        
    # Check if user is allowed to fill this form
    if not UserForms.objects.filter(user=request.user, form=form_obj).exists():
        messages.error(request, _("You are not a participant in this form."))
        return redirect("/") 
    
    questions = Question.objects.filter(form=form_obj).order_by('order')

    if request.method == "POST":
        submission = Submission.objects.create(
            form=form_obj,
            user=request.user
        )

        for question in questions:
            field_name = f"question_{question.id}"
            user_answer = ""

            if question.type == Question.QuestionType.TEXT_FIELD:
                user_answer = request.POST.get(field_name, "")

            elif question.type == Question.QuestionType.TEXT_AREA:
                user_answer = request.POST.get(field_name, "")

            elif question.type == Question.QuestionType.CHOICE:
                user_answer = request.POST.get(field_name, "")

            elif question.type == Question.QuestionType.MCHOICE:
                user_selections = request.POST.getlist(field_name)
                user_answer = ", ".join(user_selections)

            Answer.objects.create(
                user=request.user,
                submission=submission,
                field=question,
                answer=user_answer
            )

        messages.success(request, "Thank you! Your responses have been saved.")
        return redirect("/")

    else:
        return render(request, "formbuilder/fill_form.html", {
            "form_obj": form_obj,
            "questions": questions,
        })
        
@login_required
@examiner_required
def form_submissions_view(request, form_id):
    """
    Show all submissions for a given form (one row per submission), only if
    the current user is the author of that form.
    """
    # 1. Get the form, ensuring that the request.user is the author
    form = get_object_or_404(Form, pk=form_id)
    if form.author != request.user:
        messages.error(request, _("You don't have permissions to view this form!"))
        return redirect("/")

    # 2. Fetch all questions for this form in a desired order
    questions = Question.objects.filter(form=form).order_by('order')

    # 3. Fetch all submissions for this form
    submissions = (
        Submission.objects
        .filter(form=form)
        .select_related('user')  # fetch user info in one query
        .order_by('-timestamp')
    )

    # 4. Pre-fetch all answers for these submissions
    answers = (
        Answer.objects
        .filter(submission__in=submissions)
        .select_related('submission', 'field')
        .order_by('submission__timestamp', 'field__order')
    )

    # 5. Build a dictionary: submission_id -> list of Answer objects
    answers_by_submission = {}
    for ans in answers:
        answers_by_submission.setdefault(ans.submission_id, []).append(ans)

    # 6. For each submission, attach a dict: question.id -> answer.answer
    #    This makes it easy to find the answer to each question in the template.
    for submission in submissions:
        # Start empty if no answers
        submission.answers_dict = {}
        # Loop over that submission's answers and populate
        for ans in answers_by_submission.get(submission.id, []):
            submission.answers_dict[ans.field_id] = ans.answer

    context = {
        'form': form,
        'questions': questions,
        'submissions': submissions,
    }
    return render(request, 'formbuilder/form_submissions.html', context)


@login_required
def remove_participant(request, form_id , user_id):
    if request.method == 'POST':
        user_to_remove = get_object_or_404(User, id=user_id)
        form_object = get_object_or_404(Form, id=form_id)
        
        # Get the userform object in question
        participant = UserForms.objects.filter(user=user_to_remove, form=form_object)
        participant.delete()
        

        messages.success(request, f"Participant {user_to_remove.username} removed successfully.")
        return redirect("view_participants", form_id)
