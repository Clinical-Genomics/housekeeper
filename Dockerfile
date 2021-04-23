FROM python:3.7-slim

LABEL base_image="python:3.7-slim"
LABEL software="housekeeper"
LABEL about.summary="Image for housekeeper"
LABEL about.home="https://github.com/Clinical-Genomics/housekeeper"
LABEL about.documentation="https://github.com/Clinical-Genomics/housekeeper/README.md"
LABEL about.license_file="https://github.com/Clinical-Genomics/housekeeper/LICENSE"
LABEL about.license="MIT License (MIT)"
LABEL about.tags="files,database"
LABEL maintainer="Måns Magusson <mans.magnusson@scilifelab.se>"

RUN pip install --no-cache-dir -U pip
# Avoid running as root for security reasons
# More about that: https://pythonspeed.com/articles/root-capabilities-docker-security/
# Solution inspired from
# https://medium.com/@DahlitzF/run-python-applications-as-non-root-user-in-docker-containers-by-example-cba46a0ff384
RUN useradd --create-home worker
USER worker
WORKDIR /home/worker


# Copy the lockfile to temporary directory. This will be deleted
COPY --chown=worker:worker requirements.txt /tmp/
# Install deps
RUN pip install --no-cache-dir --user -r /tmp/requirements.txt
# Copy package
COPY --chown=worker:worker . /tmp/housekeeper
# Install package
RUN pip install --no-cache-dir /tmp/housekeeper

ENTRYPOINT ["housekeeper"]
CMD ["--help"]
