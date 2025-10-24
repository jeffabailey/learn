from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Task

UserModel = get_user_model()


class TaskModelTest(TestCase):
    """Test the Task model"""

    def setUp(self):
        self.user = UserModel.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_task_creation(self):
        """Test creating a task"""
        task = Task.objects.create(
            user=self.user,
            description='Test task',
            is_complete=False
        )
        self.assertEqual(task.user, self.user)
        self.assertEqual(task.description, 'Test task')
        self.assertFalse(task.is_complete)

    def test_task_str_representation(self):
        """Test the string representation of a task"""
        task = Task.objects.create(
            user=self.user,
            description='Test task',
            is_complete=True
        )
        expected_str = f"Test task, is_complete=True"
        self.assertEqual(str(task), expected_str)

    def test_task_ordering(self):
        """Test that tasks are ordered by -id"""
        task1 = Task.objects.create(user=self.user, description='Task 1')
        task2 = Task.objects.create(user=self.user, description='Task 2')
        task3 = Task.objects.create(user=self.user, description='Task 3')

        tasks = Task.objects.all()
        self.assertEqual(tasks[0], task3)
        self.assertEqual(tasks[1], task2)
        self.assertEqual(tasks[2], task1)

    def test_task_deletion_on_user_deletion(self):
        """Test that tasks are deleted when user is deleted"""
        task = Task.objects.create(
            user=self.user,
            description='Test task'
        )
        task_id = task.id
        self.user.delete()

        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(id=task_id)


class TaskViewTest(TestCase):
    """Test task views"""

    def setUp(self):
        self.client = Client()
        self.user = UserModel.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_task_list_unauthenticated(self):
        """Test task list view for unauthenticated users"""
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 200)

    def test_task_list_authenticated(self):
        """Test task list view for authenticated users"""
        self.client.login(username='testuser', password='testpass123')

        # Create some tasks
        Task.objects.create(user=self.user, description='Task 1')
        Task.objects.create(user=self.user, description='Task 2')

        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, 200)

    def test_task_create_requires_authentication(self):
        """Test that task creation requires authentication"""
        response = self.client.post('/tasks/create/', {
            'description': 'New task'
        })
        # Should redirect or return error for unauthenticated user
        self.assertIn(response.status_code, [302, 401, 403])

    def test_task_create_authenticated(self):
        """Test creating a task as authenticated user"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.post('/tasks/create/', {
            'description': 'New task'
        }, HTTP_HX_REQUEST='true')

        # Should create the task
        task_exists = Task.objects.filter(
            user=self.user,
            description='New task'
        ).exists()
        self.assertTrue(task_exists)

    def test_task_create_without_description(self):
        """Test creating a task without description fails gracefully"""
        self.client.login(username='testuser', password='testpass123')

        initial_count = Task.objects.count()
        response = self.client.post('/tasks/create/', {}, HTTP_HX_REQUEST='true')

        # Should not create a task without description
        self.assertEqual(Task.objects.count(), initial_count)

    def test_user_can_only_see_own_tasks(self):
        """Test that users can only see their own tasks"""
        other_user = UserModel.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )

        # Create task for main user
        Task.objects.create(user=self.user, description='My task')

        # Create task for other user
        Task.objects.create(user=other_user, description='Other task')

        # Login as main user
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/tasks/')

        # Should only see own tasks
        self.assertContains(response, 'My task')
        self.assertNotContains(response, 'Other task')
