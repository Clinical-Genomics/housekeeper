FROM docker.io/library/python:3.11-slim-bullseye

RUN addgroup --system nonroot \
    && adduser --system --ingroup nonroot nonroot

WORKDIR /app
COPY . /app/

# Install app requirements
&& pip install --no-cache-dir .

USER nonroot