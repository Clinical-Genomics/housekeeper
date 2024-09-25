FROM docker.io/library/python:3.12-slim-bullseye

WORKDIR /app
COPY . /app/

# Install app requirements
RUN pip install --ignore-installed poetry \
    && poetry config virtualenvs.create false \
    && poetry install --only main

ENTRYPOINT ["housekeeper"]