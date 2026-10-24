# Comandos habituales del sistema de referencia. `make help` los lista.
SHELL := /bin/bash
REGISTRY ?= acropsagentdev.azurecr.io/
TAG ?= 0.1.0
KIND_CLUSTER ?= opsagent
NS := opsagent
K8S := deploy/kubernetes
TF_AZURE := deploy/terraform/azure
IMAGES := ops-mcp:ops-mcp change-advisor:change-advisor ops-agent:opsagent  # imagen:paquete
KUBECONFORM := kubeconform -strict -summary -kubernetes-version 1.37.0 -schema-location default \
  -schema-location 'https://raw.githubusercontent.com/datreeio/CRDs-catalog/main/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json'

.PHONY: help install test lint format bench evals chat images push kind-load k8s-config k8s-secrets-local deploy-local deploy-azure azure-manifest validate-k8s tf-validate harness-test harness-drift

help: ## Muestra esta ayuda
	@grep -hE '^[a-z0-9-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "} {printf "  %-18s %s\n", $$1, $$2}'

install: ## Crea el entorno con uv (en WSL, mejor con el repo o UV_PROJECT_ENVIRONMENT en el FS de Linux)
	uv sync

test: ## Tests de todos los paquetes (sin red ni coste)
	uv run pytest -q

lint: ## Ruff (lint + formato)
	uv run ruff check . && uv run ruff format --check .

format: ## Aplica el formato
	uv run ruff format . && uv run ruff check --fix .

bench: ## Benchmarks offline con umbrales (recuperación, detección de inyección)
	uv run opsagent-bench --check

evals: ## Evals con el modelo real (cuesta dinero; necesita credenciales)
	uv run opsagent-evals --judge --output evals-and-benchmarks/reports/latest.json

chat: ## CLI interactiva del agente (MCP por stdio y change advisor en proceso)
	uv run opsagent

images: ## Construye las imágenes con el nombre que usan los manifiestos (REGISTRY, TAG)
	@for spec in $(IMAGES); do name=$${spec%%:*}; pkg=$${spec##*:}; \
	  docker build -f deploy/docker/Dockerfile --build-arg PACKAGE=$$pkg -t $(REGISTRY)$$name:$(TAG) . || exit 1; done

push: ## Publica las imágenes en el ACR (antes: az acr login -n <acr>)
	@for spec in $(IMAGES); do docker push $(REGISTRY)$${spec%%:*}:$(TAG) || exit 1; done

kind-load: ## Carga las imágenes en el clúster kind (no las descarga del registro)
	@for spec in $(IMAGES); do kind load docker-image --name $(KIND_CLUSTER) $(REGISTRY)$${spec%%:*}:$(TAG) || exit 1; done

k8s-config: ## Namespace y ConfigMaps desde litellm-config.yaml y la config del collector
	kubectl apply -f $(K8S)/namespace.yaml
	kubectl -n $(NS) create configmap llm-gateway-config --from-file=config.yaml=llm-gateway/litellm-config.yaml \
	  --dry-run=client -o yaml | kubectl apply -f -
	kubectl -n $(NS) create configmap otel-collector-config --from-file=config.yaml=observability/collector/otel-collector.yaml \
	  --dry-run=client -o yaml | kubectl apply -f -

k8s-secrets-local: ## Secrets de kind desde deploy/kubernetes/local/secrets/*.env
	@for example in $(K8S)/local/secrets/*.env.example; do env=$${example%.example}; \
	  [ -f "$$env" ] || { echo "Falta $$env: cópialo de $$example y rellénalo"; exit 1; }; \
	  kubectl -n $(NS) create secret generic "$$(basename $$env .env)-secrets" --from-env-file="$$env" \
	    --dry-run=client -o yaml | kubectl apply -f - || exit 1; done

deploy-local: k8s-config k8s-secrets-local ## Despliega en kind: entorno local, Jaeger y la aplicación
	kubectl apply -f $(K8S)/local -f $(K8S)
	kubectl -n $(NS) rollout restart deployment/llm-gateway deployment/otel-collector  # recargan sus ConfigMaps

azure-manifest: ## Muestra lo propio de Azure que genera Terraform (Key Vault, secretos, entorno)
	@terraform -chdir=$(TF_AZURE) output -raw kubernetes_azure

deploy-azure: k8s-config ## Despliega en AKS (tras terraform apply y az aks get-credentials)
	terraform -chdir=$(TF_AZURE) output -raw kubernetes_azure | kubectl apply -f -
	kubectl -n $(NS) rollout status deployment/secrets-sync --timeout=180s
	kubectl apply -f $(K8S)
	kubectl -n $(NS) rollout restart deployment/llm-gateway deployment/otel-collector

validate-k8s: ## kubeconform: manifiestos y render de prueba de la plantilla de Azure
	$(KUBECONFORM) $(K8S)/*.yaml $(K8S)/local/*.yaml
	@terraform -chdir=$(TF_AZURE) init -backend=false -input=false >/dev/null
	terraform -chdir=$(TF_AZURE) console < $(TF_AZURE)/tests/render-kubernetes.tfexpr | sed '1d;$$d' | $(KUBECONFORM) -

tf-validate: ## terraform fmt + validate (sin backend)
	cd $(TF_AZURE) && terraform fmt -check -recursive && terraform init -backend=false -input=false >/dev/null && terraform validate

HARNESSES := harness-engineering/harness-base/HARNESS harness-engineering/harness-base-olas/HARNESS
CORE := tools contracts templates agents bootstrap tests

harness-test: ## Validador y tests de los dos harnesses (base y olas)
	@for h in $(HARNESSES); do echo "→ $$h"; (cd $$h && python3 .claude/tools/validate_harness.py && python3 -m unittest discover -s .claude/tests -q) || exit 1; done

harness-drift: ## Comprueba que el núcleo del harness con olas es idéntico al de la base
	@for d in $(CORE); do diff -r -x __pycache__ -x test_ola.py harness-engineering/harness-base/HARNESS/.claude/$$d harness-engineering/harness-base-olas/HARNESS/.claude/$$d || exit 1; done
	@echo "✓ núcleo idéntico en harness-base y harness-base-olas"
