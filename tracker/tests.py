from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
import datetime

from .models import Routine, Activity, Habit, HabitLog, Todo
from .forms import RoutineForm, ActivityForm, HabitForm, TodoForm


# ==============================================================================
# MODEL TESTS
# ==============================================================================

class RoutineModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.routine = Routine.objects.create(
            user=self.user,
            title='Morning Jog',
            category='HEALTH',
            priority='HIGH',
            start_time=datetime.time(6, 0),
            end_time=datetime.time(7, 0),
        )

    def test_routine_creation(self):
        self.assertEqual(self.routine.title, 'Morning Jog')
        self.assertEqual(self.routine.category, 'HEALTH')
        self.assertFalse(self.routine.is_completed)

    def test_routine_str(self):
        result = str(self.routine)
        self.assertIn('Morning Jog', result)

    def test_routine_default_completed(self):
        self.assertFalse(self.routine.is_completed)


class ActivityModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.activity = Activity.objects.create(
            user=self.user,
            title='Study Django',
            description='Learning about views and templates',
            category='EDUCATION',
            date=datetime.date.today(),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(12, 0),
            productivity_score=8,
        )

    def test_activity_creation(self):
        self.assertEqual(self.activity.title, 'Study Django')
        self.assertEqual(self.activity.productivity_score, 8)
        self.assertEqual(self.activity.status, 'COMPLETED')

    def test_activity_str(self):
        result = str(self.activity)
        self.assertIn('Study Django', result)


class HabitModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.habit = Habit.objects.create(
            user=self.user,
            name='Drink Water',
            habit_type='GOOD',
        )

    def test_habit_creation(self):
        self.assertEqual(self.habit.name, 'Drink Water')
        self.assertEqual(self.habit.habit_type, 'GOOD')
        self.assertEqual(self.habit.streak, 0)

    def test_habit_str(self):
        result = str(self.habit)
        self.assertIn('Drink Water', result)
        self.assertIn('Good Habit', result)


class HabitLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.habit = Habit.objects.create(user=self.user, name='Exercise', habit_type='GOOD')
        self.log = HabitLog.objects.create(
            habit=self.habit,
            date=datetime.date.today(),
            is_completed=True,
        )

    def test_habitlog_creation(self):
        self.assertEqual(self.log.habit.name, 'Exercise')
        self.assertTrue(self.log.is_completed)

    def test_habitlog_str(self):
        result = str(self.log)
        self.assertIn('Exercise', result)
        self.assertIn('Completed', result)

    def test_unique_together(self):
        """Cannot create two logs for the same habit on the same date."""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            HabitLog.objects.create(
                habit=self.habit,
                date=datetime.date.today(),
                is_completed=False,
            )


class TodoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.todo = Todo.objects.create(
            user=self.user,
            title='Submit Assignment',
            priority='HIGH',
            due_date=datetime.date.today(),
        )

    def test_todo_creation(self):
        self.assertEqual(self.todo.title, 'Submit Assignment')
        self.assertFalse(self.todo.is_completed)

    def test_todo_str(self):
        self.assertEqual(str(self.todo), 'Submit Assignment')


# ==============================================================================
# FORM TESTS
# ==============================================================================

class RoutineFormTest(TestCase):
    def test_valid_form(self):
        data = {
            'title': 'Morning Run',
            'category': 'HEALTH',
            'priority': 'HIGH',
            'start_time': '06:00',
            'end_time': '07:00',
        }
        form = RoutineForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_blank_title(self):
        data = {
            'title': '',
            'category': 'HEALTH',
            'priority': 'HIGH',
            'start_time': '06:00',
            'end_time': '07:00',
        }
        form = RoutineForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)


class ActivityFormTest(TestCase):
    def test_valid_form(self):
        data = {
            'title': 'Code Review',
            'description': 'Reviewed pull requests',
            'category': 'WORK',
            'date': datetime.date.today(),
            'start_time': '09:00',
            'end_time': '11:00',
            'status': 'COMPLETED',
            'mood': 'Focused',
            'productivity_score': 9,
        }
        form = ActivityForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_productivity_score(self):
        data = {
            'title': 'Nap',
            'category': 'LEISURE',
            'date': datetime.date.today(),
            'start_time': '14:00',
            'end_time': '15:00',
            'status': 'COMPLETED',
            'productivity_score': 15,  # Over max of 10
        }
        form = ActivityForm(data=data)
        self.assertFalse(form.is_valid())


class HabitFormTest(TestCase):
    def test_valid_form(self):
        data = {'name': 'Read Books', 'habit_type': 'GOOD'}
        form = HabitForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_blank_name(self):
        data = {'name': '', 'habit_type': 'GOOD'}
        form = HabitForm(data=data)
        self.assertFalse(form.is_valid())


class TodoFormTest(TestCase):
    def test_valid_form(self):
        data = {
            'title': 'Buy groceries',
            'priority': 'LOW',
            'due_date': datetime.date.today(),
        }
        form = TodoForm(data=data)
        self.assertTrue(form.is_valid())

    def test_valid_form_no_due_date(self):
        """Due date is optional."""
        data = {'title': 'Random task', 'priority': 'MEDIUM'}
        form = TodoForm(data=data)
        self.assertTrue(form.is_valid())


