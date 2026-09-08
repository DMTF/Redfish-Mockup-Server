.PHONY: all build test test-http test-https clean clean-containers clean-certs help

# Docker image name
IMAGE_NAME := redfish-mockup-server
IMAGE_TAG := test

# Container names
HTTP_CONTAINER := redfish-http-test
HTTPS_CONTAINER := redfish-https-test

# Ports
HTTP_PORT := 8456
HTTPS_PORT := 8443

# Certificate paths (created in repo root)
CERT_DIR_TEMPLATE := redfish-test-certs.XXXXXX
CERT_DIR := $(shell mktemp -d ./$(CERT_DIR_TEMPLATE) 2>/dev/null || mktemp -d)
CERT_FILE := $(CERT_DIR)/cert.pem
KEY_FILE := $(CERT_DIR)/key.pem

# Default target
all: build test

# Build the Docker image
build:
	@echo "Building Docker image $(IMAGE_NAME):$(IMAGE_TAG)..."
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

# Generate self-signed certificates for testing
$(CERT_FILE):
	@echo "Generating self-signed SSL certificates in $(CERT_DIR)..."
	@mkdir -p $(CERT_DIR)
	@openssl req -x509 -nodes -newkey rsa:2048 \
		-keyout $(KEY_FILE) -out $(CERT_FILE) \
		-sha256 -days 365 \
		-subj "/C=US/ST=Test/L=Test/O=Test/OU=Test/CN=localhost" \
		2>/dev/null

# Test both HTTP and HTTPS
test: test-http test-https
	@echo "All tests passed!"

# Test HTTP mode
test-http: build clean-containers
	@echo "Testing HTTP mode..."
	@echo "Starting container..."
	@docker run -d --name $(HTTP_CONTAINER) \
		-p $(HTTP_PORT):8000 \
		$(IMAGE_NAME):$(IMAGE_TAG) >/dev/null
	@echo "Waiting for container to be healthy..."
	@for i in 1 2 3 4 5 6 7 8 9 10; do \
		status=$$(docker inspect --format='{{.State.Health.Status}}' $(HTTP_CONTAINER) 2>/dev/null); \
		if [ "$$status" = "healthy" ]; then \
			echo "✓ HTTP container is healthy"; \
			break; \
		elif [ $$i -eq 10 ]; then \
			echo "✗ HTTP container failed to become healthy"; \
			docker logs $(HTTP_CONTAINER); \
			exit 1; \
		fi; \
		sleep 3; \
	done
	@echo "Testing HTTP endpoint..."
	@curl --fail --silent http://localhost:$(HTTP_PORT)/redfish/v1 >/dev/null && \
		echo "✓ HTTP endpoint is accessible" || \
		(echo "✗ HTTP endpoint is not accessible" && exit 1)
	@docker stop $(HTTP_CONTAINER) >/dev/null
	@docker rm $(HTTP_CONTAINER) >/dev/null
	@echo "✓ HTTP mode test completed"

# Test HTTPS mode
test-https: build clean-containers $(CERT_FILE)
	@echo "Testing HTTPS mode..."
	@echo "Starting container with SSL..."
	@docker run -d --name $(HTTPS_CONTAINER) \
		-v $(CERT_DIR):/certs:ro \
		-p $(HTTPS_PORT):8000 \
		$(IMAGE_NAME):$(IMAGE_TAG) \
		--ssl --cert /certs/cert.pem --key /certs/key.pem >/dev/null
	@echo "Waiting for container to be healthy..."
	@for i in 1 2 3 4 5 6 7 8 9 10; do \
		status=$$(docker inspect --format='{{.State.Health.Status}}' $(HTTPS_CONTAINER) 2>/dev/null); \
		if [ "$$status" = "healthy" ]; then \
			echo "✓ HTTPS container is healthy"; \
			break; \
		elif [ $$i -eq 10 ]; then \
			echo "✗ HTTPS container failed to become healthy"; \
			docker logs $(HTTPS_CONTAINER); \
			exit 1; \
		fi; \
		sleep 3; \
	done
	@echo "Testing HTTPS endpoint..."
	@curl --fail --silent --insecure https://localhost:$(HTTPS_PORT)/redfish/v1 >/dev/null && \
		echo "✓ HTTPS endpoint is accessible" || \
		(echo "✗ HTTPS endpoint is not accessible" && exit 1)
	@docker stop $(HTTPS_CONTAINER) >/dev/null
	@docker rm $(HTTPS_CONTAINER) >/dev/null
	@echo "✓ HTTPS mode test completed"

# Run containers interactively for debugging
run-http: build
	docker run --rm -it -p $(HTTP_PORT):8000 $(IMAGE_NAME):$(IMAGE_TAG)

run-https: build $(CERT_FILE)
	docker run --rm -it -v $(CERT_DIR):/certs:ro -p $(HTTPS_PORT):8000 \
		$(IMAGE_NAME):$(IMAGE_TAG) \
		--ssl --cert /certs/cert.pem --key /certs/key.pem

# Clean up everything
clean: clean-containers clean-certs
	@echo "Cleanup completed"

# Clean up containers
clean-containers:
	@docker stop $(HTTP_CONTAINER) 2>/dev/null || true
	@docker stop $(HTTPS_CONTAINER) 2>/dev/null || true
	@docker rm $(HTTP_CONTAINER) 2>/dev/null || true
	@docker rm $(HTTPS_CONTAINER) 2>/dev/null || true

# Clean up certificates
clean-certs:
	@echo "Cleaning up certificate directories..."
	@rm -rf ./redfish-test-certs.*

# Show available targets
help:
	@echo "Available targets:"
	@echo "  make build       - Build the Docker image"
	@echo "  make test        - Run all tests (HTTP and HTTPS)"
	@echo "  make test-http   - Test HTTP mode only"
	@echo "  make test-https  - Test HTTPS mode only"
	@echo "  make run-http    - Run container in HTTP mode (interactive)"
	@echo "  make run-https   - Run container in HTTPS mode (interactive)"
	@echo "  make clean       - Clean up containers and certificates"
	@echo "  make help        - Show this help message"