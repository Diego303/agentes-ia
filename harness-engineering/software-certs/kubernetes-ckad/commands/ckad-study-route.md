---
description: Ruta de estudio personalizada CKAD por dominio. Order de archivos respetando prerequisitos (wikilinks foundational antes), agrupados por sesión de 60-90 min. Para preparar plan de revisión las semanas previas al examen.
allowed-tools: Read, Bash, Glob, Grep, AskUserQuestion
---

# /ckad-study-route — Ruta de estudio personalizada CKAD

## Pasos

1. Pregunta al usuario con `AskUserQuestion`:
   - **Tiempo total disponible** (horas): e.g., 20h, 40h, 80h.
   - **Tiempo por sesión** (min): e.g., 60, 90, 120.
   - **Dominios a priorizar**: e.g., todos / solo D (peso 25 %) / focus en hands-on.
   - **Nivel actual**: principiante (todo desde 0) / intermedio (revisar) / experto (solo trampas).
   - **Acceso a cluster**: tienes kind/minikube/killercoda para hands-on? (sí/no afecta el ratio práctica/teoría).

2. Calcula plan:
   - Archivos por sesión = (tiempo_sesion_min / 15) × factor_dificultad.
   - Order recomendado:
     - 00-Foundational primero.
     - Domain D (25 %, mayor peso) tras foundational.
     - Domain A (workloads — base para D y E).
     - Domain B (deployment strategies).
     - Domain E (services + networking).
     - Domain C (observability — útil pero menor peso 15 %).
   - Respeta prerequisitos: wikilinks foundational antes de los que los usan.

3. Output al usuario:

```
📅 Plan de estudio CKAD (X sesiones × Y min)

## Semana 1 — Foundational + arranque Domain D
- **Sesión 1** (60 min): Foundational (00-kubectl-fundamentos, 00-yaml-manifest-anatomy)
- **Sesión 2** (60 min): Foundational (00-imperativo-vs-declarativo, 00-labels-selectors-annotations, 00-namespaces)
- **Sesión 3** (90 min): Foundational restante + D5 ConfigMaps
- ...

## Semana 2 — Domain D (peso máximo 25 %)
- **Sesión 4** (90 min): D6 Secrets (3 archivos)
- **Sesión 5** (90 min): D4 Resource Requirements (3 archivos)
- **Sesión 6** (60 min): D7 Security Contexts (2 archivos)
- **Sesión 7** (90 min): D2 Auth + RBAC (3 archivos)
- **Sesión 8** (60 min): D3 ServiceAccount + D1 CRDs
- ...

## Semana 3 — Domain A (workloads)
- **Sesión 9-12**: A1 Container Images, A2 Workload Resources, A3 Multi-Container, A4 Volumes
- ...

## Semana 4 — Domain B + E
- ...

## Semana 5 — Domain C + revisión + mock exams
- Sesión final de cada semana → mock exam del dominio recién estudiado
- /ckad-mock domain-d (90 min cronometrado)
- /ckad-mock all (full 2h simulation)

## Última semana — Revisión final
- /ckad-study-pack all --type all
- /ckad-mock all (full exam simulation con cluster en vivo)
- /ckad-flashcards all (Anki spaced repetition diaria)
```

4. Pregunta si quiere guardar el plan en `00-Aggregations/study-route-<fecha>.md`.

## Reglas

- Adapta el plan al perfil del usuario (no genérico).
- Última sesión de cada semana → mock exam.
- Última semana → solo agregados + flashcards (NO mock exams, mantén energía mental fresca).
- Si el usuario tiene cluster, recomienda 70 % hands-on / 30 % lectura. Sin cluster, 50/50.

$ARGUMENTS
