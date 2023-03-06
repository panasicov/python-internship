<div align="center">
    <h1>EBS Python Internship Test</h1>
    <p>REST API for task management application</p>
</div>

Welcome to the EBS Python Internship Test codebase. This is a REST API for task management application. This app
allows users to create tasks, assign them to other users, and log time spent on them.

## 🛠 Requirements
- Python 3.11
- Django 3.2.16
- Docker 23.0.1

## .env (with example of values)
```azure
SECRET_KEY='django-insecure-...'
DEBUG=1

CORS_ORIGIN_ALLOW_ALL=1
CORS_ORIGIN_WHITELIST=http://localhost:8000,http://127.0.0.1:8000,http://0.0.0.0:8000

DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres.internship.com
DB_PORT=5432

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_USE_TLS=1
EMAIL_PORT=587
EMAIL_HOST_USER=sender@gmail.com
EMAIL_HOST_PASSWORD=senderpass

REDIS_LOCATION=redis://internship_redis:6379/0

INTERNAL_IPS=127.0.0.1,0.0.0.0

RABBITMQ_USER=guest
RABBITMQ_PASS=guest
RABBITMQ_HOST=rabbitmq.internship.com
RABBITMQ_PORT=5672
RABBITMQ_VHOST=/
SENTRY_DSN=...
```

## 🔮 Installing and running locally

1. Install [Docker](https://www.docker.com/get-started)

2. Clone the repo

    ```sh
    $ git clone https://github.com/panasicov/python-internship
    $ cd python-internship
    ```

3. Create .env

4. Run

    ```sh
    $ docker compose up -d --build
    ```

## Endpoints:

### Register:
1. User register `POST | /register`

### Token:
1. User access token `POST | /token`
2. User refresh token `POST | /token/refresh`

### Users:
1. User list `GET | users/`
2. Total amount of time logged by user in last month `GET | /users/me/month_time`

### Tasks:
1. Task list `GET | tasks/`
2. Create task `POST | tasks/`
3. Top 20 user tasks in last month by time `GET | /task/month_top_20_by_time`
4. List with id and title of tasks assigned to user `GET | /task/user_tasks`
5. Task details by id `GET | /task/{id}`
6. Update task by id `PUT | /task/{id}`
7. Partial update task by id `PATCH | /task/{id}`
8. Delete task by id `DELETE | /task/{id}`
9. Create comment to task `POST | /task/{id}/create_comment`
10. Assign a task to user `PATCH | /task/{id}/task_assign`
11. Complete a task  `PATCH | /task/{id}/task_complete`

### TimeLogs:
1. Add time log for a task on a specific date  `POST | /timelog`
2. Start a timer for user task `POST | /timelog/start`
2. Stop a timer for user task `PATCH | /timelog/stop`
