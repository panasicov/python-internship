docker-run-dev:
	python3 ./apps/common/wait_for_postgres.py
	python3 manage.py migrate
	python3 manage.py filldb
	python3 manage.py test apps --no-input
	python3 manage.py runserver 0.0.0.0:8000
