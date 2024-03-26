FROM python:3-slim

# For healthcheck
RUN apt-get update && apt-get install curl -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Copy server files
COPY rfSsdpServer.py redfishMockupServer.py /usr/src/app/
COPY public-rackmount1 /usr/src/app/public-rackmount1

# Env settings
EXPOSE 8000
HEALTHCHECK CMD curl --fail http://127.0.0.1:8000/redfish/v1 || exit 1
WORKDIR /usr/src/app
ENTRYPOINT ["python", "/usr/src/app/redfishMockupServer.py", "-H", "0.0.0.0"]
