---
description: Genera lab exercises hands-on focalizados para práctica con cluster (kind/minikube/killercoda). Distinto a mock-exam: drill exercises sobre UN concepto con starting state, tareas, criterios y solución. Argumento: slug específico o sub-dominio. Variantes: build / modify / troubleshoot / refactor.
allowed-tools: Read, Write, Bash, Glob, Grep, Agent, AskUserQuestion
---

# /ckad-lab — Generar lab hands-on

Eres el orquestador. El usuario quiere ejercicios prácticos para construir muscle memory kubectl.

## Argumento

- **$ARGUMENTS** = scope:
  - **Slug específico** (ej. `D6-config-secret-creation`) — genera 1-4 variantes (build, modify, troubleshoot, refactor).
  - **Sub-dominio** (ej. `D.6`) — pregunta cuántos archivos y qué variantes.
  - Sin args → ofrece con `AskUserQuestion` los 3 archivos más recientemente generados.

## Pasos

### 1. Resolver scope

1. Verificar que el slug/archivo exista en el vault (`Glob`).
2. Si el archivo NO está generado aún (⬜ en INDICE), sugiere generarlo primero con `/ckad-write <slug>` antes del lab.

### 2. Confirmación de variantes

Pregunta con `AskUserQuestion`:
- **Variantes a generar**: build / modify / troubleshoot / refactor / todas las que apliquen.
- **Difficulty**: easy / medium / hard / mix (default: mix progresivo).
- **Cluster disponible**: kind / minikube / killercoda / k3s / k3d (afecta cleanup commands).

### 3. Crear dir si no existe

```bash
mkdir -p /mnt/d/GitHub/LOCAL/DIEGO/APUNTES/ckad/00-Labs/
```

### 4. Dispatch al agente

Llama a `ckad-lab-generator` con:
- scope (slug)
- variants (lista confirmada)
- difficulty
- output dir: `00-Labs/`

### 5. Esperar reporte

El agente genera 1 archivo por variante (`lab-<slug>-build-<YYYYMMDD>.md`, etc.).

### 6. Reportar al usuario

Mostrar:
- Path(s) generados.
- Total de tareas + tiempo estimado.
- Sugerencia de orden de ejecución (build → modify → refactor → troubleshoot).
- Instrucciones rápidas:

```
Para ejecutar el lab:
1. Activa tu cluster:
   - kind: kind create cluster --name ckad-practice
   - minikube: minikube start --profile=ckad
   - killercoda: usa el playground de killercoda.io
2. Abre el lab.md y sigue las secciones en orden.
3. Cronómetro recomendado: ~<X> min total.
4. Mira la solución SOLO al final.
```

## ⚠️ Reglas

- **No generes lab si el archivo source no está ✅ generado todavía** (sin docs base, el lab no tendría calidad).
- **Crea `00-Labs/` dir** si no existe.
- Si scope es sub-dominio con >3 archivos, confirma con usuario (puede ser sesión larga).
- Optimiza para **práctica focalizada**, no simulacro de examen completo (para eso /ckad-mock).

## 🎯 Recomendación de uso

Workflow ideal:
1. Genera un archivo del vault: `/ckad-write D6-config-secret-creation`.
2. Lee el archivo (estudia conceptos).
3. Genera lab: `/ckad-lab D6-config-secret-creation`.
4. Ejecuta lab en cluster: 15-30 min hands-on.
5. Si dudas → vuelve al archivo.
6. Pasa al siguiente slug.

Tras completar un dominio completo, ejecuta `/ckad-mock domain-<X>` como simulacro consolidado.

$ARGUMENTS
