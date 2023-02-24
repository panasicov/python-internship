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
        self.assertEqual(response.data['title'], 'Test title 1')

        response = self.client.put(reverse('task-detail', kwargs={"pk": 1}), data={"title": "Put title", "description": "Put description"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Put title')
        self.assertEqual(response.data['description'], 'Put description')

        response = self.client.patch(reverse('task-detail', kwargs={"pk": 1}), data={"title": "Patched title"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Patched title')
        self.assertEqual(response.data['description'], 'Put description')

        response = self.client.delete(reverse('task-detail', kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(reverse('task-detail', kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list(self):
        response = self.client.get(reverse('task-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['title'], 'Test title 1')
        self.assertEqual(response.data['results'][0]['description'], 'Test description 1')
        self.assertEqual(response.data['results'][1]['title'], 'Test title 2')
        self.assertEqual(response.data['results'][1]['description'], 'Test description 2')

        response = self.client.get(reverse('task-list'), {'is_completed': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

        response = self.client.get(reverse('task-list'), {'search': 'Test title 2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test title 2')
        self.assertEqual(response.data['results'][0]['description'], 'Test description 2')

    def test_create(self):
        response = self.client.post(reverse('task-list'), data={"title": "Test title", "description": "Test description"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test title')
        self.assertEqual(response.data['description'], 'Test description')
        self.assertEqual(response.data['created_by'], 1)
        self.assertEqual(response.data['assigned_to'], 1)

    def test_me(self):
        response = self.client.get(reverse('task-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test title 1')
        self.assertEqual(response.data['results'][0]['description'], 'Test description 1')

    def test_assign(self):
        response = self.client.post(reverse('task-assign', kwargs={"pk": 2}), data={'assigned_to': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['assigned_to'], 1)

        response = self.client.get(reverse('task-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_complete(self):
        response = self.client.patch(reverse('task-complete', kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_completed'], True)

        response = self.client.get(reverse('task-list'), {'is_completed': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        response = self.client.patch(reverse('task-complete', kwargs={"pk": 2}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_completed'], True)

        response = self.client.get(reverse('task-list'), {'is_completed': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_comment(self):
        response = self.client.post(reverse('task-comment', kwargs={"pk": 1}), data={'text': 'string'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], 'string')

    def test_timelog(self):
        response = self.client.post(
            reverse('task-create-timelog', kwargs={"pk": 1}),
            data={"start": timezone.datetime.strftime(timezone.now(), '%Y-%m-%d %H:%M:%S'),
                  "duration": 2}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse('task-me-timelog'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_start_stop_timelog(self):
        response = self.client.post(reverse('task-start-timelog', kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['start'])
        self.assertFalse(response.data['stop'])

        response = self.client.post(reverse('task-start-timelog', kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Cannot start a new time log before stopping the last one.')

        response = self.client.patch(reverse('task-stop-timelog', kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['start'])
        self.assertTrue(response.data['stop'])

        response = self.client.patch(reverse('task-stop-timelog', kwargs={"pk": 1}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Cannot stop time log before starting the new one.')
