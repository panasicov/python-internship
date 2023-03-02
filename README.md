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
