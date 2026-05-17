---
name: mobile-quick-template
description: Invoke when building a compact mobile-first quick-reference HTML (700-1000 lines). Same color palette and typography as editorial template but smaller font sizes, narrower max-width, horizontal scroll tables, compact day-cards, dense cheat grid. Optimized for "at a glance at 20:25 in the gym" use on phone screen.
---

# Mobile Quick Template · estilo rutina rápida

## Diferencias vs editorial-html-template

| Aspecto | Editorial (largo) | Mobile Quick |
|---|---|---|
| max-width | 1180 px | **760 px** |
| Font cuerpo | 18 px | **16 px** |
| Padding wrap | 0 48px | **0 18px** |
| Day-card height | Alta · técnica detallada | **Baja · notas mínimas** |
| Tablas pesos | full-width sin scroll | **min-width 580 px + overflow-x: auto** |
| Bloques técnica | `<dl>` completo por lift | **No incluidos** · notas en day-card |
| Cheat grid | 2 cols · líneas largas | **2 cols · líneas cortas (12 px)** |
| Topnav | Una línea siempre | **Stacked vertical en < 900px** |

## Estructura HTML mínima

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rutina rápida · ...</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT@9..144,300..900,0..100&family=Newsreader:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>/* CSS de abajo */</style>
</head>
<body>
  <header class="topnav">
    <div class="topnav-inner">
      <div class="brand">Rutina · qué hago hoy</div>
      <nav>
        <a href="#lun">LUN</a>
        <a href="#mie">MIÉ</a>
        <a href="#vie">VIE</a>
        <a href="#pesos">Pesos</a>
        <a href="#cheat">Cheat</a>
      </nav>
    </div>
  </header>
  <div class="wrap">
    <section class="hero">...</section>
    <section id="lun">...</section>
    <section id="mie">...</section>
    <section id="vie">...</section>
    <section id="pesos">...</section>
    <section id="cheat">...</section>
  </div>
  <footer>...</footer>
</body>
</html>
```

## CSS completo (mobile-first compacto)

```css
:root {
  /* Misma paleta que editorial · ver editorial-html-template */
  --ink: #1F1B16; --ink-soft: #3D362C; --ink-mute: #6B6354;
  --paper: #F5EFE3; --paper-warm: #EFE5D2;
  --copper: #B4632F; --copper-deep: #8E4A1F;
  --ochre: #C49A3B; --moss: #3F5A36;
  --wine: #7A2E2B; --wine-deep: #5C1F1D;
  --rule: #C9BCA0; --rule-soft: #D9CFB7;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0; background: var(--paper); color: var(--ink);
  font-family: 'Newsreader', Georgia, serif;
  font-size: 16px; line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}
.wrap { max-width: 760px; margin: 0 auto; padding: 0 18px; }

/* TOPNAV compacto */
.topnav {
  position: sticky; top: 0; z-index: 50;
  background: rgba(245,239,227,0.96); backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--rule); padding: 10px 18px;
}
.topnav-inner {
  max-width: 760px; margin: 0 auto;
  display: flex; align-items: center; justify-content: space-between;
  gap: 10px;
}
.topnav .brand {
  font-family: 'Fraunces', serif; font-style: italic; font-weight: 600;
  font-size: 14px;
}
.topnav nav {
  display: flex; gap: 10px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px; text-transform: uppercase; letter-spacing: 0.12em;
  flex-wrap: wrap;
}
.topnav nav a {
  color: var(--ink-mute); text-decoration: none;
  border-bottom: 1px solid transparent; padding-bottom: 2px;
}

/* HERO compacto */
.hero { padding: 28px 0 18px; text-align: center; }
.hero h1 {
  font-family: 'Fraunces', serif; font-weight: 400;
  font-size: clamp(28px, 6vw, 40px); margin: 0 0 6px; line-height: 1;
}
.hero h1 em { font-style: italic; color: var(--copper); }
.hero .sub {
  font-family: 'JetBrains Mono', monospace; font-size: 10px;
  text-transform: uppercase; letter-spacing: 0.18em;
  color: var(--copper); margin-bottom: 18px;
}

