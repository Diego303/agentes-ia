# HARNESS · Coach de fuerza/hipertrofia

Sistema general de agentes y skills para programación de entrenamiento (fuerza, hipertrofia, rendimiento general), auditoría de planes, reajustes por disrupciones (vacaciones/lesiones/eventos vitales), generación de manuales operativos editoriales HTML, coaching en tiempo real, y análisis longitudinal de bitácoras. Aplicable a cualquier humano con vida activa que busque mejora medible.

Para usar en futuros proyectos con cualquier perfil de usuario (hombre/mujer, principiante/intermedio/avanzado, lifter/runner/triatleta/persona activa). Solo necesitas adaptar los **valores numéricos** al perfil concreto — los **principios, fórmulas, protocolos y plantillas son invariantes**.

---

## Filosofía · general vs ejemplos del perfil de referencia

Este harness se construyó a partir de un caso real de uso (un atleta intermedio natural masculino con restricciones específicas). Los **principios, protocolos, formulas y templates son completamente generales**.

Los **ejemplos numéricos concretos** (cuando aparecen pesos como 85 kg, fechas como 19 oct 2026, etc.) son del **perfil de referencia** del caso de estudio:

> **Perfil de referencia del caso de estudio**:
> - Hombre · intermedio natural · ~80 kg corporal · 3 años entrenando
> - PRs partida: bench 85 kg · sentadilla 110 kg · HT 120×8 · prensa 190×8
> - Targets macro: bench 92,5 / sentadilla 125 / HT 130×8 / prensa 220×8
> - Restricciones: 6 h sueño consolidadas · 3 días/sem · rodilla sensible · hora 20-21 h hardcoded
> - Duración: 17 semanas + 1 deload post-test
>
> **Si tu perfil es distinto** (mujer · principiante · runner · triatleta · senior · sin restricciones · con más sesiones/semana):
> - Las **fórmulas** (Epley, Mifflin, ratio doble columna, cafeína mg/kg) se recalculan con tus números.
> - Los **principios** (DUP, deload cada 4-5 sem, frecuencia 2× por grupo, autorregulación por RPE/AMRAP) son invariantes.
> - Los **protocolos** (RECON, taper, ritual mental, deuda sueño) son invariantes.
> - Las **plantillas** (Telegram, manual HTML, quick-ref, report quirúrgico) son invariantes en estructura.
> - **Solo los pesos absolutos en kg, las recetas concretas, las fechas, y la elección de lifts principales** cambian de un perfil a otro.

Cada skill que usa estos números lo declara explícitamente al inicio con una nota visible. **Adapta los valores a tu usuario real antes de aplicar**.

**Skills 100 % generales** (sin números específicos · directamente aplicables):
- accessory-technique-reference, body-composition-tracking, bracing-valsalva, coaching-principles, daily-morning-check, deload-by-session, deload-week-design, disruption-adaptation-framework, editorial-data-viz, editorial-html-template, editorial-writing-rules, exercise-substitution-matrix, harness-self-audit, lift-technique-reference, longitudinal-analysis-dimensions, manual-expansion-rules, mental-game-plateau, mobile-quick-template, mobility-prehab-by-joint, multi-macro-roadmap, peak-week-tapering, plan-abc-knee, pre-session-mental-prep, rpe-scale, sleep-debt-protocol, support-gear-protocol, surgical-4-pass-methodology, surgical-report-structure, telegram-template-library, troubleshooting-catalog, warmup-calculator

**Skills con ejemplos del perfil de referencia** (etiquetados explícitamente · adaptables):
- amrap-tree, bench-dual-column, calendar-arithmetic, cardio-z2, epley-formula, hip-thrust-reentry, micro-celebraciones, nutrition-complete, periodization-design, plan-audit-checklist, recon-protocols, recovery-smr, telegram-tracking, test-day-protocol, vacation-bw-routine, volume-landmarks-mev-mav-mrv

---

## Estructura

