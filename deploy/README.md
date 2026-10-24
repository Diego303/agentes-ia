# deploy

Contenedores, manifiestos de Kubernetes y Terraform (Azure). Sin Helm ni Kustomize: lo que se
aplica es lo que se lee en `deploy/kubernetes/`
([ADR 0008](../architecture/adr/0008-kubernetes-terraform.md)).

```text
deploy/
├── docker/Dockerfile           una imagen por servicio Python (--build-arg PACKAGE=...)
├── kubernetes/                 manifiestos iguales en todos los entornos (kubectl apply -f)
│   ├── namespace.yaml          Pod Security restricted
│   ├── serviceaccounts.yaml    una por workload, sin token de la API
│   ├── llm-gateway.yaml  ops-mcp.yaml  change-advisor.yaml  ops-agent.yaml  otel-collector.yaml
│   ├── networkpolicies.yaml    default-deny y solo los flujos del diagrama
│   └── local/                  solo kind: Jaeger, ConfigMap del entorno y plantillas de secretos
└── terraform/azure/            AKS, ACR, Key Vault, identidad de secretos y lo propio de Azure
    └── templates/kubernetes-azure.yaml.tftpl
```

## Qué cambia entre entornos

Los Deployments son los mismos en kind y en AKS. Lo que cambia queda fuera de ellos:

| Qué | Local (kind) | Azure (AKS) |
| --- | --- | --- |
| Secrets `<workload>-secrets` | `make k8s-secrets-local` desde `local/secrets/*.env` | Key Vault, sincronizado por el pod `secrets-sync` (driver CSI) |
| ConfigMap `opsagent-entorno` (backend de trazas, emisor de tokens) | `local/entorno.yaml` | generado por Terraform |
| Imágenes | `make images kind-load`: kind las carga | `make images push`: AKS las descarga del ACR |
| Backend de trazas | Jaeger (`local/jaeger.yaml`) | el OTLP que indiques en `otel_traces_backend` |

La configuración del gateway y del collector vive en un solo archivo cada una
(`llm-gateway/litellm-config.yaml`, `observability/collector/otel-collector.yaml`).
`make k8s-config` las convierte en ConfigMaps con `kubectl create configmap --from-file`.

Las imágenes se llaman igual en los dos entornos (`acropsagentdev.azurecr.io/<servicio>:0.1.0`).
Si tu ACR tiene otro nombre, cambia `REGISTRY` en el `Makefile` y la imagen de los tres
Deployments.

## Local (kind)

```bash
kind create cluster --name opsagent
for f in deploy/kubernetes/local/secrets/*.env.example; do cp "$f" "${f%.example}"; done   # rellena las claves
make images kind-load deploy-local
kubectl -n opsagent port-forward svc/ops-agent 8080   # API del agente
kubectl -n opsagent port-forward svc/jaeger 16686     # trazas
```

## Azure

```bash
cd deploy/terraform/azure
cp terraform.tfvars.example terraform.tfvars        # suscripción y backend de trazas
terraform init && terraform apply
# Valores reales de los secretos: nunca por Terraform.
az keyvault secret set --vault-name kv-opsagent-dev --name anthropic-api-key --value "$ANTHROPIC_API_KEY"
#   ... litellm-master-key, voyage-api-key, llm-gateway-key, mcp-tokens, mcp-token, a2a-tokens, advisor-token, agent-api-tokens
az acr login -n acropsagentdev && cd ../../.. && make images push
az aks get-credentials -g rg-opsagent-dev -n aks-opsagent-dev
make deploy-azure
```

`make deploy-azure` aplica lo que genera Terraform (`make azure-manifest` lo muestra):
- la `SecretProviderClass` del Key Vault;
- la ServiceAccount federada y el pod `secrets-sync`;
- el ConfigMap del entorno.

Espera a que los Secrets estén sincronizados y aplica `deploy/kubernetes/`.

## Postura de seguridad

| Control | Dónde |
| --- | --- |
| Pod Security Admission `restricted` en el namespace | `kubernetes/namespace.yaml` |
| No root, sin capabilities, seccomp `RuntimeDefault`, raíz de solo lectura (salvo el gateway) | cada Deployment |
| ServiceAccount por workload, sin token de la API montado | `kubernetes/serviceaccounts.yaml` |
| NetworkPolicy *default-deny*; solo los flujos del diagrama; solo el gateway sale a Internet (443) | `kubernetes/networkpolicies.yaml` |
| Workloads sin identidad de Azure: solo leen su Secret | Deployments (`envFrom`) |
| Secretos desde Key Vault; la identidad de sincronización solo lee los secretos de la app, uno a uno; los valores no pasan por el state | `terraform/azure/main.tf`, plantilla de Azure |
| AKS sin cuentas locales, Azure RBAC, OIDC y Workload Identity, Cilium | `terraform/azure/main.tf` |
| ACR sin usuario admin; el kubelet descarga imágenes con AcrPull | `terraform/azure/main.tf` |

## Validación (CI)

```bash
make validate-k8s   # kubeconform -strict (Kubernetes 1.37 y CRDs) de los manifiestos y de un render de la plantilla de Azure
make tf-validate    # terraform fmt -check + validate (azurerm 5.11)
```
