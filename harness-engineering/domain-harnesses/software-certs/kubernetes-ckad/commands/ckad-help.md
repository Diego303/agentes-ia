---
description: Resumen de todos los comandos del harness CKAD con explicación de cuándo usar cada uno. Útil para descubrir capacidades del vault.
allowed-tools: Read
---

# /ckad-help — Guía rápida del harness CKAD

Muestra al usuario un resumen organizado por fase:

```markdown
# 🧰 Harness CKAD — Comandos disponibles

## 📝 Fase 1 — Generación de contenido
| Comando | Cuándo |
|---|---|
| `/ckad-status` | Ver dashboard de progreso. Cualquier momento. |
| `/ckad-next` | Generar siguiente archivo del orden pedagógico (auto-cycle author→reviewer). |
| `/ckad-write <slug>` | Generar archivo específico. |
| `/ckad-batch <pattern>` | Generar varios archivos del mismo sub-dominio en serie. |
| `/ckad-brief <slug>` | Expandir brief antes de dispatchar. |
| `/ckad-next-best` | Sugerencia inteligente del siguiente archivo (impacto + prerequisitos + peso CKAD). |

## 🩺 Fase 2 — Validación y calidad
| Comando | Cuándo |
|---|---|
| `/ckad-review <slug>` | Re-revisar archivo ya generado. |
| `/ckad-validate [--scope]` | Health check completo del vault (frontmatter, wikilinks, apiVersion sanity, YAML parse). |
| `/ckad-coverage` | Coverage report vs curriculum oficial CKAD (CNCF + LF Training). |
| `/ckad-version-check` | Detectar drift entre vault (`v1.35`) y versión K8s vigente. |

## 📚 Fase 3 — Navegación y exploración
| Comando | Cuándo |
|---|---|
| `/ckad-deps <slug>` | Ver dependencias (in/out) de un archivo. |
| `/ckad-graph [--scope]` | Mermaid graph del wikilink graph. |
| `/ckad-glossary` | Glossary A-Z de términos del vault. |

## 🎓 Fase 4 — Estudio y práctica
| Comando | Cuándo |
|---|---|
| `/ckad-mock <scope>` | Mock exam estilo CKAD (simulacro completo, performance-based). |
| `/ckad-quiz <slug>` | Quiz corto (5 preguntas inline) sobre un archivo. |
| `/ckad-lab <slug>` | Lab hands-on focalizado (drill build/modify/troubleshoot/refactor) — necesita cluster real. |
| `/ckad-study-pack <scope>` | Agregados (trampas/mnemónicos/snippets/cheatsheets). |
| `/ckad-flashcards <scope>` | Flashcards Anki TSV. |
| `/ckad-study-route` | Plan personalizado de sesiones (semanas previas al examen). |

## ⚙️ Meta
| Comando | Cuándo |
|---|---|
| `/ckad-help` | Este menú. |

## 📐 Convenciones
- **scope**: `slug` (un archivo), `<sub-dominio>` (e.g., `D.5`, `A.2`), `domain-X` (todo el dominio), `all`.
- **Archivos meta**: `INDICE-MAESTRO.md`, `PLAN.md`, `README.md` no se mueven.
- **Carpeta 00-Aggregations/**: outputs de los agentes agregadores (validation, coverage, glossary, graph, study-pack, flashcards).
- **Carpeta 00-Mock-Exams/**: mock exams generados (simulacros completos 2 h).
- **Carpeta 00-Labs/**: lab exercises hands-on (drill focalizado por slug, ~15-30 min cada uno).
- **Carpeta apuntes-base/**: archivos semilla originales del usuario (NO modificar; solo lectura).
- **Carpeta .claude/deprecated/**: harness AI-103 histórico (no se ejecuta).

## 🛡️ Seguridad anti-injection
Todos los agentes con WebFetch tienen allowlist estricta:
- `kubernetes.io/docs/` (primario)
- `helm.sh/docs/`, `kustomize.io`
- `github.com/kubernetes/*`, `github.com/kubernetes-sigs/*`, `github.com/helm/*`
- `cncf.io`, `training.linuxfoundation.org`
- `docs.docker.com` (solo Docker build images)

Patrones de injection en contenido fetched son detectados, ignorados y reportados.

## 🎯 Ruta sugerida de uso

**Generación inicial** (semanas 1-6):
```
/ckad-status            # ver donde estamos
/ckad-next-best         # qué generar primero
/ckad-next              # auto-pick + author + reviewer
# ... repetir hasta cubrir 77 archivos
```

**Validación** (al final de cada dominio):
```
/ckad-validate --scope domain-d
/ckad-coverage          # cross-check vs curriculum oficial
```

**Estudio + práctica** (últimas 4 semanas pre-examen):
```
/ckad-study-route                                 # plan personalizado
/ckad-study-pack all --type all
/ckad-flashcards all                              # Anki spaced rep diaria
/ckad-lab D6-config-secret-creation               # drill hands-on por slug (cluster real)
/ckad-mock domain-d                               # mock por dominio
/ckad-mock all                                    # full exam simulation 2 h
/ckad-version-check                               # check drift v1.35 → vigente (1 semana antes)
```

**Kubernetes version target**: v1.35 · **Score paso**: 66 % · **Duración examen**: 2 h
```

Sin argumentos. Solo lectura.
