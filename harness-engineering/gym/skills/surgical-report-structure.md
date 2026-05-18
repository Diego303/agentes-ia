---
name: surgical-report-structure
description: Invoke when building the HTML structure of a surgical longitudinal report. Defines the obligatory 24+ sections (Hero, KPI grid, executive summary with 3 hard truths, method, current state, thematic sections per dimension, 15-20 numbered findings, time-bracketed recommendations, final callout, footer), the pre-delivery checklist, and editorial anti-patterns. 100% general.
---

# Surgical Report Structure · estructura obligatoria del entregable

## Propósito

Define la estructura HTML del informe quirúrgico longitudinal. Un único archivo HTML self-contained, ~80-150 KB, con ~20-25 secciones, ~25-30 figuras embebidas (.png en carpeta paralela), ~10-15 tablas, y ~15-20 cards de hallazgos.

Aplica este skill después de:
- `[[surgical-4-pass-methodology]]` (pases 1-3 completos)
- `[[longitudinal-analysis-dimensions]]` (dimensiones calculadas)

Combina con:
- `[[editorial-writing-rules]]` (cómo redactar dentro de cada sección)
- `[[editorial-data-viz]]` (cómo construir cada plot)
- `[[editorial-html-template]]` (CSS + tipografía + paleta)

## Estructura obligatoria

```
HERO
├── Kicker (pre-título con periodo cubierto)
├── Título grande serif italic display, palabra clave en color de acento
├── Subtítulo ~3 frases que enmarca el ámbito
├── Meta-info (sujeto · eventos · entidades · etc.)
└── KPI grid (6 indicadores: 3 críticos wine + 3 positivos moss)

§01 · Resumen ejecutivo
├── Lead en italic con borde lateral
├── Las 3 verdades duras (ver [[editorial-writing-rules]] regla 5)
├── Callout box destacada con el diagnóstico central
└── "Lo que SÍ va bien" (equilibrio emocional)

§02 · Método
├── Pipeline aplicado (qué pases · qué dimensiones)
└── Dimensiones nuevas respecto a versiones previas (si las hay)

§03 · Estado actual real (últimos 30 días)
├── Tabla inventario actual
└── Lectura inmediata del régimen

§04 a §22 · Secciones temáticas
└── Una por bloque de dimensiones del catálogo (ver [[longitudinal-analysis-dimensions]])

§23 · Lista de 15-20 hallazgos numerados
└── Cards con número, categoría, headline, justificación, acción

§24 · Recomendaciones diferenciales
├── Inmediato (próximas 2 sem)
├── Corto plazo (8 sem)
├── Mediano plazo (12-16 sem)
└── Hábitos transversales

Callout final
└── Veredicto cualitativo equilibrado

Footer
└── Colofón con metodología, contadores, fórmulas, paleta
```

## Detalle por sección

### Hero

- **Kicker** (línea pre-título): tipo `mono uppercase`, color `--copper`, ej: `informe quirúrgico v2 · jun 2023 → may 2026`
- **Título grande** serif italic display, `Fraunces opsz max`, una palabra clave coloreada en acento (e.g., `--copper` o `--wine`)
- **Subtítulo**: 3 frases en `Newsreader 18px`, color `--ink-mute`, que enmarca el ámbito del informe
- **Meta-info** (`mono 12px`): sujeto · número de eventos · número de entidades · periodo · número de tablas/figuras
- **KPI grid** (6 cards en grid 3×2):
  - 3 críticos: fondo `--paper-warm`, border-left `--wine`, número grande en `--wine`
  - 3 positivos: border-left `--moss`, número en `--moss`
  - **Los críticos deben ser cosas que el lector NO sabía o subestimaba** (no triviales)

### §01 Resumen ejecutivo

- **Lead en italic** con borde lateral copper, 1 párrafo de ~4-6 líneas
- **Tres verdades duras** (sección rotulada explícita):
  - Cada verdad como párrafo numerado
  - Cada una con número y fecha específica (regla 2 de `[[editorial-writing-rules]]`)
  - Cada una contradice/reformula impresión previa del sujeto
- **Callout box destacada** (fondo oscuro, ochre accent, padding 24px): el diagnóstico central en 2-3 frases
- **Lista "lo que SÍ va bien"** (3-5 puntos, fondo `--paper-warm`, sin números)

### §02 Método

- Pipeline aplicado: lista de los pases ejecutados
- Dimensiones nuevas vs informe previo (si lo hay)
- Limitaciones reconocidas (1 párrafo · no académico, operativo)

### §03 Estado actual real (últimos 30 días)

- Tabla inventario: entidad activa · última fecha · métrica actual · estado
- Lectura inmediata del régimen: 1-2 párrafos que sintetizan el snapshot

### §04 a §22 · Secciones temáticas

Una por bloque del catálogo de `[[longitudinal-analysis-dimensions]]`. Cada sección incluye:

- **Lead en italic** (1-2 líneas)
- **1-3 figuras** con figcaptions editoriales (no etiquetas · ver regla 5e de `[[editorial-writing-rules]]`)
- **1-2 tablas** con datos específicos
- **Una `.finding` box**: clases `note` (copper), `warn` (ochre), `good` (moss), o `crit` (wine)
- Si es crítica: una `.callout` con título grande

### §23 · Lista de 15-20 hallazgos numerados

Cada hallazgo es una card con:

