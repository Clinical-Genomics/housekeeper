FROM docker.io/library/python:3.11-slim-bullseye

RUN addgroup --system nonroot \
    && adduser --system --ingroup nonroot nonroot

WORKDIR /app
COPY . /app/

# Install app requirements
RUN pip install poetry \
&& poetry config virtualenvs.create false \
&& poetry install --no-interaction --no-ansi



USER nonroot