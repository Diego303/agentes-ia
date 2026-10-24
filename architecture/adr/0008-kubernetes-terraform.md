# 0008 · Manifiestos de Kubernetes y Terraform, sin Helm ni Kustomize

**Estado**: aceptada

## Contexto

El destino es Kubernetes (AKS en producción, kind en local). Hay que gestionar
configuración por entorno, secretos e identidad, y que lo que se aplica se pueda leer tal
cual.

## Decisión

- **Manifiestos planos, iguales en todos los entornos** (`deploy/kubernetes/*.yaml`), con
  `kubectl apply -f`. Lo que cambia entre entornos queda fuera de los Deployments:
  - los secretos, en Secrets `<workload>-secrets` que los pods leen con `envFrom`;
  - los valores de entorno (backend de trazas, emisor de tokens), en el ConfigMap
    `opsagent-entorno`;
  - la imagen tiene el mismo nombre en local y en AKS: kind la carga y AKS la descarga del
    ACR.
- **La configuración vive en un solo archivo por componente** (`llm-gateway/litellm-config.yaml`,
  `observability/collector/otel-collector.yaml`). Se convierte en ConfigMap con
  `kubectl create configmap --from-file`, sin copiarla dentro de un manifiesto.
- **Terraform crea la infraestructura de Azure** (AKS con OIDC y Workload Identity, Azure
  CNI overlay con Cilium y sin cuentas locales, ACR sin usuario admin, Key Vault con RBAC) y
  **genera lo propio de Azure** desde sus outputs: la `SecretProviderClass`, la
  ServiceAccount federada y el ConfigMap del entorno (output `kubernetes_azure`).
- **Secretos**: en local, desde archivos `.env` que no se versionan. En Azure, desde Key
  Vault:
  - un pod `secrets-sync` monta el Key Vault con el driver CSI y lo sincroniza en los
    Secrets;
  - su identidad solo lee los secretos de la aplicación, uno a uno;
  - los valores nunca pasan por el state de Terraform.
- **Seguridad por defecto**:
  - namespace con Pod Security `restricted`;
  - NetworkPolicy *default-deny*, y solo el gateway sale a Internet;
  - contenedores no root, sin capabilities y con sistema de archivos de solo lectura
    (salvo el gateway, documentado).

## Alternativas

- **Helm**. Plantillas potentes, pero para una aplicación propia añaden una capa que hay
  que renderizar para saber qué se aplica.
- **Kustomize con overlays**. Evita duplicar, pero los parches y los `replacements` reparten
  un mismo Deployment entre varios archivos. Con los Deployments iguales en todos los
  entornos no hace falta.
- **CSI en cada Deployment, con una identidad por workload**. Da mínimo privilegio por
  workload dentro del Key Vault, pero obliga a Deployments distintos en Azure y en local.
  Con un pod de sincronización, los workloads no tienen identidad de Azure y la del pod solo
  lee los secretos de la aplicación.
- **Workloads desplegados con el proveedor de Kubernetes de Terraform**. Una sola
  herramienta, pero el state guardaría los Secrets y el clúster pasaría a depender del
  apply de Terraform.

## Consecuencias

- Lo que se aplica es exactamente lo que se lee en `deploy/kubernetes/`. El CI lo valida
  con `kubeconform -strict`, junto con un render de prueba de la plantilla de Azure.
- Un cambio en `litellm-config.yaml` o en la configuración del collector se aplica con
  `make k8s-config` y un `rollout restart`, que `make deploy-*` ya hace.
- El pod `secrets-sync` es una pieza más que vigilar: si no está en marcha, los Secrets no
  se actualizan, aunque los que ya existen siguen funcionando.
