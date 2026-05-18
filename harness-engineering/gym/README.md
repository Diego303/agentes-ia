# HARNESS · Coach de fuerza/hipertrofia

Sistema general de agentes y skills para programación de fuerza/hipertrofia, auditoría de planes, reajustes por disrupciones (vacaciones/lesiones), generación de manuales operativos editoriales HTML, y coaching en tiempo real.

Para usar en futuros proyectos con cualquier perfil de usuario · solo necesitas adaptar los valores numéricos al perfil concreto.

---

## Filosofía · general vs ejemplos del perfil de referencia

Este harness se construyó a partir de un caso real de uso (un atleta intermedio natural masculino con restricciones específicas). Los **principios, protocolos, formulas y templates son completamente generales**.

Los **ejemplos numéricos concretos** (cuando aparecen pesos como 85 kg, fechas como 19 oct 2026, etc.) son del **perfil de referencia** del caso de estudio:

> Intermedio natural masculino · ~80 kg corporal · 3 años entrenando ·
> PRs partida: bench 85 kg · sentadilla 110 kg · HT 120×8 · prensa 190×8 ·
> Targets macro: bench 92,5 / sentadilla 125 / HT 130×8 / prensa 220×8 ·
> Restricciones: 6 h sueño consolidadas · 3 días/sem · rodilla sensible · hora 20-21 h hardcoded ·
> Duración: 17 semanas + 1 deload post-test.

Cada skill que usa estos números lo declara explícitamente al inicio con una nota visible. **Adapta los valores a tu usuario real antes de aplicar**.

**Skills 100 % generales** (sin números específicos · directamente aplicables):
- coaching-principles, disruption-adaptation-framework, editorial-data-viz, editorial-html-template, editorial-writing-rules, lift-technique-reference, longitudinal-analysis-dimensions, manual-expansion-rules, mobile-quick-template, plan-abc-knee, pre-session-mental-prep, rpe-scale, sleep-debt-protocol, surgical-4-pass-methodology, surgical-report-structure, telegram-template-library, troubleshooting-catalog

**Skills con ejemplos del perfil de referencia** (etiquetados explícitamente · adaptables):
- amrap-tree, bench-dual-column, calendar-arithmetic, cardio-z2, epley-formula, hip-thrust-reentry, micro-celebraciones, nutrition-complete, periodization-design, plan-audit-checklist, recon-protocols, recovery-smr, telegram-tracking, test-day-protocol, vacation-bw-routine

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
    ├── plan-abc-knee.md               Plan A/B/C rodilla
    ├── bench-dual-column.md           Sistema doble columna 1RM bench
    ├── hip-thrust-reentry.md          Re-entry HT tras pausa larga
    ├── calendar-arithmetic.md         Aritmética calendario (fechas, sesiones, weeks)
    │
    │ ─── RECUPERACIÓN, NUTRICIÓN, EJECUCIÓN ───
    ├── sleep-debt-protocol.md         Protocolo deuda sueño (1, 2-3, 4+ noches)
    ├── nutrition-complete.md          Mifflin + macros + tomas + cafeína + recetas
    ├── recovery-smr.md                SMR/foam roll por día
    ├── cardio-z2.md                   Cardio Z2 protocolo + verificación
    ├── lift-technique-reference.md    Técnica detallada de los 4 lifts principales
    ├── pre-session-mental-prep.md     Ritual mental + activación 5 min pre-sesión
    │
    │ ─── EVENTOS ESPECIALES Y DISRUPCIONES ───
    ├── test-day-protocol.md           Pre-test, día, regla fallido
    ├── vacation-bw-routine.md         Rutina BW vacaciones
    ├── recon-protocols.md             RECON-1 / RECON-2 post-vacación
    ├── disruption-adaptation-framework.md  Meta-protocolo reajuste de macros
    ├── troubleshooting-catalog.md     25+ escenarios comunes con acción
    │
    │ ─── TRACKING Y BITÁCORA ───
    ├── telegram-tracking.md           Cabecera + notación
    ├── telegram-template-library.md   Biblioteca de 14 familias de plantillas
    ├── micro-celebraciones.md         Sistema de micro-wins para adherencia
    │
    │ ─── ANÁLISIS LONGITUDINAL Y AUDITORÍA ───
    ├── surgical-4-pass-methodology.md Metodología 4-pase con ultrathink loop
    ├── longitudinal-analysis-dimensions.md  Catálogo 25 dimensiones
    ├── plan-audit-checklist.md        Checklist exhaustivo de auditoría
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
- **v1.2** · 18 may 2026 · extracciones cruzadas (PROMPTS-UTILES + manual v5 + plantillas_telegram). 8 nuevos skills:
  - `telegram-template-library` (biblioteca de 14 familias de plantillas)
  - `coaching-principles` (10 principios rectores)
  - `troubleshooting-catalog` (25+ escenarios con acción)
  - `editorial-writing-rules` (5 reglas de escritura)
  - `surgical-report-structure` (estructura HTML del informe quirúrgico)
  - `editorial-data-viz` (estilo matplotlib + 14 plot types)
  - `pre-session-mental-prep` (ritual + activación 5 min)
  - `disruption-adaptation-framework` (meta-protocolo de reajuste)