/* PR card oscura compacta */
.pr-card {
  background: var(--ink); color: var(--paper);
  padding: 18px 20px; margin: 18px 0;
}
.pr-card .head {
  font-family: 'JetBrains Mono', monospace; font-size: 9px;
  text-transform: uppercase; letter-spacing: 0.18em;
  color: var(--ochre); margin-bottom: 12px;
}
.pr-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.pr-item .lift {
  font-family: 'JetBrains Mono', monospace; font-size: 8px;
  text-transform: uppercase; letter-spacing: 0.14em;
  color: rgba(245,239,227,0.65); margin-bottom: 2px;
}
.pr-item .now { font-family: 'Fraunces', serif; font-size: 18px; color: var(--paper); }
.pr-item .target {
  font-family: 'Fraunces', serif; font-style: italic; font-size: 11px;
  color: var(--ochre); margin-top: 2px;
}
@media (max-width: 480px) { .pr-grid { grid-template-columns: repeat(2, 1fr); gap: 14px; } }

/* Hardcoded compacto (wine) */
.hardcoded {
  background: var(--wine-deep); color: var(--paper);
  padding: 10px 16px; margin: 0 0 20px;
  font-family: 'JetBrains Mono', monospace; font-size: 10px;
  text-transform: uppercase; letter-spacing: 0.1em;
  display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px;
}
.hardcoded strong { color: var(--ochre); }

/* Section heads compactos */
.sec-head {
  margin: 32px 0 10px; padding-bottom: 8px;
  border-bottom: 1px solid var(--ink);
  display: flex; align-items: baseline; justify-content: space-between;
  gap: 12px;
}
.sec-head h2 {
  font-family: 'Fraunces', serif; font-weight: 500;
  font-size: 22px; margin: 0;
}
.sec-head h2 em { font-style: italic; color: var(--copper); }
.sec-head .meta {
  font-family: 'JetBrains Mono', monospace; font-size: 10px;
  text-transform: uppercase; letter-spacing: 0.12em; color: var(--ink-mute);
}

/* DAY CARD compacto */
.day {
  background: var(--paper); border: 1px solid var(--rule);
  margin: 14px 0 26px;
}
.day-head {
  background: var(--ink); color: var(--paper); padding: 12px 16px;
  display: flex; justify-content: space-between; align-items: baseline;
  gap: 10px; flex-wrap: wrap;
}
.day-head .title {
  font-family: 'Fraunces', serif; font-size: 18px;
}
.day-head .title em { font-style: italic; color: var(--ochre); }
.day-head .when {
  font-family: 'JetBrains Mono', monospace; font-size: 10px;
  text-transform: uppercase; letter-spacing: 0.12em; color: var(--ochre);
}

table.ex {
  width: 100%; border-collapse: collapse;
  font-size: 13px; font-family: 'Newsreader', serif;
}
table.ex td {
  padding: 9px 6px; border-bottom: 1px solid var(--rule-soft);
  vertical-align: top;
}
table.ex td.code {
  font-family: 'JetBrains Mono', monospace; font-size: 10px;
  color: var(--copper); font-weight: 700; width: 32px;
  text-transform: uppercase; padding-left: 14px;
}
table.ex td.ex { font-weight: 500; }
table.ex td.ex .note {
  display: block; font-weight: 400; color: var(--ink-mute);
  font-size: 11px; font-style: italic; margin-top: 2px; line-height: 1.35;
}
table.ex td.cfg {
  font-family: 'JetBrains Mono', monospace; font-size: 11px;
  text-align: right; white-space: nowrap; color: var(--ink);
  padding-right: 14px; min-width: 95px;
}
table.ex td.cfg .rpe {
  display: block; color: var(--copper-deep); font-size: 10px; margin-top: 2px;
}
table.ex td.cfg .rest {
  display: block; color: var(--ink-mute); font-size: 10px; margin-top: 1px;
}
table.ex tr.warm td { background: var(--paper-warm); }
table.ex tr.warm td.code { color: var(--moss); }
table.ex tr.ss td { background: rgba(180,99,47,0.05); }
table.ex tr.ss td.code::after { content: " ↻"; color: var(--copper); }

