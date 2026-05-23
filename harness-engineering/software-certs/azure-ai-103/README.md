
 🧠 Cómo funciona (el flujo)

  sequenceDiagram
      participant U as Usuario
      participant O as Orquestador (este chat)
      participant FC as ai103-fact-checker
      participant A as ai103-author
      participant R as ai103-reviewer

      U->>O: /ai103-next (o /ai103-write <slug>)
      O->>O: Lee PLAN.md, extrae brief del slug
      O->>FC: (opcional) verifica hechos críticos
      FC-->>O: dossier verbatim
      O->>A: dispatch con brief + dossier
      A->>A: ultrathink + 3 iteraciones + rúbrica
      A-->>O: archivo escrito + reporte (<400 palabras)
      O->>R: dispatch revisión independiente
      R->>R: cross-check brief + URLs oficiales
      R-->>O: dictamen + scores rúbrica
      alt RECHAZADO
          O->>A: re-dispatch con correcciones (max 2 ciclos)
      end
      O->>O: marca ✅ en INDICE-MAESTRO
      O-->>U: reporte conciso + próximo sugerido

🎯 Calidad encoded en el harness

agents/
      │   ├── ai103-author.md          (Opus · ultrathink · 3-iter + rúbrica)
      │   ├── ai103-reviewer.md        (Opus · revisor independiente, sin contexto del autor)
      │   └── ai103-fact-checker.md    (Opus · verifica contra Microsoft Learn)

  ┌───────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────┐
  │        Encoded en         │                                      Garantiza                                      │
  ├───────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────┤
  │ ai103-author system       │ Nivel doctoral, ultrathink, 3 iteraciones, rúbrica ≥9, Python-only, frontmatter     │
  │ prompt                    │ Obsidian, ⚠️ para incertidumbres                                                    │
  ├───────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────┤
  │ ai103-reviewer system     │ Contexto limpio (no ve proceso del autor), cross-check ≥3 hechos contra Microsoft   │
  │ prompt                    │ Learn, dictamen estructurado con acciones correctivas                               │
  ├───────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────┤
  │ ai103-fact-checker system │ Solo fuentes oficiales (Microsoft Learn, PyPI Azure, GitHub Azure), copia verbatim, │
  │  prompt                   │  fechas de actualización                                                            │
  ├───────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────┤
  │ PLAN.md briefs            │ Sub-puntos verbatim del temario AI-103, URLs específicas, wikilinks, trampas        │
  │                           │ concretas                                                                           │
  ├───────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────┤
  │ Skills                    │ Ciclo automático autor→reviewer→marca-completado, max 2 ciclos de corrección antes  │
  │                           │ de pedir intervención                                                               │
  └───────────────────────────┴─────────────────────────────────────────────────────────────────────────────────────┘

  🚀 Cómo empezar a usarlo

  Reinicia Claude Code en este directorio (o sigue en esta sesión; al estar en el cwd, los agentes y skills
  proyecto-scoped son detectables). Luego:

  ┌────────────────────────────────────────────────┬────────────────────────────────────────────────────────────────┐
  │                    Comando                     │                           Resultado                            │
  ├────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ /ai103-status                                  │ Dashboard: 4/168 completados (2.4%), desglose por dominio,     │
  │                                                │ sugerencia de siguiente                                        │
  ├────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ /ai103-next                                    │ Sigo orden pedagógico, dispatch autor+reviewer, devuelvo       │
  │                                                │ reporte conciso                                                │
  ├────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ /ai103-write                                   │ Genero archivo específico por slug                             │
  │ plan-deployment-options-models-agents          │                                                                │
  ├────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ /ai103-batch A.3                               │ Genero TODOS los archivos de A.3 (security) en serie con       │
  │                                                │ confirmación previa                                            │
  ├────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ /ai103-review <slug>                           │ Re-reviso un archivo ya escrito                                │
  ├────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ /ai103-brief <slug>                            │ Expando un brief antes de dispatchar (útil si PLAN.md está     │
  │                                                │ escueto)                                                       │
  └────────────────────────────────────────────────┴────────────────────────────────────────────────────────────────┘

  ⚙️ Configuración recomendada antes de lanzar

  Hay UN paso opcional pero útil: permite explícitamente a los agentes el uso de WebFetch/WebSearch en
  .claude/settings.local.json para que no haga prompt cada vez. Mira si lo configuras o lo dejas para que pregunten.