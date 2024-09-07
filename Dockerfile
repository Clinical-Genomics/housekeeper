FROM docker.io/library/python:3.11-slim-bullseye

RUN addgroup --system nonroot \
    && adduser --system --ingroup nonroot nonroot

WORKDIR /app
COPY . /app/

RUN pip install poetry

# Install app requirements
RUN poetry export -f requirements.txt -o requirements.txt --without-hashes
RUN pip install -r requirements.txt -e .

USER nonroot