/* Tree A/B/C compacto */
.tree {
  background: var(--paper-warm); border-left: 3px solid var(--wine);
  padding: 10px 14px; margin: 12px 14px; font-size: 12px; line-height: 1.45;
}
.tree .tag {
  font-family: 'JetBrains Mono', monospace; font-size: 9px;
  text-transform: uppercase; letter-spacing: 0.14em;
  color: var(--wine); margin-bottom: 6px;
}
.tree strong { color: var(--wine-deep); }

/* PESOS tables compactas con scroll horizontal */
.lift-block { margin: 18px 0 26px; }
.lift-block h3 {
  font-family: 'Fraunces', serif; font-weight: 500; font-size: 18px;
  margin: 0 0 4px;
}
.lift-block h3 em { font-style: italic; color: var(--copper); }
.lift-block .base {
  font-family: 'JetBrains Mono', monospace; font-size: 10px;
  text-transform: uppercase; letter-spacing: 0.1em;
  color: var(--ink-mute); margin-bottom: 10px;
}
.table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
table.weeks {
  width: 100%; border-collapse: collapse;
  font-size: 11px; font-family: 'Newsreader', serif;
  min-width: 580px;  /* ← clave para scroll horizontal */
}
table.weeks th {
  text-align: left; padding: 7px 8px;
  border-bottom: 2px solid var(--ink);
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px; text-transform: uppercase; letter-spacing: 0.1em;
  white-space: nowrap;
}
table.weeks td {
  padding: 7px 8px; border-bottom: 1px solid var(--rule-soft);
}
table.weeks td.sem {
  font-family: 'JetBrains Mono', monospace; font-weight: 600;
  color: var(--copper); width: 28px;
}
table.weeks td.fase {
  font-family: 'JetBrains Mono', monospace; font-size: 9px;
  color: var(--ink-mute); width: 60px;
}
table.weeks td.rx {
  font-family: 'JetBrains Mono', monospace; font-size: 11px;
  color: var(--ink); white-space: nowrap;
}
table.weeks td.amr {
  font-family: 'JetBrains Mono', monospace; font-size: 10px;
  color: var(--moss); font-weight: 600; text-align: right;
}
table.weeks tr.dload td { background: rgba(196,154,59,0.10); color: var(--ink-mute); }
table.weeks tr.test td { background: rgba(63,90,54,0.12); font-weight: 600; }
table.weeks tr.recal td { border-bottom: 2px solid var(--copper); }

/* Cheat box (oscura · grid 2 cols compacto) */
.cheat {
  background: var(--ink); color: var(--paper);
  padding: 18px 20px; margin: 18px 0;
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 18px;
}
.cheat h4 {
  font-family: 'JetBrains Mono', monospace; font-size: 9px;
  text-transform: uppercase; letter-spacing: 0.16em;
  color: var(--ochre); margin: 0 0 6px;
}
.cheat ul { list-style: none; padding: 0; margin: 0; font-size: 12px; line-height: 1.55; }
.cheat li {
  padding-left: 12px; position: relative; margin-bottom: 3px;
  color: rgba(245,239,227,0.92);
}
.cheat li::before { content: "·"; position: absolute; left: 0; color: var(--ochre); }
.cheat code {
  font-family: 'JetBrains Mono', monospace; background: rgba(245,239,227,0.1);
  color: var(--ochre); padding: 1px 4px; border-radius: 2px; font-size: 0.92em;
}
@media (max-width: 600px) { .cheat { grid-template-columns: 1fr; gap: 14px; } }

/* Notas/avisos compactas */
.note {
  background: var(--paper-warm); border-left: 3px solid var(--copper);
  padding: 10px 14px; margin: 14px 0;
  font-size: 12px; line-height: 1.5;
}
.note.warn { border-left-color: var(--wine); background: rgba(122,46,43,0.06); }
.note .lbl {
  font-family: 'JetBrains Mono', monospace; font-size: 9px;
  text-transform: uppercase; letter-spacing: 0.14em;
  color: var(--copper); margin-bottom: 4px;
}
.note.warn .lbl { color: var(--wine); }

/* Telegram box compacta */
.telegram {
  background: var(--ink); color: var(--paper);
  padding: 14px 18px; margin: 14px 0;
  font-family: 'JetBrains Mono', monospace; font-size: 11px; line-height: 1.7;
}
.telegram .lbl {
  font-size: 9px; text-transform: uppercase; letter-spacing: 0.18em;
  color: var(--ochre); margin-bottom: 8px;
}

