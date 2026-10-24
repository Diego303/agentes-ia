# 🧠 Harness CKAD — Vista rápida

> Sistema de orquestación de agentes + slash commands para construir y estudiar con un vault Obsidian de **77 archivos atómicos** orientados a la certificación **CKAD** (Certified Kubernetes Application Developer · CNCF / Linux Foundation · Kubernetes v1.35).

---

## 🗂️ Contenido e instalación

```
kubernetes-ckad/
├── README.md               ← este archivo
├── settings.json.example   ← permisos WebFetch (allowlist CKAD)
├── agents/                 ← 10 sub-agentes especializados (todos ckad-*)
└── commands/               ← 20 slash commands invocables por el usuario
```

El harness vive dentro del vault de apuntes. Todas las rutas de agentes y
comandos son **relativas a la raíz del vault** (el directorio donde abres Claude Code):

```bash
mkdir -p <vault>/.claude
cp -r agents commands <vault>/.claude/
cp settings.json.example <vault>/.claude/settings.local.json
cd <vault> && claude
```

## 🤖 Agentes (`agents/`) — 10

| Agente | Color | Rol |
|---|---|---|
| `ckad-author.md` | 🔵 | Genera archivos atómicos con ULTRATHINK + 3 iteraciones + rúbrica ≥ 9 |
| `ckad-reviewer.md` | 🔴 | Revisor independiente, contexto limpio, gate de calidad |
| `ckad-fact-checker.md` | 🟡 | Dossier verbatim contra `kubernetes.io/docs/` (opcional pre-author) |
| `ckad-vault-validator.md` | 🟠 | Health check: frontmatter, YAML parse, apiVersion sanity |
| `ckad-mock-exam-builder.md` | 🟣 | Mock exams performance-based estilo CKAD (simulacro completo) |
| `ckad-coverage-analyst.md` | 🌸 | Cross-check vs curriculum oficial CNCF |
| `ckad-organizer.md` | 🟢 | Reorganiza vault + genera `_index.md` por carpeta |
| `ckad-flashcard-generator.md` | 🟡 | TSV Anki spaced-repetition |
| `ckad-study-aggregator.md` | 🔵 | Cheatsheets + traps + mnemónicos consolidados |
| `ckad-lab-generator.md` | 🟦 | Lab exercises hands-on (build/modify/troubleshoot/refactor) para cluster real |

## 🧰 Commands (`commands/`) — 20

20 slash commands organizados por fase. Ejecuta `/ckad-help` dentro de Claude Code para verlos.

| Fase | Commands |
|---|---|
| 1 — Generación | `/ckad-status`, `/ckad-next`, `/ckad-next-best`, `/ckad-write`, `/ckad-batch`, `/ckad-brief` |
| 2 — Calidad | `/ckad-review`, `/ckad-validate`, `/ckad-coverage`, `/ckad-version-check` |
| 3 — Navegación | `/ckad-deps`, `/ckad-graph`, `/ckad-glossary` |
| 4 — Estudio + práctica | `/ckad-mock`, `/ckad-quiz`, `/ckad-lab`, `/ckad-study-pack`, `/ckad-flashcards`, `/ckad-study-route` |
| Meta | `/ckad-help` |

## 🛡️ Allowlist WebFetch (`settings.json.example` → `.claude/settings.local.json`)

```json
{
  "permissions": {
    "allow": [
      "WebSearch",
      "WebFetch(domain:kubernetes.io)",
      "WebFetch(domain:helm.sh)",
      "WebFetch(domain:kustomize.io)",
      "WebFetch(domain:github.com)",
      "WebFetch(domain:cncf.io)",
      "WebFetch(domain:training.linuxfoundation.org)",
      "WebFetch(domain:docs.docker.com)"
    ]
  }
}
```

**Documentación oficial primaria**: https://kubernetes.io/docs/

El pattern `WebFetch(domain:kubernetes.io)` cubre TODO el subdominio incluyendo `/docs/`, `/blog/`, `/community/`, etc.

## 🔄 Flujo end-to-end (auto-cycle de generación)

```
Usuario invoca → /ckad-next
                      ↓
              Orquestador lee INDICE-MAESTRO + PLAN.md
                      ↓
              (Opcional) Dispatch ckad-fact-checker → dossier
                      ↓
              Dispatch ckad-author con brief + dossier
                      ↓
              ckad-author: ultrathink + 3 iteraciones + rúbrica
                      ↓
              Dispatch ckad-reviewer (contexto limpio)
                      ↓
              Si ✅ APROBADO → marca ✅ en INDICE
              Si ❌ RECHAZADO → re-dispatch author (max 2 ciclos)
                      ↓
              Reporte al usuario + siguiente sugerido
```

## 📐 Convenciones del vault

- **Frontmatter obligatorio**: `tema`, `dominio_examen`, `peso_en_examen`, `dificultad`, `prioridad_examen`, `verificado_fecha`, `kubernetes_version: v1.35`, `fuentes`, `tags`.
- **9 secciones obligatorias** por archivo atómico: TL;DR + Relevancia + Concepto + Cómo se hace (kubectl + YAML + Helm/Kustomize cuando aplique) + Tablas + Trampas (≥5) + Mnemotecnia + Conceptos relacionados + Autotest + Control de calidad.
- **Wikilinks** `[[slug]]` por nombre (Obsidian resuelve por basename).
- **Idioma**: prosa en español, términos técnicos en inglés (`Pod`, `Deployment`, `kubectl apply`).

## 📁 Carpetas de output del vault

- `00-Aggregations/` — outputs de validation, coverage, glossary, graph, study-pack, flashcards.
- `00-Mock-Exams/` — mock exams generados (simulacros completos 2 h).
- `00-Labs/` — lab exercises hands-on (drill por slug, ejecutables contra cluster real).

## 📚 Harness hermano

Este harness deriva del de AI-103 (Azure AI), que está en
[`../azure-ai-103/`](../azure-ai-103/) con la misma estructura (9 agentes
`ai103-*` y 18 commands `ai103-*`). Para otra certificación, copia uno de los dos
y renombra el prefijo, el temario y las fuentes oficiales.

---

*Harness CKAD versión 1.0 · Bootstrap 2026-05-24 · Kubernetes target v1.35.*
