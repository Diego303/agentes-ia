---
name: editorial-data-viz
description: Invoke when producing data visualizations for a surgical longitudinal report (matplotlib or equivalent). Defines the editorial plot style (paper background, copper/moss/wine palette, serif font, custom DPI) and a mapping of 14 plot types to longitudinal dimensions (heatmap calendar, timeline + moving avg, scatter w/ PR star, horizontal bars colored by state, etc.). 100% general.
---

# Editorial Data Viz · estilo + 14 tipos de plot para informes longitudinales

## Propósito

Las visualizaciones de un informe quirúrgico NO son decoración. Son **dispositivos retóricos**: cada plot debe contar una historia que el lector identifica en 5 segundos.

Este skill define:
1. El **estilo visual fijo** (paleta, fuente, DPI, ejes)
2. El **catálogo de 14 tipos de plot** mapeados a las dimensiones de `[[longitudinal-analysis-dimensions]]`

## Estilo visual fijo (matplotlib)

### Paleta editorial (NO NEGOCIABLE)

```python
PAPER       = "#F5EFE3"   # fondo principal
PAPER_WARM  = "#EFE5D2"   # fondo secundario (findings, hover)
INK         = "#1F1B16"   # texto principal, axis labels
INK_MUTE    = "#6B6354"   # texto secundario, axis ticks
COPPER      = "#B4632F"   # acento primario, datos generales
OCHRE       = "#C49A3B"   # atención, neutro
MOSS        = "#3F5A36"   # positivo, progresando
WINE        = "#7A2E2B"   # crítico, regresando
RULE        = "#C9BCA0"   # líneas separadoras, grid
```

### Configuración base matplotlib

```python
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams.update({
    "figure.facecolor": PAPER,
    "axes.facecolor": PAPER,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "axes.titlecolor": INK,
    "xtick.color": INK_MUTE,
    "ytick.color": INK_MUTE,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": RULE,
    "grid.linewidth": 0.5,
    "grid.alpha": 0.5,
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "axes.titleweight": "regular",
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "savefig.dpi": 140,
    "savefig.facecolor": PAPER,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.3,
})
```

### Reglas de tamaño por tipo

| Tipo de plot | Tamaño típico (in) | Razón |
|---|---|---|
| Timeline (volume/tonnage mensual) | 14 × 6 | aspect ratio narrativo |
| Barras horizontales (top N) | 13 × 8 | labels legibles |
| Heatmap calendario | 14 × 4 | una fila por mes |
| Heatmap matriz NxN | 12 × 10 | aspecto cuadrado |
| 4-panel grid (deep dive) | 14 × 10 | 2×2 con margen |
| Scatter + linea suavizada | 12 × 7 | espacio para anotar puntos |
| Barras agrupadas (proyecciones) | 13 × 6 | tres barras × N entidades |
| Stacked bars (push/pull) | 13 × 6 | signo arriba/abajo |
| Distribución por banda | 12 × 6 | bandas en x, % en y |
| Cronología timeline | 14 × 5 | barras horizontales largas |

## Catálogo de 14 tipos de plot por dimensión

### Plot 1 · Tonelaje/volumen mensual con media móvil

**Para**: §4.1 (métricas globales) o cualquier serie temporal aditiva.

**Estructura**:
- Barras mensuales en `COPPER` (alpha 0.7)
- Línea de media móvil 3M en `INK` (linewidth 1.5)
- Anotaciones verticales `WINE` para pausas >14 días
- Eje y con unidad (kg, €, hours, etc.)
- Eje x: meses con formato `mmm-aa`

### Plot 2 · Progresión por entidad (scatter + suavizado + estrella en PR)

**Para**: §4.2 (trayectoria por entidad).

**Estructura**:
- Scatter de cada evento (dot 4px, alpha 0.5, color por estado)
- Línea LOESS suave en `INK` linewidth 1.2
- Estrella `OCHRE` size 80 en el evento PR
- Título: nombre entidad + métrica inicial vs actual
- Subtitle: span en meses + pendiente

### Plot 3 · Heatmap calendario consistencia (7×53 por año)

**Para**: §4.6 (patrones temporales) · §4.12 (streaks).

**Estructura**:
- Grid 7 días × 53 semanas
- Color: `PAPER` (vacío) → `MOSS` saturado (alta densidad)
- Una sub-figura por año
- Etiquetas mes en eje superior, día semana en eje izquierdo
- Cero leyenda · colormap explícito en figcaption

### Plot 4 · Distribución por banda apilada anual

**Para**: §4.16 (distribución intensidad).

**Estructura**:
- Barras stacked por año
- Cada banda con color del catálogo (4-7 bandas máximo)
- % numérico (mono 10px) DENTRO de cada segmento si >5%
- Eje y: porcentaje 0-100%
- Eje x: años

### Plot 5 · Ritmo reciente 90d (barras horizontales coloreadas)

**Para**: §4.3 (CRÍTICO).

**Estructura**:
- Barras horizontales · entidades en y · pendiente en x
- Color por categoría:
  - `MOSS` para `progressing_fast`/`progressing`
  - `OCHRE` para `stalled`
  - `WINE` para `regressing`
  - `INK_MUTE` con alpha 0.3 para `no_data`
- Valor numérico a la derecha de cada barra
- Línea vertical `INK` en x=0

### Plot 6 · Paisaje de plateaus (barras horizontales por días sin PR)

**Para**: §4.4 (plateaus).

**Estructura**:
- Barras horizontales · entidades en y · días desde último max en x
- Color por umbral:
  - `MOSS` si <90 días
  - `COPPER` si 90-180
  - `OCHRE` si 180-365
  - `WINE` si >365
- Anotación de la fecha del PR a la derecha

