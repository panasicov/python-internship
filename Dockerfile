FROM python:3.11-slim-buster

WORKDIR /app
EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org poetry

COPY ./poetry.lock ./poetry.lock
COPY ./pyproject.toml ./pyproject.toml

RUN poetry config virtualenvs.create false --local && \
    poetry install

COPY ./internship ./internship

CMD ["python", "-m", "internship", "runserver"]