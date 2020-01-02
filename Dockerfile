FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN pip install poetry==1.0.0

WORKDIR /usr/src/app

COPY pyproject.toml poetry.lock ./
RUN poetry install

COPY . /usr/src/app

CMD ["poetry", "run", "app.py"]
