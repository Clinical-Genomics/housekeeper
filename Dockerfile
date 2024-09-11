FROM docker.io/library/python:3.11-slim-bullseye


RUN addgroup --system nonroot \
    && adduser --system --ingroup nonroot nonroot

COPY . /app/
WORKDIR /app

# Install app requirements
RUN pip install poetry \
&& poetry export -f requirements.txt -o requirements.txt --without-hashes \
&& pip install --no-cache-dir -r requirements.txt -e .

USER nonroot

ENTRYPOINT ["python", "-m", "housekeeper"]