# ==============================================================================
# VIEW TESTS
# ==============================================================================

class LoginRequiredTest(TestCase):
    """Test that all tracker views require login."""

    def test_dashboard_redirect(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_routine_list_redirect(self):
        response = self.client.get(reverse('routine_list'))
        self.assertEqual(response.status_code, 302)

    def test_activity_list_redirect(self):
        response = self.client.get(reverse('activity_list'))
        self.assertEqual(response.status_code, 302)

    def test_habit_list_redirect(self):
        response = self.client.get(reverse('habit_list'))
        self.assertEqual(response.status_code, 302)

    def test_todo_list_redirect(self):
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 302)

    def test_search_redirect(self):
        response = self.client.get(reverse('search_results'))
        self.assertEqual(response.status_code, 302)


class DashboardViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_dashboard_status_code(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_template(self):
        response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'tracker/dashboard.html')

    def test_dashboard_contains_welcome(self):
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, 'Welcome back')


class RoutineViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.routine = Routine.objects.create(
            user=self.user,
            title='Study',
            category='EDUCATION',
            priority='HIGH',
            start_time=datetime.time(8, 0),
            end_time=datetime.time(10, 0),
        )

    def test_routine_list(self):
        response = self.client.get(reverse('routine_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Study')

    def test_routine_create(self):
        data = {
            'title': 'Workout',
            'category': 'HEALTH',
            'priority': 'MEDIUM',
            'start_time': '06:00',
            'end_time': '07:00',
        }
        response = self.client.post(reverse('routine_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Routine.objects.filter(title='Workout').exists())

    def test_routine_toggle(self):
        response = self.client.post(reverse('routine_toggle', args=[self.routine.pk]))
        self.assertEqual(response.status_code, 302)
        self.routine.refresh_from_db()
        self.assertTrue(self.routine.is_completed)

    def test_routine_delete(self):
        response = self.client.post(reverse('routine_delete', args=[self.routine.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Routine.objects.filter(pk=self.routine.pk).exists())


class ActivityViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_activity_list(self):
        response = self.client.get(reverse('activity_list'))
        self.assertEqual(response.status_code, 200)

    def test_activity_create(self):
        data = {
            'title': 'Write Report',
            'description': '',
            'category': 'WORK',
            'date': datetime.date.today().isoformat(),
            'start_time': '09:00',
            'end_time': '11:00',
            'status': 'COMPLETED',
            'mood': '',
            'productivity_score': 7,
        }
        response = self.client.post(reverse('activity_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Activity.objects.filter(title='Write Report').exists())


class HabitViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.habit = Habit.objects.create(
            user=self.user, name='Meditate', habit_type='GOOD'
        )

    def test_habit_list(self):
        response = self.client.get(reverse('habit_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Meditate')

    def test_habit_create(self):
        data = {'name': 'Stretch', 'habit_type': 'GOOD'}
        response = self.client.post(reverse('habit_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Habit.objects.filter(name='Stretch').exists())

    def test_habit_toggle(self):
        response = self.client.post(reverse('habit_toggle', args=[self.habit.pk]))
        self.assertEqual(response.status_code, 302)
        # A HabitLog should be created for today
        today = timezone.localdate()
        self.assertTrue(HabitLog.objects.filter(habit=self.habit, date=today).exists())


class TodoViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.todo = Todo.objects.create(
            user=self.user, title='Clean Room', priority='LOW'
        )

    def test_todo_list(self):
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Clean Room')

    def test_todo_create(self):
        data = {'title': 'Do Laundry', 'priority': 'MEDIUM'}
        response = self.client.post(reverse('todo_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Todo.objects.filter(title='Do Laundry').exists())

    def test_todo_toggle(self):
        response = self.client.post(reverse('todo_toggle', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 302)
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.is_completed)

    def test_todo_delete(self):
        response = self.client.post(reverse('todo_delete', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Todo.objects.filter(pk=self.todo.pk).exists())


class SearchViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        Activity.objects.create(
            user=self.user, title='Gym Workout', category='HEALTH',
            date=datetime.date.today(),
            start_time=datetime.time(7, 0), end_time=datetime.time(8, 0),
            productivity_score=9,
        )

    def test_search_page_loads(self):
        response = self.client.get(reverse('search_results'))
        self.assertEqual(response.status_code, 200)

    def test_search_with_query(self):
        response = self.client.get(reverse('search_results'), {'q': 'Gym'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gym Workout')

    def test_search_no_results(self):
        response = self.client.get(reverse('search_results'), {'q': 'xyz123nothing'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No matching activities found')


class ReportViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_weekly_report(self):
        response = self.client.get(reverse('weekly_report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tracker/weekly_report.html')

    def test_monthly_report(self):
        response = self.client.get(reverse('monthly_report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tracker/monthly_report.html')


class HabitAnalysisViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_habit_analysis_page(self):
        response = self.client.get(reverse('habit_analysis'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tracker/habit_analysis.html')


class InsightsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_insights_page(self):
        response = self.client.get(reverse('improvement_suggestions'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tracker/improvement_suggestions.html')
