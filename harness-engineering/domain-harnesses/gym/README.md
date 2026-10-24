# HARNESS · Coach de fuerza/hipertrofia

Sistema general de agentes y skills para programación de entrenamiento (fuerza, hipertrofia, rendimiento general), auditoría de planes, reajustes por disrupciones (vacaciones/lesiones/eventos vitales), generación de manuales operativos editoriales HTML, coaching en tiempo real, y análisis longitudinal de bitácoras. Aplicable a cualquier humano con vida activa que busque mejora medible.

Para usar en futuros proyectos con cualquier perfil de usuario (hombre/mujer, principiante/intermedio/avanzado, lifter/runner/triatleta/persona activa). Solo necesitas adaptar los **valores numéricos** al perfil concreto — los **principios, fórmulas, protocolos y plantillas son invariantes**.

---

## Ejemplos numéricos

Los principios, fórmulas, protocolos y plantillas son generales. Cuando una skill necesita
un ejemplo con números, usa siempre el mismo **perfil ficticio**, para que los ejemplos
cuadren entre skills:

> - Persona intermedia · 75 kg · 175 cm · 32 años
> - 1RM: banca 100 kg · sentadilla 140 kg · peso muerto 180 kg · hip thrust 150×8 · prensa 240×8
> - Objetivos del macro: banca 105 · sentadilla 150 · hip thrust 160×8 · prensa 260×8
> - Macro de ejemplo: 17 semanas, 3 días/semana, deloads en las semanas 5 y 10, taper en la 15; empieza el lunes 12 ene 2026

Con otro perfil se recalculan las fórmulas (Epley, Mifflin, doble columna, cafeína mg/kg)
y se eligen los ejercicios principales; los principios (DUP, deload cada 4-5 semanas,
frecuencia 2× por grupo, autorregulación por RPE/AMRAP), los protocolos y la estructura de
las plantillas no cambian. **Adapta los valores a tu usuario real antes de aplicar.**

---

## Estructura

```
gym/
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
└── skills/                            ← una carpeta por skill con su SKILL.md
    │
    │ ─── PROGRAMACIÓN Y CÁLCULOS ───
    ├── epley-formula/                 Cálculo 1RM + ratio shortcut
    ├── rpe-scale/                     Escala RPE con señales físicas
    ├── amrap-tree/                    Árbol AMRAP de decisión
    ├── periodization-design/          DUP intra-semanal + bloques + deload + hitos
    ├── coaching-principles/           10 principios rectores de programación
    ├── volume-landmarks-mev-mav-mrv/     MEV/MAV/MRV operativos por grupo
    ├── plan-abc-knee/                 Plan A/B/C rodilla
    ├── exercise-substitution-matrix/    Matriz por articulación y equipo (generaliza A/B/C)
    ├── bench-dual-column/             Sistema doble columna 1RM bench
    ├── hip-thrust-reentry/            Re-entry HT tras pausa larga
    ├── calendar-arithmetic/           Aritmética calendario (fechas, sesiones, weeks)
    │
    │ ─── RECUPERACIÓN, NUTRICIÓN, EJECUCIÓN ───
    ├── sleep-debt-protocol/           Protocolo deuda sueño (1, 2-3, 4+ noches)
    ├── daily-morning-check/           Chequeo 60s al despertar (FC + sueño + sensación)
    ├── nutrition-complete/            Mifflin + macros + tomas + cafeína + recetas
    ├── recovery-smr/                  SMR/foam roll por día
    ├── mobility-prehab-by-joint/      Mobility activa pre-sesión (≠ SMR)
    ├── cardio-z2/                     Cardio Z2 protocolo + verificación
    ├── lift-technique-reference/      Técnica detallada de los compuestos (+ deadlift)
    ├── accessory-technique-reference/    Técnica de 12 ejercicios accesorios
    ├── bracing-valsalva/              Bracing 360° + Valsalva por intensidad
    ├── support-gear-protocol/         Cinturón, muñequeras, mangas, agarres
    ├── warmup-calculator/             Tabla warm-up por intensidad work-set
    ├── pre-session-mental-prep/       Ritual mental + activación 5 min pre-sesión
    │
    │ ─── DELOADS, EVENTOS Y DISRUPCIONES ───
    ├── deload-week-design/            Estructura de sem deload (sem 5, 10)
    ├── deload-by-session/             Deload de sesión única (entre normal y semana)
    ├── peak-week-tapering/            Taper neural sem 15 pre-test
    ├── test-day-protocol/             Pre-test, día, regla fallido (3 intentos universal)
    ├── vacation-bw-routine/           Rutina BW vacaciones
    ├── recon-protocols/               RECON-1 / RECON-2 + creatina re-saturación
    ├── disruption-adaptation-framework/    Meta-protocolo reajuste de macros
    ├── troubleshooting-catalog/       25+ escenarios comunes con acción
    │
    │ ─── TRACKING, ADHERENCIA Y META-PLANNING ───
    ├── telegram-tracking/             Cabecera + notación
    ├── telegram-template-library/     Biblioteca de 14 familias de plantillas
    ├── micro-celebraciones/           Sistema de micro-wins para adherencia
    ├── mental-game-plateau/           Gestión de pozos mentales mid-macro
    ├── body-composition-tracking/     Báscula + medidas + fotos + Mifflin recal
    ├── multi-macro-roadmap/           Planning 12-24m · rotación prioridades
    │
    │ ─── ANÁLISIS LONGITUDINAL Y AUDITORÍA ───
    ├── surgical-4-pass-methodology/   Metodología 4-pase con ultrathink loop
    ├── longitudinal-analysis-dimensions/    Catálogo 25 dimensiones
    ├── plan-audit-checklist/          Checklist exhaustivo de auditoría
    ├── harness-self-audit/            Meta-auditoría del propio harness (7 capas)
    │
    │ ─── PRODUCCIÓN EDITORIAL Y ENTREGABLES ───
    ├── manual-expansion-rules/        Filosofía "explicar vs diseñar" + 5 tests
    ├── editorial-html-template/       CSS + tipografía + paleta editorial
    ├── editorial-writing-rules/       5 reglas de escritura editorial
    ├── editorial-data-viz/            Estilo matplotlib + 14 tipos de plot
    ├── surgical-report-structure/     Estructura HTML del informe quirúrgico
    └── mobile-quick-template/         Template mobile-first compacto
```

