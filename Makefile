IMAGE_NAME ?= quay.io/oma/oma-service-mcp
TAG ?= latest
NAMESPACE ?= $(shell oc project -q 2>/dev/null || echo "default")

# ─── Local Development ───────────────────────────────────────────────

.PHONY: run-local
run-local: ## Run the MCP server locally (SSE on port 8000)
	uv run python -m oma_service_mcp.src.main

.PHONY: run-stdio
run-stdio: ## Run the MCP server over stdio (for IDE integration)
	uv run python -m oma_service_mcp.src.stdio

.PHONY: sync
sync: ## Install/sync project dependencies
	uv sync

.PHONY: test
test: ## Run tests
	uv run --group test pytest

.PHONY: test-coverage
test-coverage: ## Run tests with coverage report
	uv run --group test pytest --cov=oma_service_mcp --cov-report=html --cov-report=term-missing

.PHONY: lint
lint: ## Run linter (ruff)
	uv run --group dev ruff check .

.PHONY: typecheck
typecheck: ## Run type checker (mypy)
	uv run --group dev mypy --config-file pyproject.toml .

.PHONY: format
format: ## Auto-format code
	uv run --group dev ruff check . --fix
	uv run --group dev ruff format .

.PHONY: verify
verify: lint typecheck test ## Run all checks (lint + typecheck + test)

# ─── Container Build ─────────────────────────────────────────────────

.PHONY: build
build: ## Build container image with podman
	podman build -f Containerfile -t $(IMAGE_NAME):$(TAG) .

.PHONY: push
push: ## Push container image to registry
	podman push $(IMAGE_NAME):$(TAG)

.PHONY: run
run: ## Run container locally with podman
	podman run --rm -p 127.0.0.1:8000:8000 \
		--env-file .env \
		$(IMAGE_NAME):$(TAG)

# ─── OpenShift Deployment ────────────────────────────────────────────

.PHONY: deploy
deploy: ## Deploy to OpenShift (current namespace)
	@echo "Deploying to namespace: $(NAMESPACE)"
	oc apply -f deploy/openshift/configmap.yaml -n $(NAMESPACE)
	oc apply -f deploy/openshift/secret.yaml -n $(NAMESPACE)
	oc apply -f deploy/openshift/deployment.yaml -n $(NAMESPACE)
	oc apply -f deploy/openshift/service.yaml -n $(NAMESPACE)
	oc apply -f deploy/openshift/route.yaml -n $(NAMESPACE)
	@echo "Waiting for rollout..."
	oc rollout status deployment/oma-service-mcp -n $(NAMESPACE) --timeout=120s
	@echo "Route URL:"
	@oc get route oma-service-mcp -n $(NAMESPACE) -o jsonpath='https://{.spec.host}' 2>/dev/null && echo || echo "(route not yet available)"

.PHONY: deploy-image
deploy-image: build push deploy ## Build, push, and deploy to OpenShift
	oc set image deployment/oma-service-mcp \
		oma-service-mcp=$(IMAGE_NAME):$(TAG) -n $(NAMESPACE)

.PHONY: undeploy
undeploy: ## Remove deployment from OpenShift
	@echo "Removing from namespace: $(NAMESPACE)"
	oc delete -f deploy/openshift/route.yaml -n $(NAMESPACE) --ignore-not-found
	oc delete -f deploy/openshift/service.yaml -n $(NAMESPACE) --ignore-not-found
	oc delete -f deploy/openshift/deployment.yaml -n $(NAMESPACE) --ignore-not-found
	oc delete -f deploy/openshift/secret.yaml -n $(NAMESPACE) --ignore-not-found
	oc delete -f deploy/openshift/configmap.yaml -n $(NAMESPACE) --ignore-not-found

.PHONY: deploy-status
deploy-status: ## Check deployment status on OpenShift
	@echo "=== Deployment ==="
	oc get deployment oma-service-mcp -n $(NAMESPACE) 2>/dev/null || echo "Not found"
	@echo "\n=== Pods ==="
	oc get pods -l app=oma-service-mcp -n $(NAMESPACE) 2>/dev/null || echo "No pods"
	@echo "\n=== Route ==="
	@oc get route oma-service-mcp -n $(NAMESPACE) -o jsonpath='https://{.spec.host}' 2>/dev/null && echo || echo "No route"

.PHONY: deploy-logs
deploy-logs: ## Tail logs from the OpenShift pod
	oc logs -f deployment/oma-service-mcp -n $(NAMESPACE)

.PHONY: deploy-set-config
deploy-set-config: ## Update ConfigMap values (usage: make deploy-set-config KEY=migration-planner-url VALUE=http://host:7443)
	@if [ -z "$(KEY)" ] || [ -z "$(VALUE)" ]; then \
		echo "Usage: make deploy-set-config KEY=<key> VALUE=<value>"; \
		echo "Keys: migration-planner-url, auth-type, sso-url"; \
		exit 1; \
	fi
	oc patch configmap oma-service-mcp-config -n $(NAMESPACE) \
		--type merge -p '{"data":{"$(KEY)":"$(VALUE)"}}'
	oc rollout restart deployment/oma-service-mcp -n $(NAMESPACE)

.PHONY: deploy-set-secret
deploy-set-secret: ## Update Secret values (usage: make deploy-set-secret KEY=bearer-token VALUE=xxx)
	@if [ -z "$(KEY)" ] || [ -z "$(VALUE)" ]; then \
		echo "Usage: make deploy-set-secret KEY=<key> VALUE=<value>"; \
		echo "Keys: bearer-token, offline-token"; \
		exit 1; \
	fi
	oc patch secret oma-service-mcp-secret -n $(NAMESPACE) \
		--type merge -p '{"stringData":{"$(KEY)":"$(VALUE)"}}'
	oc rollout restart deployment/oma-service-mcp -n $(NAMESPACE)

# ─── Help ────────────────────────────────────────────────────────────

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
