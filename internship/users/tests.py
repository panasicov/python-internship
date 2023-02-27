from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class UsersTests(APITestCase):
    fixtures = ['users', 'tasks', 'comments', 'timelogs']

    def test_register_login(self):
        response = self.client.post(
            reverse('token_register'),
            data={
                "first_name": "string",
                "last_name": "string",
                "email": "user@example.com",
                "password": "string"
            }
        )

        self.assertTrue(response.data['access'])
        self.assertTrue(response.data['refresh'])
        test_refresh = response.data['refresh']

        response = self.client.post(
            reverse('token_obtain_pair'),
            data={
                "email": "user@example.com",
                "password": "string"
            }
        )
        self.assertTrue(response.data['access'])
        self.assertTrue(response.data['refresh'])

        response = self.client.post(reverse('token_refresh'), data={"refresh": test_refresh})
        self.assertTrue(response.data['access'])

    def test_list(self):
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['full_name'], 'first_name1 last_name1')
        self.assertEqual(response.data['results'][1]['full_name'], 'first_name2 last_name2')

    def test_timelog(self):
        user = User.objects.get(email='user1@mail.com')
        self.client.force_authenticate(user=user)

        response = self.client.get(reverse('user_timelog'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data.get('time_sum_minutes', False))

        response = self.client.post(
            reverse('task-create-timelog', kwargs={"pk": 1}),
            data={"start": timezone.datetime.strftime(timezone.now(), '%Y-%m-%d %H:%M:%S'),
                  "duration": 5}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse('user_timelog'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['time_sum_minutes'], 5)
