---
name: editorial-html-template
description: Invoke when building long-form editorial HTML training manuals (3000-5000 lines). Provides complete CSS template with typography (Fraunces/Newsreader/JetBrains Mono), color palette (paper/copper/moss/wine), components (day-card, technique block, lift-table, finding/callout, kpi-grid, telegram, cheat), and print stylesheet.
---

# Editorial HTML Template · estilo manual largo

## Fuentes (Google Fonts)

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT@9..144,300..900,0..100&family=Newsreader:ital,opsz,wght@0,6..72,200..800;1,6..72,200..800&family=JetBrains+Mono:wght@300;400;500;700&display=swap" rel="stylesheet">
```

- **Fraunces** (display) · variable opsz + SOFT · para h1, h2, h3 · italic emphasis
- **Newsreader** (body) · serif elegante · cuerpo de texto 17-18 px
- **JetBrains Mono** (data) · monospace · etiquetas, código, números

## Paleta de colores (CSS vars)

```css
:root {
  --ink: #1F1B16;          /* texto principal · titulares oscuros */
  --ink-soft: #3D362C;     /* texto secundario */
  --ink-mute: #6B6354;     /* texto menos prominente */
  --paper: #F5EFE3;        /* fondo cálido · crema */
  --paper-warm: #EFE5D2;   /* fondo de finding/callout */
  --paper-deep: #E6D9BE;   /* fondo más oscuro */
  --copper: #B4632F;       /* acentos cálidos · links · acentos copper */
  --copper-deep: #8E4A1F;  /* copper más oscuro */
  --ochre: #C49A3B;        /* deload · ochre cálido */
  --moss: #3F5A36;         /* positivo · verde oliva */
  --moss-soft: #6A8059;    /* moss más claro */
  --wine: #7A2E2B;         /* crítico · alertas */
  --wine-deep: #5C1F1D;    /* wine más oscuro · fondos oscuros */
  --rule: #C9BCA0;         /* bordes principales */
  --rule-soft: #D9CFB7;    /* bordes secundarios */
  --shadow: 0 1px 0 rgba(31,27,22,0.06), 0 8px 24px -16px rgba(31,27,22,0.18);
}
```

## CSS base completo

```css
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: 'Newsreader', Georgia, serif;
  font-size: 18px;
  line-height: 1.65;
  font-feature-settings: "kern", "liga", "onum";
  -webkit-font-smoothing: antialiased;
  background-image:
    radial-gradient(circle at 20% 10%, rgba(180,99,47,0.04) 0%, transparent 35%),
    radial-gradient(circle at 80% 70%, rgba(63,90,54,0.035) 0%, transparent 35%);
}
.grain {
  position: fixed; inset: 0; pointer-events: none; z-index: 100;
  opacity: 0.28; mix-blend-mode: multiply;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0.12 0 0 0 0 0.10 0 0 0 0 0.08 0 0 0 0.06 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
.wrap { max-width: 1180px; margin: 0 auto; padding: 0 48px; }
@media (max-width: 720px) { body { font-size: 16px; } .wrap { padding: 0 18px; } }
```

## Topnav sticky

```css
.topnav {
  position: sticky; top: 0; z-index: 50;
  background: rgba(245,239,227,0.94);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--rule);
}
.topnav-inner {
  max-width: 1180px; margin: 0 auto; padding: 12px 48px;
  display: flex; align-items: baseline; justify-content: space-between; gap: 18px;
}
.topnav .brand {
  font-family: 'Fraunces', serif; font-weight: 600; font-style: italic;
  font-size: 16px; letter-spacing: 0.01em;
}
.topnav nav {
  display: flex; gap: 9px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px; text-transform: uppercase; letter-spacing: 0.1em;
  flex-wrap: wrap; justify-content: flex-end;
}
.topnav nav a {
  color: var(--ink-mute); text-decoration: none;
  border-bottom: 1px solid transparent; padding-bottom: 3px;
  transition: all 0.2s;
}
.topnav nav a:hover { color: var(--copper); border-bottom-color: var(--copper); }
```

## Hero · portada

```css
.hero { padding: 70px 0 50px; }
.hero .kicker {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px; text-transform: uppercase; letter-spacing: 0.22em;
  color: var(--copper); margin-bottom: 22px;
  display: flex; align-items: center; gap: 14px; justify-content: center;
}
.hero h1 {
  font-family: 'Fraunces', serif; font-weight: 400;
  font-variation-settings: "opsz" 144, "SOFT" 30;
  font-size: clamp(40px, 6vw, 80px); line-height: 0.98; letter-spacing: -0.02em;
  margin: 0 0 24px; text-align: center;
}
.hero h1 em { font-style: italic; color: var(--copper); }
.hero .subtitle {
  text-align: center; max-width: 760px; margin: 0 auto;
  font-size: 21px; color: var(--ink-soft); line-height: 1.5; font-style: italic;
}
```

## PR card · cabecera mental oscura

```css
.pr-card {
  background: var(--ink); color: var(--paper);
  padding: 30px 36px; margin: 50px 0 30px;
}
.pr-card .head {
  font-family: 'JetBrains Mono', monospace; font-size: 10px;
  text-transform: uppercase; letter-spacing: 0.22em;
  color: var(--ochre); margin: 0 0 20px;
}
.pr-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }
.pr-item .lift {
  font-family: 'JetBrains Mono', monospace; font-size: 9px;
  text-transform: uppercase; letter-spacing: 0.18em;
  color: rgba(245,239,227,0.7); margin-bottom: 6px;
}
.pr-item .now {
  font-family: 'Fraunces', serif; font-size: 30px; font-weight: 400;
  color: var(--paper); line-height: 1;
}
.pr-item .target {
  font-family: 'Fraunces', serif; font-style: italic; font-size: 15px;
  color: var(--ochre); margin-top: 4px;
}
@media (max-width: 600px) { .pr-grid { grid-template-columns: repeat(2, 1fr); gap: 22px; } }
```

## Hardcoded strip (wine deep)

```css
.hardcoded {
  background: var(--wine-deep); color: var(--paper);
  padding: 16px 26px; margin: 0 0 30px;
  font-family: 'JetBrains Mono', monospace; font-size: 12px;
  text-transform: uppercase; letter-spacing: 0.12em;
  display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px;
}
.hardcoded strong { color: var(--ochre); }
```

## KPI grid

```css
.kpi-grid {
  margin-top: 50px; display: grid; grid-template-columns: repeat(6, 1fr);
  border-top: 1px solid var(--ink); border-bottom: 1px solid var(--ink);
}
.kpi-cell {
  padding: 22px 12px; text-align: center;
  border-right: 1px solid var(--rule);
}
.kpi-cell:last-child { border-right: none; }
.kpi-cell .num {
  font-family: 'Fraunces', serif; font-weight: 300;
  font-variation-settings: "opsz" 144;
  font-size: clamp(26px, 3.2vw, 40px); line-height: 1;
}
.kpi-cell .num .unit { font-size: 0.45em; color: var(--copper); font-style: italic; }
.kpi-cell .lbl {
  font-family: 'JetBrains Mono', monospace; font-size: 9px;
  text-transform: uppercase; letter-spacing: 0.15em;
  color: var(--ink-mute); margin-top: 10px;
}
.kpi-cell.good .num { color: var(--moss); }
.kpi-cell.crit .num { color: var(--wine); }
```

## Section heads

```css
section { padding: 80px 0 30px; scroll-margin-top: 100px; }
.section-head {
  display: grid; grid-template-columns: 110px 1fr; gap: 30px;
  align-items: baseline; margin-bottom: 36px;
  border-bottom: 1px solid var(--ink); padding-bottom: 18px;
}
.section-head .num {
  font-family: 'JetBrains Mono', monospace; font-size: 13px;
  letter-spacing: 0.18em; color: var(--copper); padding-top: 6px;
}
.section-head h2 {
  font-family: 'Fraunces', serif; font-weight: 400;
  font-variation-settings: "opsz" 144, "SOFT" 20;
  font-size: clamp(30px, 4vw, 48px); line-height: 1.02;
  letter-spacing: -0.015em; margin: 0;
}
.section-head h2 em { color: var(--copper); font-style: italic; }
```

## Finding / callout / delta

```css
.finding {
  background: var(--paper-warm); border-left: 3px solid var(--copper);
  padding: 22px 26px; margin: 28px 0;
}
.finding .tag {
  font-family: 'JetBrains Mono', monospace; font-size: 10px;
  text-transform: uppercase; letter-spacing: 0.18em;
  color: var(--copper); margin-bottom: 10px;
}
.finding.warn { border-left-color: var(--wine); background: rgba(122,46,43,0.06); }
.finding.warn .tag { color: var(--wine); }
.finding.good { border-left-color: var(--moss); background: rgba(63,90,54,0.06); }
.finding.good .tag { color: var(--moss); }
.finding.note { border-left-color: var(--ochre); background: rgba(196,154,59,0.07); }