---

## Filosofía base · qué asume este harness

El harness está calibrado para personas intermedias naturales con restricciones reales (no atletas de élite con 8 h de sueño y 5 días). Asume:

- **3-4 sesiones/semana** como máximo realista
- **Sueño limitado** (p. ej., 6-7 h consolidadas) como restricción frecuente
- **Posibles molestias articulares** (rodilla, hombro) que requieren contingencias
- **Adherencia psicológica** como factor crítico para macros largos (17+ semanas)
- **Honestidad en targets**: probabilidades 70-80% de éxito, no promesas de 100%

Si tu usuario es atleta de élite con todo bajo control, este harness puede subestimar lo que es posible. Si es principiante absoluto, puede sobrestimar la complejidad necesaria.

---

## Perfiles compatibles

| Perfil | Compatibilidad | Skills que requieren mayor adaptación |
|---|---|---|
| Intermedio natural (perfil base) | 100% | ninguno |
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
| ¿Mi 1RM de banca es 95 o 100? | `[[bench-dual-column]]` | `[[epley-formula]]` |
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

Desde la raíz del proyecto donde lo quieras usar:

```bash
mkdir -p .claude/agents .claude/skills
cp <ruta>/gym/agents/*.md .claude/agents/
cp -r <ruta>/gym/skills/* .claude/skills/
```

Los agentes se activan cuando la tarea encaja con su `description`, o explícitamente ("usa
el agente gym-plan-architect"). Las skills, igual, o con `/epley-formula`. También sirven
como referencia documental sin instalarlas.

`PROMPTS-UTILES/` contiene dos plantillas de prompt (informe quirúrgico de una bitácora y
manual operativo expandido) con huecos `<...>` para los datos de tu usuario.

---

## Origen

Se extrajo de un caso real de diseño, ejecución y reajuste de un macrociclo. En la v2.1 se
generalizó: no contiene datos de ninguna persona, los ejemplos usan el perfil ficticio de
arriba y los documentos originales no forman parte del repositorio.

---

## Versión

- **v1** · may 2026 · extracción inicial desde sesión completa de diseño del plan
- **v1.1** · may 2026 · extracciones desde `PROMPTS-UTILES/`: agente `surgical-report-builder` + skills `surgical-4-pass-methodology`, `longitudinal-analysis-dimensions`, `manual-expansion-rules`
- **v1.2** · may 2026 · 8 nuevos skills (telegram-template-library, coaching-principles, troubleshooting-catalog, editorial-writing-rules, surgical-report-structure, editorial-data-viz, pre-session-mental-prep, disruption-adaptation-framework)
- **v2.0** · may 2026 · Plan 1 (5 fixes críticos + generalización del harness a cualquier humano) + Plan 2 (15 nuevos skills + 11 archivos editados). Estado: **8 agentes · 47 skills · ~12.000 líneas**.

  Nuevos skills v2.0:
  - **Meta**: harness-self-audit
  - **Fundamentos**: bracing-valsalva, warmup-calculator, daily-morning-check, accessory-technique-reference
  - **Periodización**: deload-week-design, peak-week-tapering, volume-landmarks-mev-mav-mrv, deload-by-session
  - **Adaptación**: exercise-substitution-matrix, support-gear-protocol, mobility-prehab-by-joint
  - **Tracking + meta**: body-composition-tracking, multi-macro-roadmap, mental-game-plateau
  - **Ampliación**: lift-technique-reference ahora incluye deadlift
- **v2.1** · 24 oct 2026 · generalización: fuera los datos del caso real (ejemplos con un perfil ficticio común), skills en formato `skills/<nombre>/SKILL.md` para que Claude Code las descubra y `PROMPTS-UTILES/` convertidas en plantillas.