```
HARNESS/
├── README.md                          ← este archivo
├── agents/                            ← roles especialistas (multi-step)
│   ├── gym-plan-architect.md          Diseña macrociclos completos desde perfil
│   ├── plan-auditor.md                Audita planes existentes (math/dates/refs)
│   ├── plan-reajuster.md              Reorganiza calendario tras disrupciones
│   ├── manual-html-builder.md         Construye manuales operativos HTML editoriales
│   ├── quick-ref-builder.md           Construye rutinas rápidas mobile-first
│   ├── recovery-optimizer.md          Diseña infraestructura recuperación (sueño/SMR/Z2/nutrición)
│   ├── coach-realtime.md              Coach en tiempo real para dudas operativas
│   └── surgical-report-builder.md     Informes longitudinales quirúrgicos (4-pass + ultrathink)
└── skills/                            ← conocimiento/templates reusable
    │
    │ ─── PROGRAMACIÓN Y CÁLCULOS ───
    ├── epley-formula.md               Cálculo 1RM + ratio shortcut
    ├── rpe-scale.md                   Escala RPE con señales físicas
    ├── amrap-tree.md                  Árbol AMRAP de decisión
    ├── periodization-design.md        DUP intra-semanal + bloques + deload + hitos
    ├── coaching-principles.md         10 principios rectores de programación
    ├── volume-landmarks-mev-mav-mrv.md   MEV/MAV/MRV operativos por grupo
    ├── plan-abc-knee.md               Plan A/B/C rodilla
    ├── exercise-substitution-matrix.md  Matriz por articulación y equipo (generaliza A/B/C)
    ├── bench-dual-column.md           Sistema doble columna 1RM bench
    ├── hip-thrust-reentry.md          Re-entry HT tras pausa larga
    ├── calendar-arithmetic.md         Aritmética calendario (fechas, sesiones, weeks)
    │
    │ ─── RECUPERACIÓN, NUTRICIÓN, EJECUCIÓN ───
    ├── sleep-debt-protocol.md         Protocolo deuda sueño (1, 2-3, 4+ noches)
    ├── daily-morning-check.md         Chequeo 60s al despertar (FC + sueño + sensación)
    ├── nutrition-complete.md          Mifflin + macros + tomas + cafeína + recetas
    ├── recovery-smr.md                SMR/foam roll por día
    ├── mobility-prehab-by-joint.md    Mobility activa pre-sesión (≠ SMR)
    ├── cardio-z2.md                   Cardio Z2 protocolo + verificación
    ├── lift-technique-reference.md    Técnica detallada de los compuestos (+ deadlift)
    ├── accessory-technique-reference.md  Técnica de 12 ejercicios accesorios
    ├── bracing-valsalva.md            Bracing 360° + Valsalva por intensidad
    ├── support-gear-protocol.md       Cinturón, muñequeras, mangas, agarres
    ├── warmup-calculator.md           Tabla warm-up por intensidad work-set
    ├── pre-session-mental-prep.md     Ritual mental + activación 5 min pre-sesión
    │
    │ ─── DELOADS, EVENTOS Y DISRUPCIONES ───
    ├── deload-week-design.md          Estructura de sem deload (sem 5, 10)
    ├── deload-by-session.md           Deload de sesión única (entre normal y semana)
    ├── peak-week-tapering.md          Taper neural sem 15 pre-test
    ├── test-day-protocol.md           Pre-test, día, regla fallido (3 intentos universal)
    ├── vacation-bw-routine.md         Rutina BW vacaciones
    ├── recon-protocols.md             RECON-1 / RECON-2 + creatina re-saturación
    ├── disruption-adaptation-framework.md  Meta-protocolo reajuste de macros
    ├── troubleshooting-catalog.md     25+ escenarios comunes con acción
    │
    │ ─── TRACKING, ADHERENCIA Y META-PLANNING ───
    ├── telegram-tracking.md           Cabecera + notación
    ├── telegram-template-library.md   Biblioteca de 14 familias de plantillas
    ├── micro-celebraciones.md         Sistema de micro-wins para adherencia
    ├── mental-game-plateau.md         Gestión de pozos mentales mid-macro
    ├── body-composition-tracking.md   Báscula + medidas + fotos + Mifflin recal
    ├── multi-macro-roadmap.md         Planning 12-24m · rotación prioridades
    │
    │ ─── ANÁLISIS LONGITUDINAL Y AUDITORÍA ───
    ├── surgical-4-pass-methodology.md Metodología 4-pase con ultrathink loop
    ├── longitudinal-analysis-dimensions.md  Catálogo 25 dimensiones
    ├── plan-audit-checklist.md        Checklist exhaustivo de auditoría
    ├── harness-self-audit.md          Meta-auditoría del propio harness (7 capas)
    │
    │ ─── PRODUCCIÓN EDITORIAL Y ENTREGABLES ───
    ├── manual-expansion-rules.md      Filosofía "explicar vs diseñar" + 5 tests
    ├── editorial-html-template.md     CSS + tipografía + paleta editorial
    ├── editorial-writing-rules.md     5 reglas de escritura editorial
    ├── editorial-data-viz.md          Estilo matplotlib + 14 tipos de plot
    ├── surgical-report-structure.md   Estructura HTML del informe quirúrgico
    └── mobile-quick-template.md       Template mobile-first compacto
```