.callout {
  margin: 40px 0; padding: 32px 40px;
  background: var(--ink); color: var(--paper); box-shadow: var(--shadow);
}
.callout.warn { background: var(--wine-deep); }
.callout.good { background: var(--moss); }
.callout .tag { color: var(--ochre); }
```

## Day-card

```css
.day-card {
  background: var(--paper); border: 1px solid var(--rule);
  margin: 30px 0; padding: 0;
}
.day-head {
  background: var(--ink); color: var(--paper); padding: 20px 28px;
  display: grid; grid-template-columns: auto 1fr auto; gap: 24px; align-items: baseline;
}
.day-head .day-no {
  font-family: 'JetBrains Mono', monospace; font-size: 11px;
  text-transform: uppercase; letter-spacing: 0.18em; color: var(--ochre);
}
.day-head .day-title {
  font-family: 'Fraunces', serif; font-size: 26px; font-weight: 500;
}
.day-head .day-title em { font-style: italic; color: var(--ochre); }
.day-body { padding: 26px 28px; }
.day-intent {
  font-style: italic; color: var(--ink-mute); margin-bottom: 22px;
  padding: 14px 18px; background: var(--paper-warm);
  border-left: 2px solid var(--copper); font-size: 15px;
}
```

## Exercise table

```css
table.ex-table {
  width: 100%; border-collapse: collapse;
  font-size: 14px; font-family: 'Newsreader', serif;
}
table.ex-table td {
  padding: 12px 8px; border-bottom: 1px solid var(--rule-soft);
  vertical-align: top;
}
table.ex-table td.code {
  font-family: 'JetBrains Mono', monospace; font-size: 11px;
  color: var(--copper); font-weight: 600; width: 32px;
  text-transform: uppercase; padding-top: 14px;
}
table.ex-table td.ex { font-weight: 500; }
table.ex-table td.ex .note {
  display: block; font-weight: 400;
  color: var(--ink-mute); font-size: 13px; font-style: italic;
  margin-top: 4px; line-height: 1.45;
}
table.ex-table td.cfg {
  font-family: 'JetBrains Mono', monospace; font-size: 12px;
  text-align: right; white-space: nowrap; color: var(--ink);
}
table.ex-table tr.warmup td { background: var(--paper-warm); }
table.ex-table tr.warmup td.code { color: var(--moss); }
table.ex-table tr.superset td { background: rgba(180,99,47,0.04); }
table.ex-table tr.superset td.code::after { content: " ↻"; color: var(--copper); }
```

## Technique block (bloque `<dl>`)

```css
.technique {
  margin: 28px 0; padding: 22px 26px;
  background: var(--paper-warm); border: 1px solid var(--rule);
}
.technique .ex-title {
  font-family: 'Fraunces', serif; font-weight: 600; font-size: 19px;
  color: var(--ink); margin: 0 0 4px;
}
.technique .ex-title em { font-style: italic; color: var(--copper); }
.technique .ex-role {
  font-family: 'JetBrains Mono', monospace; font-size: 10px;
  text-transform: uppercase; letter-spacing: 0.15em;
  color: var(--copper); margin-bottom: 14px;
}
.technique dt {
  font-family: 'JetBrains Mono', monospace; font-size: 10px;
  text-transform: uppercase; letter-spacing: 0.14em;
  color: var(--ink-mute); margin: 12px 0 4px;
}
.technique dd { margin: 0 0 6px; font-size: 15px; line-height: 1.55; }
```

## Lift table (semana a semana)

```css
table.weeks {
  width: 100%; border-collapse: collapse;
  font-size: 13px; font-family: 'Newsreader', serif;
}
table.weeks th {
  text-align: left; padding: 9px 10px;
  border-bottom: 2px solid var(--ink);
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px; text-transform: uppercase; letter-spacing: 0.13em;
  color: var(--ink); background: var(--paper);
}
table.weeks td {
  padding: 10px 10px; border-bottom: 1px solid var(--rule-soft);
}
table.weeks td.sem {
  font-family: 'JetBrains Mono', monospace; font-weight: 600;
  color: var(--copper); width: 40px;
}
table.weeks td.phase {
  font-family: 'JetBrains Mono', monospace; font-size: 10px;
  color: var(--ink-mute); width: 80px;
}
table.weeks td.rx {
  font-family: 'JetBrains Mono', monospace; font-size: 12px;
  color: var(--ink);
}
table.weeks td.amrap {
  font-family: 'JetBrains Mono', monospace; font-size: 11px;
  color: var(--moss); font-weight: 600; text-align: right;
}
table.weeks tr.deload td { background: rgba(196,154,59,0.08); color: var(--ink-mute); }
table.weeks tr.test td { background: rgba(63,90,54,0.1); }
table.weeks tr.recal td { border-bottom: 2px solid var(--copper); }
```

## Telegram box (oscura)

```css
.telegram {
  background: var(--ink); color: var(--paper);
  padding: 22px 28px; margin: 22px 0;
  font-family: 'JetBrains Mono', monospace; font-size: 13px; line-height: 1.7;
}
.telegram .tag {
  font-size: 10px; text-transform: uppercase; letter-spacing: 0.22em;
  color: var(--ochre); margin-bottom: 14px;
}
```

## Cheat sheet (oscura · grid 2 cols)

```css
.cheat {
  background: var(--ink); color: var(--paper);
  padding: 30px 36px; margin: 30px 0;
  border: 2px solid var(--ink);
}
.cheat h3 {
  font-family: 'Fraunces', serif; font-weight: 500;
  color: var(--ochre); font-size: 22px; margin: 0 0 6px;
}
.cheat-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 26px; }
.cheat-block h5 {
  font-family: 'JetBrains Mono', monospace; font-size: 10px;
  text-transform: uppercase; letter-spacing: 0.18em;
  color: var(--ochre); margin: 0 0 8px;
}
.cheat-block ul { list-style: none; padding: 0; margin: 0; }
.cheat-block li {
  font-size: 14px; line-height: 1.55;
  padding-left: 18px; position: relative; margin-bottom: 6px;
  color: rgba(245,239,227,0.9);
}
.cheat-block li::before { content: "·"; position: absolute; left: 0; color: var(--ochre); }
.cheat-block code {
  background: rgba(245,239,227,0.12); color: var(--ochre);
  padding: 1px 5px; font-family: 'JetBrains Mono', monospace; font-size: 0.85em;
}
@media (max-width: 720px) { .cheat-grid { grid-template-columns: 1fr; } }
```

## Print stylesheet

```css
@media print {
  .grain, .topnav { display: none; }
  body { background: white; font-size: 10pt; }
  .day-card, .callout, .finding, .delta, .technique, .telegram, .cheat {
    break-inside: avoid;
  }
  section { padding: 18pt 0; }
  .wrap { padding: 0 10mm; }
}
```

## Estructura HTML completa

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>...</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?..." rel="stylesheet">
  <style>/* ... CSS completo de arriba ... */</style>
</head>
<body>
  <div class="grain"></div>
  <header class="topnav">
    <div class="topnav-inner">
      <div class="brand">...</div>
      <nav>
        <a href="#portada">00</a>
        ...
      </nav>
    </div>
  </header>
  <div class="wrap">
    <section id="portada" class="hero">...</section>
    <section id="leer">...</section>
    ...
    <footer>
      <div class="colophon">...</div>
      <div class="signature">...</div>
    </footer>
  </div>
</body>
</html>
```

## Reglas no negociables del estilo

1. **Tipografía consistente** · solo Fraunces + Newsreader + JetBrains Mono
2. **Cero emojis** (excepto si el usuario lo pide explícito)
3. **Paleta cálida** · crema/cobre/musgo/vino/ocre (sin azul/púrpura/saturados)
4. **Mobile-first** · max-width 1180 px, breakpoint 720 px
5. **Print stylesheet incluido** para impresión limpia
6. **Topnav sticky** con navegación accesible siempre
7. **Sin animaciones excesivas** · transiciones 0.2 s en hover, nada más
