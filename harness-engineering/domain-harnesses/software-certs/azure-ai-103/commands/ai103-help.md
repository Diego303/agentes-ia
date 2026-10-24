---
description: Resumen de todos los comandos del harness AI-103 con explicación de cuándo usar cada uno. Útil para descubrir capacidades del vault.
allowed-tools: Read
---

# /ai103-help — Guía rápida del harness

Muestra al usuario un resumen organizado por fase:

```markdown
# 🧰 Harness AI-103 — Comandos disponibles

## 📝 Fase 1 — Generación de contenido
| Comando | Cuándo |
|---|---|
| `/ai103-status` | Ver dashboard de progreso. Cualquier momento. |
| `/ai103-next` | Generar siguiente archivo del orden pedagógico. |
| `/ai103-write <slug>` | Generar archivo específico. |
| `/ai103-batch <pattern>` | Generar varios archivos del mismo sub-dominio. |
| `/ai103-brief <slug>` | Expandir brief antes de dispatchar. |
| `/ai103-next-best` | Sugerencia inteligente del siguiente archivo (impacto + prerequisitos). |

## 🩺 Fase 2 — Validación y calidad
| Comando | Cuándo |
|---|---|
| `/ai103-review <slug>` | Re-revisar archivo ya generado. |
| `/ai103-validate [--scope]` | Health check completo del vault. |
| `/ai103-coverage` | Coverage report vs temario oficial Microsoft. |

## 📚 Fase 3 — Navegación y exploración
| Comando | Cuándo |
|---|---|
| `/ai103-deps <slug>` | Ver dependencias (in/out) de un archivo. |
| `/ai103-graph [--scope]` | Mermaid graph del wikilink graph. |
| `/ai103-glossary` | Glossary A-Z de términos del vault. |

## 🎓 Fase 4 — Estudio activo
| Comando | Cuándo |
|---|---|
| `/ai103-mock <scope>` | Mock exam estilo Microsoft (15-50 preguntas). |
| `/ai103-quiz <slug>` | Quiz corto (5 preguntas) sobre un archivo. |
| `/ai103-study-pack <scope>` | Agregados (trampas/mnemónicos/snippets/cheatsheets). |
| `/ai103-flashcards <scope>` | Flashcards Anki TSV. |
| `/ai103-study-route` | Plan personalizado de sesiones (semanas previas). |

## ⚙️ Meta
| Comando | Cuándo |
|---|---|
| `/ai103-help` | Este menú. |

## 📐 Convenciones
- **scope**: `slug` (un archivo), `<sub-dominio>` (e.g., `A.3`), `domain-X` (todo el dominio), `all`.
- **Archivos meta**: `INDICE-MAESTRO.md`, `PLAN.md`, `README.md` no se mueven.
- **Carpeta 00-Aggregations/**: outputs de los agentes agregadores.
- **Carpeta 00-Mock-Exams/**: mock exams generados.

## 🛡️ Seguridad
Todos los agentes con WebFetch tienen allowlist estricta a dominios Microsoft. Patrones de injection en contenido fetched son detectados, ignorados y reportados.
```

Sin argumentos. Solo lectura.