---

## Filosofía base · qué asume este harness

El harness está calibrado para perfil intermedio natural masculino con restricciones reales (no atleta de élite con sueño 8 h y 5 días). Asume:

- **3-4 sesiones/semana** como máximo realista
- **6-7 h de sueño consolidadas** como restricción frecuente (común en padres con hijo pequeño)
- **Posibles molestias articulares** (rodilla, hombro) que requieren contingencias
- **Adherencia psicológica** como factor crítico para macros largos (17+ semanas)
- **Honestidad en targets**: probabilidades 70-80% de éxito, no promesas de 100%

Si tu usuario es atleta de élite con todo bajo control, este harness puede subestimar lo que es posible. Si es principiante absoluto, puede sobrestimar la complejidad necesaria.

---

## Perfiles compatibles · más allá del caso de estudio

| Perfil | Compatibilidad | Skills que requieren mayor adaptación |
|---|---|---|
| Hombre intermedio natural (perfil de referencia) | 100% | ninguno |
| Mujer intermedia natural | 95% | nutrition-complete (Mifflin tiene fórmula mujer · ajustar), bench-dual-column (escala pesos), micro-celebraciones (PRs femeninos distintos) |
| Principiante absoluto (< 1 año) | 70% | periodization-design (DUP innecesario · usar linear), coaching-principles (algunos no aplican), volumen recuperable (más alto) |
| Avanzado / elite (> 5 años) | 80% | volumen recuperable (más alto), frecuencia (más alta), deload (cada 3 sem) |
| Senior (50+) | 85% | recovery-smr (más frecuente), sleep-debt-protocol (umbrales distintos), nutrition (proteína techo 2 g/kg), test-day (intentos más conservadores) |
| Runner / triatleta | 75% | cardio-z2 es central (no opcional), test-day mide tiempo no peso, periodization-design adapta a periodización deportiva, lift-technique-reference solo para crossover |
| Persona activa sin objetivo competitivo | 90% | test-day-protocol opcional, micro-celebraciones más flexibles, target macros más generosos |

**En todos los casos**: el harness es punto de partida, no jaula. Adapta lo que aplique.

---

## Matriz de cobertura · pregunta operativa → skill