### Plot 7 · Push/pull o ratio (stacked bars signed + línea de ratio)

**Para**: §4.13 (ratios estructurales).

**Estructura**:
- Push: barras positivas arriba en `COPPER`
- Pull: barras negativas (mismo valor abs) abajo en `MOSS`
- Línea de ratio push/pull en eje secundario (`INK`)
- Anotación zona "saludable" (0.9-1.1) en fondo `PAPER_WARM`

### Plot 8 · Frecuencia por categoría (líneas con marcadores + smoothing)

**Para**: §4.6, §4.10 (cambios de régimen).

**Estructura**:
- Una línea por categoría (4-7 max)
- Marcadores en cada punto
- Smoothing 3M para visual
- Leyenda fuera del plot (lateral derecha)
- Colores cíclicos: `COPPER` → `MOSS` → `OCHRE` → `WINE` → `INK`

### Plot 9 · Top entidades por volumen (barras horizontales coloreadas por estado)

**Para**: §4.1 + cross con §4.3.

**Estructura**:
- Top 15-20 entidades
- Barras horizontales · entidad en y · volumen en x
- Color cada barra por estado (ver Plot 5)
- Anotación con valor exacto a la derecha
- Eje y ordenado descendente

### Plot 10 · Deep dive por entidad (4-panel grid)

**Para**: §4.2 + análisis temático profundo.

**Estructura**: subplot 2×2:
- (0,0) Timeline cronológico (scatter + LOESS)
- (0,1) Distribución de pesos (histograma)
- (1,0) Tonelaje mensual (barras)
- (1,1) Distribución por reps/rango (pie o barras)
- Título global: nombre entidad

### Plot 11 · Day-of-week o hora-del-día (heatmap o barras)

**Para**: §4.6 (temporales) · §4.7 (cronobiología CRÍTICO).

**Estructura · barras**:
- Día semana o hora en x · número de eventos en y
- Color `COPPER` para volumen
- Segunda barra `MOSS` para performance media (eje y2)
- Anotar pico y valle

**Estructura · heatmap**:
- Hora × día semana
- Color por densidad o performance media
- Annotar el valor en cada celda

### Plot 12 · Cronología (timeline horizontal con barras de duración)

**Para**: §4.5 (abandonos) · §4.6 (pausas).

**Estructura**:
- Eje x: fecha
- Eje y: entidades (top 20)
- Barra horizontal por cada periodo activo de cada entidad
- Color: `MOSS` (activa actual) · `INK_MUTE` (abandonada)
- Anotaciones verticales `WINE` para pausas globales

### Plot 13 · Proyecciones a 6/12 meses (barras agrupadas)

**Para**: §4.14 (proyecciones).

**Estructura**:
- Por cada entidad: 3 barras agrupadas (actual, +6m, +12m)
- Color actual: `INK_MUTE` · proyección: gradiente `COPPER` → `MOSS` o `WINE` según signo
- Annotación con confianza (verosímil/improbable/artefacto)

### Plot 14 · Best session anatomy (scatter + bar + pie en grid)

**Para**: §4.15 (mejores eventos).

**Estructura**: subplot 2×2:
- (0,0) Scatter de la sesión (cada serie como punto · peso vs reps)
- (0,1) Barras de volumen por ejercicio de la sesión
- (1,0) Pie de distribución por grupo muscular
- (1,1) Tabla mini con métricas clave

## Reglas transversales

### Figcaptions editoriales (NO etiquetas)

- ❌ "Evolución del bench"
- ❌ "Volumen mensual 2023-2026"
- ✅ "Bench progresa lineal hasta jun 2024, plateau brusco coincidente con cambio de gym, recuperación parcial desde feb 2026"
- ✅ "Tonelaje mensual con dos pausas claras: jun 2024 (viaje 21d) y dic 2025 (lesión hombro), ambas con caída -40% del mes previo"

Ver regla 5e de `[[editorial-writing-rules]]`.

### Cero leyendas si el color es semántico

Si el lector puede inferir el color por contexto (verde=bien, rojo=mal), no hace falta leyenda. Si necesita una, está en el figcaption, no en una caja flotante encima del plot.

### Title vs subtitle

- Title: 1 línea descriptiva técnica
- Subtitle: 1 línea con la lectura editorial (ej: "lift más estancado: bench, 331 días sin PR")

### Anotación de eventos clave

Eventos vitales del sujeto (mudanza, lesión, nacimiento de hijo, cambio de trabajo) deben anotarse con línea vertical `WINE` punteada + texto rotado 90º.

## Anti-patrones de visualización

- ❌ Todos los plots del mismo color (paleta es funcional, no decorativa)
- ❌ Plots con leyenda en inglés cuando informe está en español
- ❌ Eje y empezando en valor arbitrario para exagerar tendencias
- ❌ Heatmaps con colormap inverso (rojo=alto cuando rojo=malo en el resto del informe)
- ❌ Pie charts con >5 categorías (ilegible)
- ❌ 3D plots (siempre · sin excepción)
- ❌ Spines superior y derecho visibles
- ❌ Grid con linewidth >0.5 (compite con datos)
- ❌ DPI <140 (pixelado al imprimir)
- ❌ Font sans en plots cuando informe es serif

## Sinergia con otros skills

- `[[longitudinal-analysis-dimensions]]` · catálogo de dimensiones que cada plot visualiza
- `[[surgical-report-structure]]` · cada §04-§22 contiene 1-3 plots
- `[[editorial-writing-rules]]` · regla 5e (figcaptions editoriales)
- `[[editorial-html-template]]` · paleta consistente entre HTML y plots

## Aplicación

`surgical-report-builder` invoca este skill obligatorio durante el Pase 2 (cuando produce los borradores de plots) y el Pase 4 (cuando los integra al HTML final).