```html
<article class="hallazgo crit">  <!-- o "atencion" / "positivo" -->
  <div class="hallazgo-tag">Hallazgo 01 · Cronobiología</div>
  <h3 class="hallazgo-title">Tu bench rinde 11 kg menos a las 18h que a las 21h</h3>
  <p>De las 124 sesiones de bench analizadas, las 58 ejecutadas
     entre 17h-19h promedian 72 kg en lift principal, frente a las
     43 entre 20h-22h que promedian 83 kg...</p>
  <p class="accion"><strong>Acción ·</strong> hardcodear lunes/viernes
     a 20-21h en el plan v5. No mover día para mover hora.</p>
</article>
```

- Tag superior (`Hallazgo NN · Categoría breve`) en `mono uppercase`
- Título tipo "headline" (1-2 líneas) en `Fraunces medium`
- 1-2 párrafos de justificación con números específicos
- Línea final `Acción · [verbo + objeto + parámetro]` (regla 4 de `[[editorial-writing-rules]]`)
- Border-left coloreado: `--wine` (crítico), `--ochre` (atención), `--moss` (positivo)

### §24 · Recomendaciones diferenciales

Organizadas por bloque temporal (cada bloque su propia sub-sección):

```
Inmediato (próximas 2 semanas)
├── 3-5 acciones ejecutables esta semana

Corto plazo (8 semanas / macro siguiente)
├── 3-5 acciones para el siguiente bloque

Mediano plazo (12-16 semanas / 2 macros)
├── 3-5 acciones estructurales

Hábitos transversales (todo el periodo)
├── 3-5 acciones no datables
```

Cada recomendación cumple las 3 preguntas: ¿qué hago? ¿cuándo? ¿durante cuánto?

### Callout final

Veredicto cualitativo equilibrado (regla 1 de `[[editorial-writing-rules]]`). NO es sermón, NO es palmadita.

Plantilla:

> "Esto es lo que tienes [resumen positivo en 1 frase].
> Esto es lo que está atascado o regresando [resumen crítico en 1 frase].
> Esto es lo que podrías tener si los próximos [N] meses los gestionas con los ajustes del informe [proyección honesta]."

### Footer

Colofón en `mono 11px`, color `--ink-mute`:
- Metodología (pases ejecutados, dimensiones cubiertas)
- Número de mensajes/eventos analizados
- Fórmulas usadas (Epley, ratio, etc.)
- Paleta editorial (los 9 colores)
- Fecha de generación y versión

## Checklist pre-entrega

Antes de declarar el informe terminado:

- [ ] He ejecutado los 4 pases de `[[surgical-4-pass-methodology]]`, incluido ≥1 ultrathink loop sin hallazgos nuevos significativos
- [ ] He vuelto al texto crudo del dataset (§4.20) e integrado ≥1 hallazgo solo visible ahí
- [ ] Tengo ≥3 hallazgos que contradicen impresiones superficiales o conclusiones previas
- [ ] Tengo ≥1 artefacto de medición detectado y explicado (cambio de unidad, variante, instrumento)
- [ ] Cada hallazgo numerado tiene número + fecha + acción específica
- [ ] Las recomendaciones son ejecutables esta semana sin más interpretación
- [ ] La narrativa principal del Pase 4 NO es la del Pase 1 (si lo es, no he profundizado)
- [ ] El informe tiene equilibrio (regla 1): hay crítica, hay reconocimiento, hay matiz
- [ ] Las cifras y fechas son verificables contra el dataset original
- [ ] El HTML compila sin errores, las imágenes referencian rutas existentes
- [ ] La estructura cumple las 24+ secciones (Hero + §01-§24 + Callout + Footer)
- [ ] KPI grid contiene 3 críticos no obvios + 3 positivos no triviales
- [ ] §23 contiene ≥15 hallazgos numerados con border-left coloreado
- [ ] §24 cubre los 4 bloques temporales

## Anti-patrones de estructura

- ❌ KPI grid con métricas globales medias (sin sorpresa)
- ❌ §01 Resumen ejecutivo basado en cifras all-time en lugar de ventanas recientes
- ❌ §23 con menos de 15 hallazgos (informe superficial)
- ❌ §24 sin separar bloques temporales (recomendaciones amontonadas)
- ❌ Una sección por cada métrica calculada (genera 50 secciones tediosas) · sintetizar por temática
- ❌ Mismo tono en todas las secciones (todo crítico o todo celebratorio)
- ❌ Hallazgos sin acción (entretenimiento)
- ❌ Callout final ausente o genérico
- ❌ Footer sin colofón metodológico (no se puede reproducir el informe)
- ❌ Plots con leyenda en otro idioma que el resto del informe

## Sinergia con otros skills

- `[[surgical-4-pass-methodology]]` · metodología que produce el contenido
- `[[longitudinal-analysis-dimensions]]` · catálogo que alimenta las §04-§22
- `[[editorial-writing-rules]]` · cómo redactar dentro de cada sección
- `[[editorial-data-viz]]` · cómo construir cada plot y figcaption
- `[[editorial-html-template]]` · CSS, paleta, tipografía (base técnica)

## Aplicación por agente

- `surgical-report-builder` · invoca obligatorio para construir el HTML final
- `plan-auditor` · NO aplica directamente (su entregable es lista, no informe). Sí aplica si producir audit como "informe HTML editorial"
- `manual-html-builder` · NO aplica (su estructura es distinta · son 17 secciones operativas, no 24 analíticas)