| Pregunta del usuario | Skill principal | Complementarios |
|---|---|---|
| ¿Cuánto peso pongo hoy? | tabla del plan | `[[epley-formula]]`, `[[amrap-tree]]` |
| ¿Cómo cuento warm-up sets? | `[[warmup-calculator]]` | `[[lift-technique-reference]]` |
| ¿Cómo sé si es RPE 9? | `[[rpe-scale]]` | — |
| AMRAP fuera de target · ¿qué hago? | `[[amrap-tree]]` | `[[epley-formula]]` |
| ¿Cuánto volumen por grupo muscular? | `[[volume-landmarks-mev-mav-mrv]]` | `[[periodization-design]]` |
| Dormí mal · ¿hago la sesión? | `[[sleep-debt-protocol]]` | `[[daily-morning-check]]` |
| Llegué al gym sin ganas | `[[deload-by-session]]` | `[[pre-session-mental-prep]]`, `[[mental-game-plateau]]` |
| Rodilla molesta hoy | `[[plan-abc-knee]]` | `[[exercise-substitution-matrix]]` |
| Hombro/codo/lumbar molesta | `[[exercise-substitution-matrix]]` | `[[mobility-prehab-by-joint]]` |
| Equipo no disponible (rack, banco, máquina) | `[[exercise-substitution-matrix]]` | `[[vacation-bw-routine]]` |
| Vacaciones · ¿qué llevo? | `[[vacation-bw-routine]]` | `[[disruption-adaptation-framework]]` |
| Vuelvo de pausa · ¿cómo empiezo? | `[[recon-protocols]]` | `[[disruption-adaptation-framework]]` |
| ¿Cómo bracing pesado? | `[[bracing-valsalva]]` | `[[support-gear-protocol]]` |
| ¿Uso cinturón? ¿Muñequeras? ¿Mangas? | `[[support-gear-protocol]]` | `[[lift-technique-reference]]` |
| ¿Cómo me mido? Fotos? | `[[body-composition-tracking]]` | `[[telegram-tracking]]` |
| Empieza el deload · ¿qué hago? | `[[deload-week-design]]` | `[[periodization-design]]` |
| ¿Cómo es la semana pre-test? | `[[peak-week-tapering]]` | `[[test-day-protocol]]` |
| ¿Cómo es el día del test? | `[[test-day-protocol]]` | `[[peak-week-tapering]]` |
| Falla intento 1 del test | `[[test-day-protocol]]` §regla fallido | `[[mental-game-plateau]]` |
| Bench rinde más a ciertas horas | `[[longitudinal-analysis-dimensions]]` §4.7 | `[[coaching-principles]]` §4 |
| ¿Mi 1RM bench es 80 o 85? | `[[bench-dual-column]]` | `[[epley-formula]]` |
| Necesito plantilla Telegram | `[[telegram-template-library]]` | `[[telegram-tracking]]` |
| Ritual pre-sesión 5 min | `[[pre-session-mental-prep]]` | `[[mobility-prehab-by-joint]]` |
| Plateau · no avanzo · sem 8 | `[[mental-game-plateau]]` | `[[amrap-tree]]`, `[[deload-by-session]]` |
| ¿Cómo se hace este accesorio? | `[[accessory-technique-reference]]` | `[[lift-technique-reference]]` |
| Mobility pre-sesión | `[[mobility-prehab-by-joint]]` | `[[recovery-smr]]` |
| ¿Qué hacer tras este macro? | `[[multi-macro-roadmap]]` | `[[gym-plan-architect]]` |
| Cafeína · cuándo · cuánto | `[[nutrition-complete]]` | `[[test-day-protocol]]` (test) |
| Diseñar macro nuevo desde cero | (agent) `gym-plan-architect` | múltiples |
| Auditar plan existente | (agent) `plan-auditor` | `[[plan-audit-checklist]]` |
| Reajustar plan por vacaciones | (agent) `plan-reajuster` | `[[disruption-adaptation-framework]]` |
| Construir manual HTML | (agent) `manual-html-builder` | múltiples |
| Informe quirúrgico de bitácora | (agent) `surgical-report-builder` | `[[surgical-4-pass-methodology]]` |
| Coach en tiempo real | (agent) `coach-realtime` | múltiples |
| Auditar el propio HARNESS | `[[harness-self-audit]]` | — |

---

## Convenciones usadas

