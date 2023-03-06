from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class TaskTests(TestCase):
    fixtures = ['users', 'tasks', 'comments', 'timelogs']

    def setUp(self):
        self.client = APIClient()
        user = User.objects.get(email='user1@mail.com')
        self.client.force_authenticate(user=user)

    def test_retrieve(self):
        response = self.client.get(reverse('task-detail', kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.put(
            reverse('task-detail', kwargs={"pk": 1}),
            data={"title": "Put title", "description": "Put description"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.patch(
            reverse('task-detail', kwargs={"pk": 1}),
            data={"title": "Patched title"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(reverse('task-detail', kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(reverse('task-detail', kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list(self):
        response = self.client.get(reverse('task-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse('task-list'), {'is_completed': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse('task-list'), {'search': 'Test title 2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        response = self.client.post(
            reverse('task-list'),
            data={"title": "Test title", "description": "Test description"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_me(self):
        response = self.client.get(reverse('task-user_tasks'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_assign(self):
        response = self.client.patch(reverse('task-task_assign', kwargs={"pk": 2}), data={'assigned_to': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse('task-user_tasks'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_complete(self):
        response = self.client.patch(reverse('task-task_complete', kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse('task-list'), {'is_completed': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.patch(reverse('task-task_complete', kwargs={"pk": 2}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse('task-list'), {'is_completed': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment(self):
        response = self.client.post(reverse('task-create_comment', kwargs={"pk": 1}), data={'text': 'string'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_timelog(self):
        response = self.client.post(
            reverse('timelog-list'),
            data={
                "start": timezone.datetime.strftime(timezone.now(), '%Y-%m-%d %H:%M:%S'),
                "duration": "2",
                "task": 1
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(reverse('user_month_time'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_start_stop_timelog(self):
        response = self.client.post(reverse('timelog-start_timelog'), data={"task": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(reverse('timelog-start_timelog'), data={"task": 1})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(reverse('timelog-stop_timelog'), data={"task": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.patch(reverse('timelog-stop_timelog'), data={"task": 1})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
