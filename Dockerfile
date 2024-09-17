FROM docker.io/library/python:3.11-slim-bullseye
WORKDIR /app
COPY poetry.lock pyproject.toml /app/
COPY . /app/

# Install app requirements
RUN pip install poetry \
    && poetry install --only main

ENTRYPOINT ["poetry", "run", "housekeeper"]