from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth import get_user_model
from formbuilder.models import Form, UserForms, Submission, Question, Answer
from django.contrib.messages import get_messages


User = get_user_model()

class FillFormViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.form = Form.objects.create(title="Test Form", interval=Form.Regularity.EVERY_DAY, description="Test Form", author=self.user)
        self.user_form = UserForms.objects.create(user=self.user, form=self.form)
        self.question_text = Question.objects.create(form=self.form, title="Test question", type=Question.QuestionType.TEXT_FIELD, order=1, mandatory=False)
        self.url = reverse("fill_form_view", args=[self.form.id])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/login/?next=/form/1/fill-out")

    def test_access_denied_if_not_participant(self):
        self.client.login(username='testuser', password='password')
        self.user_form.delete()  # Remove user from allowed participants
        response = self.client.get(self.url)
        self.assertRedirects(response, "/")
        response = self.client.get(self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("You are not a participant in this form." in str(m) for m in messages))

    def test_prevent_duplicate_submission(self):
        self.client.login(username='testuser', password='password')
        today = now().date()
        Submission.objects.create(form=self.form, user=self.user, timestamp=now())
        response = self.client.get(self.url)
        self.assertRedirects(response, "/my-forms/")
        response = self.client.get(self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Cannot fill form, it has already been submitted for this period!" in str(m) for m in messages))

    def test_successful_submission(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(self.url, {
            f"question_{self.question_text.id}": "John Doe"
        })
        self.assertRedirects(response, "/")
        self.assertTrue(Submission.objects.filter(form=self.form, user=self.user).exists())
        self.assertTrue(Answer.objects.filter(submission__form=self.form, field=self.question_text, answer="John Doe").exists())

    def test_next_submission_time_calculation(self):
        self.client.login(username='testuser', password='password')
        today = now().date()
        Submission.objects.create(form=self.form, user=self.user, timestamp=now())
        response = self.client.get(self.url)
        next_submission_date = today + timedelta(days=1)
        response = self.client.get(self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(f"Next available submission: {next_submission_date}" in str(m) for m in messages))