/* Footer */
footer {
  margin-top: 40px; padding: 20px 0 30px; text-align: center;
  border-top: 1px solid var(--rule);
}
footer p {
  font-family: 'JetBrains Mono', monospace; font-size: 9px;
  text-transform: uppercase; letter-spacing: 0.16em;
  color: var(--copper); margin: 0;
}

/* Print stylesheet */
@media print {
  .topnav { display: none; }
  body { background: white; font-size: 11pt; }
  .day, .lift-block, .cheat, .telegram, .note { break-inside: avoid; }
}
```

## Day-card minimal ejemplo

```html
<div class="day">
  <div class="day-head">
    <div class="title">Upper A — <em>Heavy + leg sprinkle</em></div>
    <div class="when">9 ejercicios · 22 series</div>
  </div>
  <div class="day-body">
    <table class="ex">
      <tbody>
        <tr class="warm"><td class="code">W</td>
          <td class="ex">Calentamiento progresivo
            <span class="note">3 min bici · band pull-aparts 2×15 · scapular push-ups 1×10 · barra 20×10 → 40×5 → 60×3 → 80% × 1-2</span>
          </td>
          <td class="cfg">8 min</td>
        </tr>
        <tr><td class="code">A1</td>
          <td class="ex">Press banca plano <strong>· primario</strong>
            <span class="note">3 sets fijos + 1 AMRAP final. Peso según §Pesos.</span>
          </td>
          <td class="cfg">3+1*<span class="rpe">RPE 7-9</span><span class="rest">3 min</span></td>
        </tr>
        <tr class="ss"><td class="code">C1</td>
          <td class="ex">Dominada lastrada/asistida
            <span class="note">&lt;5 PC = banda · ≥10 PC = lastrar</span>
          </td>
          <td class="cfg">3 × 5-8<span class="rpe">RPE 8</span><span class="rest">90 s</span></td>
        </tr>
        ...
      </tbody>
    </table>
  </div>
</div>
```

## Tabla pesos compacta ejemplo

```html
<div class="table-wrap">
  <table class="weeks">
    <thead>
      <tr><th>Sem</th><th>Fase</th><th>Lun · 1RM 80</th><th>Lun · 1RM 85</th><th>Vie · 1RM 80</th><th>Vie · 1RM 85</th><th>AMR</th></tr>
    </thead>
    <tbody>
      <tr><td class="sem">1</td><td class="fase">Acum</td><td class="rx">3×5 @ 60 + AMRAP</td><td class="rx">3×5 @ 65 + AMRAP</td><td class="rx">4×8 @ 55</td><td class="rx">4×8 @ 57,5</td><td class="amr">≥ 9</td></tr>
      ...
    </tbody>
  </table>
</div>
```

## Cheat sheet ejemplo (8 cajas grid)

```html
<div class="cheat">
  <div>
    <h4>Notación</h4>
    <ul>
      <li><code>3+1*</code> = 3 fijos + 1 AMRAP</li>
      <li><code>↻</code> = superserie</li>
      <li><code>25 mc/lado</code> = 25 kg cada mano</li>
      <li><code>RECAL</code> = aplica Epley</li>
    </ul>
  </div>
  <div>
    <h4>Escala RPE</h4>
    <ul>
      <li>RPE 7 · 3 reps reserva</li>
      <li>RPE 8 · 2 reps reserva · <strong>trabajo</strong></li>
      <li>RPE 9 · 1 rep reserva</li>
      <li>RPE 10 · imposible · SOLO test</li>
    </ul>
  </div>
  ...
</div>
```

## Reglas no negociables

1. **max-width 760 px** (NO 1180 px como editorial)
2. **Tipografía 13-16 px** (legible sin zoom en móvil)
3. **Tablas con `min-width 580 px` + wrapper `overflow-x: auto`** para scroll horizontal en pantalla estrecha
4. **Day-card notas mínimas** · 1-2 frases por ejercicio max
5. **Cheat grid 2 cols** que colapsa a 1 col en < 600 px
6. **Topnav sticky** siempre visible
7. **Print stylesheet** incluido para imprimir/plastificar
8. **Cero técnica detallada** (eso va al manual largo · esto es referencia)