| Notación | Significado |
|---|---|
| `3+1*` | 3 sets fijos + 1 set AMRAP |
| `↻` | Superserie (15-20 s entre ejercicios) |
| `25 mc/lado` | 25 kg en cada mano (mancuernas) |
| `RECAL` | Recalibra 1RM con Epley |
| `≥ 9` | AMRAP target 9 reps o más |
| `RPE 8` | 2 reps en reserva (escala 1-10) |
| `DUP` | Daily Undulating Periodization |
| `MEV/MAV/MRV` | Volumen Mínimo Efectivo / Máximo Adaptativo / Máximo Recuperable |

---

## Cómo invocar

**Agents** (`HARNESS/agents/`): copia el archivo `.md` a `.claude/agents/` y se activan automáticamente cuando Claude detecta una tarea que matchea su descripción. O explícitamente: "usa el agente gym-plan-architect".

**Skills** (`HARNESS/skills/`): copia a `.claude/skills/<skill-name>/SKILL.md` y se invocan automáticamente cuando Claude detecta el contexto, o explícitamente: "aplica el skill epley-formula".

Alternativamente, puedes leer estos archivos como referencia documental sin invocación automática.

---

## Origen

Este harness se construyó a partir de la sesión de diseño del plan del perfil de referencia (18 may 2026 → 1 nov 2026 reajustado por vacaciones). Los archivos fuente están en `/mnt/d/GitHub/LOCAL/DIEGO/GYM/`:

- `plan_v4_diego_definitivo.html` (1315 líneas · plan original)
- `addendum_plan_v4_diego.html` (286 líneas · QA + glosario + 4 correcciones)
- `rutina_diego_campo.html` (794 líneas · primera versión manual de campo)
- `manual_operativo_diego_v5.html` (3796 líneas · manual completo fusionado)
- `rutina_diego_rapida.html` (932 líneas · quick reference mobile)
- `REAJUSTE_V5/manual_operativo_diego_v5_reajustado_vacaciones.html` (con vacaciones)
- `REAJUSTE_V5/rutina_diego_rapida_reajustado_vacaciones.html`
- `REAJUSTE_V5/plantillas_telegram.md` (1747 líneas · 32 plantillas vacaciones/RECON/test)
- `PROMPTS-UTILES/ANALISIS-QUIRURGICO.md` (metodología 4-pase + 25 dimensiones)
- `PROMPTS-UTILES/PLAN MANUAL ENTRENAMIENTO.md` (reglas de expansión manual · 5 tests calidad)

---

## Versión

- **v1** · 18 may 2026 · extracción inicial desde sesión completa de diseño del plan
- **v1.1** · 18 may 2026 · extracciones desde `PROMPTS-UTILES/`: agente `surgical-report-builder` + skills `surgical-4-pass-methodology`, `longitudinal-analysis-dimensions`, `manual-expansion-rules`
- **v1.2** · 18 may 2026 · 8 nuevos skills (telegram-template-library, coaching-principles, troubleshooting-catalog, editorial-writing-rules, surgical-report-structure, editorial-data-viz, pre-session-mental-prep, disruption-adaptation-framework)
- **v2.0** · 18 may 2026 · Plan 1 (5 fixes críticos + generalización del harness a cualquier humano) + Plan 2 (15 nuevos skills + 11 archivos editados). Estado: **8 agentes · 47 skills · ~12.000 líneas**.

  Nuevos skills v2.0:
  - **Meta**: harness-self-audit
  - **Fundamentos**: bracing-valsalva, warmup-calculator, daily-morning-check, accessory-technique-reference
  - **Periodización**: deload-week-design, peak-week-tapering, volume-landmarks-mev-mav-mrv, deload-by-session
  - **Adaptación**: exercise-substitution-matrix, support-gear-protocol, mobility-prehab-by-joint
  - **Tracking + meta**: body-composition-tracking, multi-macro-roadmap, mental-game-plateau
  - **Ampliación**: lift-technique-reference ahora incluye deadlift
