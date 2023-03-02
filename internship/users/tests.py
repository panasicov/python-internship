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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        test_refresh = response.data['refresh']

        response = self.client.post(
            reverse('token_obtain_pair'),
            data={
                "email": "user@example.com",
                "password": "string"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(reverse('token_refresh'), data={"refresh": test_refresh})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list(self):
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_timelog(self):
        user = User.objects.get(email='user1@mail.com')
        self.client.force_authenticate(user=user)

        response = self.client.get(reverse('user_timelog'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            reverse('task-create-timelog', kwargs={"pk": 1}),
            data={"start": timezone.datetime.strftime(timezone.now(), '%Y-%m-%d %H:%M:%S'),
                  "duration": 5}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse('user_timelog'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
