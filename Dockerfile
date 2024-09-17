FROM docker.io/library/python:3.11-slim-bullseye

WORKDIR /app
COPY . /app/

# Install app requirements
RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --only main

ENTRYPOINT ["housekeeper"]