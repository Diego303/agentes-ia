---
description: Extrae términos técnicos con definiciones across todos los archivos del vault CKAD. Genera glossary consolidado A-Z. Útil para revisión final y verificar uso consistente de nomenclatura.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# /ckad-glossary — Glossary del vault CKAD

## Pasos

1. `Glob` para listar archivos atómicos.
2. Para cada uno, extrae:
   - **Bolds** (`**término**`) que aparezcan en TL;DR o en sección "Concepto en profundidad" como introducción de concepto.
   - **Kinds K8s** verbatim (`Pod`, `Deployment`, `StatefulSet`, `CronJob`, `ConfigMap`, `Secret`, `NetworkPolicy`...).
   - **apiVersions** (`apps/v1`, `batch/v1`, `networking.k8s.io/v1`...).
   - **Campos YAML clave** (e.g., `spec.containers[].resources`, `spec.selector.matchLabels`).
   - **Comandos kubectl/helm/kustomize** únicos (e.g., `kubectl rollout undo`, `helm upgrade --install`, `kubectl apply -k`).
   - **Acrónimos** (e.g., RBAC, CRD, PV, PVC, SC, HPA, QoS, SA, CNI, CRI, OCI, NS, IPVS, OOMKilled) — busca patrones MAYÚSCULAS.
   - **Componentes named** (e.g., "Metrics Server", "CoreDNS", "kube-proxy", "containerd").
3. Por cada término extraído:
   - Si aparece en N archivos, anota frequency.
   - Toma la definición del primer párrafo donde aparece (heurística: oración con verbo "es/son/contains/refers to").
4. Consolida A-Z:
   - Deduplica.
   - Group por categoría (Kinds / Resources / Commands / Conceptos / Acrónimos / Patterns).
5. Output `00-Aggregations/glossary-ckad.md`:

```markdown
# 📘 Glossary CKAD

## A
- **apiVersion** — Campo obligatorio en cualquier manifest K8s indicando grupo y versión de API (e.g., `apps/v1`, `v1`, `batch/v1`). → ver [[00-api-versions-deprecations]]
- **Affinity** — Mecanismo de scheduling para preferir/forzar Pods en nodos con ciertas labels. → ver [[D8-config-node-selectors-affinity]]
- ...

## B
- **backoffLimit** — Campo de Job: número de reintentos antes de marcar como Failed (default 6). → ver [[A2-design-job]]
- **BestEffort** — QoS class de Pod sin requests/limits. Primero en eviction. → ver [[D4-config-resource-requests-limits-qos]]
- ...

## Acrónimos
- **CKAD** — Certified Kubernetes Application Developer.
- **CNI** — Container Network Interface.
- **CRI** — Container Runtime Interface.
- **CRD** — CustomResourceDefinition.
- **HPA** — HorizontalPodAutoscaler.
- **OOMKilled** — Out-Of-Memory killed (exit 137).
- **PV / PVC / SC** — PersistentVolume / PersistentVolumeClaim / StorageClass.
- **QoS** — Quality of Service (Guaranteed/Burstable/BestEffort).
- **RBAC** — Role-Based Access Control.
- **SA** — ServiceAccount.
- ...
```

## Reglas

- Solo análisis local.
- Atribuye cada término al archivo donde se define mejor (primer aparición con definición clara).
- No inventar definiciones; usar lo que dicen los archivos.

$ARGUMENTS
