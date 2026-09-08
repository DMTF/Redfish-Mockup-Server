#!/bin/sh
# Docker healthcheck script for Redfish Mockup Server
# Detects SSL mode and port from container arguments

# Read the container's command arguments
ARGS=$(cat /proc/1/cmdline | tr '\0' ' ')

# Detect port (default 8000)
PORT=8000
if echo "$ARGS" | grep -q -- "--port"; then
    # Extract port number after --port flag
    PORT=$(echo "$ARGS" | sed -n 's/.*--port[[:space:]]*\([0-9]*\).*/\1/p')
fi

# Detect SSL mode by checking for --ssl or -s flags
if echo "$ARGS" | grep -qE -- "(--ssl|-s[[:space:]])"; then
    # HTTPS mode - use insecure flag to accept self-signed certificates
    exec curl --insecure --fail "https://127.0.0.1:${PORT}/redfish/v1" || exit 1
else
    # HTTP mode
    exec curl --fail "http://127.0.0.1:${PORT}/redfish/v1" || exit 1
fi