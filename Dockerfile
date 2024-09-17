FROM docker.io/library/python:3.11-slim-bullseye

COPY . /app/
WORKDIR /app

# Install app requirements
RUN pip install poetry \
    && poetry install --only main

ENTRYPOINT ["poetry", "run", "housekeeper"]