import datetime
from django.utils import timezone
from django.test import TestCase
from polls.models import Question, Choice
from django.core.urlresolvers import reverse

# Create your tests here.
class QuestionMethodTests(TestCase):
    
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return False for questions whose pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_publshed_recently() should return False for questions whose pub_date is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertEqual(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() should return true for questions whose pub_date is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertEqual(recent_question.was_published_recently(), True)

def create_question(question_text, days):
    """
    Creates a question with the given 'question_text' published the given number of `days` offset to now (negative for the questions published in the past, positive for questions that have yet to be published.
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_choice(choice_text, question):
    """Creates a choice with the given choice_text and the given question. """
    return Choice.objects.create(choice_text=choice_text, question=question)

class QuestionViewTests(TestCase):
    def test_index_with_no_questions(self):
        # If no question exist, an appropriate message should be displayed.
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question(self):
        # Questions with a pub_date in the past should be displayed on the index page.
        question = create_question(question_text="Past question.", days=-30)
        create_choice(choice_text='Past choice', question=question)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question.>'])

    def test_index_view_with_a_future_question(self):
        # Questions with a pub_date in the future should not be displayed on the index page.
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.", status_code=200)
        #self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Future question.>'])

    def test_index_view_with_future_question_and_past_question(self):
        # Even if both past and future questions exist, only past questions should be displayed.
        question1 = create_question(question_text = "Past question.", days=-30)
        question2 = create_question(question_text = "Future question.", days=30)
        create_choice(choice_text="Past choice", question=question1)
        create_choice(choice_text="Future choice", question=question2)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question.>'])

    def test_index_view_with_two_past_questions(self):
        # The questions index page may display multiple questions.
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        create_choice(choice_text="Past choice", question=question1)
        create_choice(choice_text="Past choice 2", question=question2)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], 
                ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )
    
    def test_index_view_no_choices(self):
        #import pdb;pdb.set_trace()
        question = create_question(question_text="Question with no choices", days=-2)
        create_choice(choice_text="", question=question)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Question with no choices>'])
        

class QuestionIndexDetailTests(TestCase):
    def test_detail_view_with_a_future_question(self):
        # The detail view of a question with a pub_date in the future should return a 404
        future_question = create_question(question_text = "Future Question.", days=5)
        response = self.client.get(reverse('polls:detail', args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        # The detail view of a question with a pub_date n the past should display the questions text
        past_question = create_question(question_text = "Past Question.", days=-5)
        response = self.client.get(reverse('polls:detail', args=(past_question.id,)))
        self.assertContains(response, past_question.question_text, status_code=200)

class QuestionResultsViewTests(TestCase):

    def test_results_view_with_a_future_question(self):
        future_question = create_question(question_text = "Future Question.", days=3)
        response = self.client.get(reverse('polls:results', args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_past_question(self):
        past_question = create_question(question_text = "Past Question.", days=-3)
        response = self.client.get(reverse('polls:results', args=(past_question.id,)))
        self.assertContains(response, past_question.question_text, status_code=200)





