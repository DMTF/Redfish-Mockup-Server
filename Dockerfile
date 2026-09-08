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

# Copy healthcheck script
COPY healthcheck.sh /usr/src/app/

# Env settings
EXPOSE 8000
HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=3 CMD /usr/src/app/healthcheck.sh
WORKDIR /usr/src/app
ENTRYPOINT ["python", "/usr/src/app/redfishMockupServer.py", "-H", "0.0.0.0"]
