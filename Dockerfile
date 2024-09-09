FROM docker.io/library/python:3.11-slim-bullseye

RUN addgroup --system nonroot \
    && adduser --system --ingroup nonroot nonroot

WORKDIR /app
COPY . /app/

# Install app requirements
RUN pip install poetry \
&& poetry export -f requrements.txt -o requirements.txt --without-hashes \
&& pip install -r requirements.txt -e .

USER nonroot