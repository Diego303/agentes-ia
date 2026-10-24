---
name: harness-self-audit
description: Invoke after creating or modifying any skill/agent in this HARNESS to verify consistency (nota "ejemplos ilustrativos" present where needed, no personal data, fictional example profile consistent, cross-references [[name]] valid, list of invoked skills up-to-date in each agent, no content duplication across skills, frontmatter complete, math formulas consistent across files). The plan-auditor audits external plans; this skill audits the HARNESS itself.
---

# Harness Self-Audit · meta-auditoría del propio harness

> **Nota · skill 100% general · meta-tooling del harness, no del entrenamiento.**

## Propósito

El plan-auditor audita planes externos. El surgical-report-builder analiza datos longitudinales. **Pero el harness mismo crece sin meta-checklist** · cada extracción nueva puede introducir gaps: skills sin nota de ejemplos ilustrativos, datos personales filtrados en ejemplos, cross-references rotos, listas de skills invocados desactualizadas en agentes, contenido duplicado entre skills.

Este skill define **7 capas de meta-auditoría**. Ejecutarlo tras cada modificación importante previene los patrones de error documentados en auditorías previas del harness.

## Cuándo invocar

- **Inmediatamente** tras crear un nuevo skill/agente
- **Tras editar** un skill que afecta múltiples agentes
- **Mensualmente** como review preventiva
- **Antes de declarar** el harness "production-ready" para un nuevo perfil de usuario

## Las 7 capas de meta-auditoría

### Capa 1 · estructura de archivos

- Cada skill en `skills/<name>/SKILL.md` (una carpeta por skill · 47 en esta versión), cada agente en `agents/<name>.md` (8 en esta versión)
- Ningún skill suelto con el layout antiguo `skills/*.md`
- Naming kebab-case sin espacios ni acentos
- Frontmatter con `name:` (matches nombre de carpeta en skills, filename en agentes) y `description:` (presente, ≥80 chars)
- Frontmatter opcional para agentes: `tools:`, `model:`
- Skills: carpeta = `name` del frontmatter · archivo siempre `SKILL.md`. Agentes: filename = `name` + `.md`

#### Script de validación

```bash
# Layout: conteos y skills sueltos del layout antiguo
echo "skills: $(ls -d skills/*/ | wc -l) · agentes: $(ls agents/*.md | wc -l)"
ls skills/*.md 2>/dev/null && echo "LAYOUT ANTIGUO: mover a skills/<name>/SKILL.md"
for d in skills/*/; do
    [ -f "${d}SKILL.md" ] || echo "FALTA SKILL.md: $d"
done

# Validar nombres
for f in skills/*/SKILL.md agents/*.md; do
    name_yaml=$(grep -m1 "^name:" "$f" | sed 's/name: //')
    case "$f" in
        skills/*) name_file=$(basename "$(dirname "$f")") ;;
        *)        name_file=$(basename "$f" .md) ;;
    esac
    if [ "$name_yaml" != "$name_file" ]; then
        echo "MISMATCH: $f · YAML name='$name_yaml' vs nombre='$name_file'"
    fi
done

# Validar description ≥80 chars
for f in skills/*/SKILL.md agents/*.md; do
    desc=$(grep -m1 "^description:" "$f" | sed 's/description: //')
    if [ ${#desc} -lt 80 ]; then
        echo "SHORT DESC ($((${#desc})) chars): $f"
    fi
done
```

### Capa 2 · nota de ejemplos ilustrativos y datos personales

**Regla**: cada skill que mencione cifras específicas (kg, mg, fechas, %) DEBE tener una nota de generalidad en las primeras 10 líneas tras el frontmatter, del tipo:

> Los números de los ejemplos son ilustrativos: recalcula con los datos de tu usuario.

Skills 100% generales (sin cifras concretas) NO la necesitan.

**Regla complementaria**: el harness no contiene datos personales de ninguna persona real (nombre, medidas, PRs, fechas de su calendario, salud, estadísticas de su bitácora). Cuando un ejemplo trabajado ayuda, se usa SIEMPRE el mismo perfil ficticio para que todos los skills sean coherentes entre sí:

| Valor canónico del perfil ficticio | Valor |
|---|---|
| Persona | intermedia · 75 kg · 175 cm · 32 años |
| 1RM actuales | banca 100 kg · sentadilla 140 kg · peso muerto 180 kg · hip thrust 150×8 · prensa 240×8 |
| Targets del macro | banca 105 kg · sentadilla 150 kg · hip thrust 160×8 · prensa 260×8 |
| Bench dual columna | "1RM 95" vs "1RM 100" (ratio 0,95) |
| Calendario de ejemplo | macro de 17 semanas que empieza el lunes 12 ene 2026 · deloads sem 5 y 10 · taper sem 15 · 3 sesiones/sem |

Si un skill usa otro 1RM, otro target u otra fecha de inicio en un ejemplo, es drift: alinéalo con esta tabla o sustitúyelo por una fórmula.

#### Detección

```bash
for f in skills/*/SKILL.md; do
    # ¿tiene cifras específicas en kg/mg/fechas?
    has_numbers=$(grep -cE "[0-9]+ ?(kg|mg|sem|días|h|min|reps|%|cal|g/kg)" "$f")
    has_header=$(grep -c "ejemplos son ilustrativos\|perfil ficticio\|skill general aplicable\|skill 100% general" "$f")
    if [ "$has_numbers" -gt 10 ] && [ "$has_header" -eq 0 ]; then
        echo "FALTA nota de ejemplos: $f ($has_numbers cifras detectadas)"
    fi
done
```

### Capa 3 · cross-references `[[name]]` válidos

Toda referencia `[[skill-name]]` debe apuntar a un skill real (`skills/<skill-name>/SKILL.md`).

#### Script

```python
import re, os

ROOT = "skills"
skills_existentes = set(d for d in os.listdir(ROOT) if os.path.isfile(f"{ROOT}/{d}/SKILL.md"))
refs = set()
for d in skills_existentes:
    content = open(f"{ROOT}/{d}/SKILL.md").read()
    refs |= set(re.findall(r'\[\[([a-z-0-9]+)\]\]', content))

rotos = refs - skills_existentes
if rotos:
    print(f"REFS ROTOS: {sorted(rotos)}")
else:
    print(f"✓ {len(refs)} refs válidos · 0 rotos")
```

### Capa 4 · listas "Skills que invoca" en cada agente

Para cada agente:
1. Listar skills mencionados en la sección "Skills que invoca"
2. Verificar que cada skill referenciado existe
3. Verificar que el agente no usa skills "huérfanos" (mencionados en código pero no en la lista)
4. Heurística: si un skill se menciona ≥3 veces en un agente, debería estar en su lista

#### Script

```python
import re, os

for agente in os.listdir("agents"):
    if not agente.endswith(".md"): continue
    content = open(f"agents/{agente}").read()

    # Skills declarados en sección "Skills que invoca"
    lista_seccion = re.search(r"## Skills que invoca.*?(?=##|\Z)", content, re.DOTALL)
    declarados = set(re.findall(r"`?\[?\[?([a-z][a-z-]+)\]?\]?`?", lista_seccion.group(0))) if lista_seccion else set()

    # Skills mencionados en el cuerpo
    mencionados = re.findall(r"\[\[([a-z-]+)\]\]|`([a-z-]+)`", content)
    counts = {}
    for m in mencionados:
        nombre = m[0] or m[1]
        counts[nombre] = counts.get(nombre, 0) + 1

    # Huérfanos (mencionados ≥3 veces pero no en lista)
    huerfanos = [n for n, c in counts.items() if c >= 3 and n not in declarados and os.path.exists(f"skills/{n}/SKILL.md")]
    if huerfanos:
        print(f"{agente}: huérfanos {huerfanos}")
```

### Capa 5 · solapamiento de contenido

Detectar párrafos copiados textualmente entre 2+ skills.

**Regla**: si dos skills explican el mismo protocolo, uno debe ser **canónico** y el otro debe **delegar** con `[[link]]`.

#### Detección heurística

```bash
# Buscar frases idénticas de ≥80 caracteres en 2+ archivos
for skill in skills/*/SKILL.md; do
    grep -oE ".{80,}" "$skill" | sort -u > /tmp/frases_$(basename "$(dirname "$skill")").txt
done

cat /tmp/frases_*.txt | sort | uniq -d | head -20
# Frases duplicadas detectadas → candidatas a refactor con [[link]]
```

### Capa 6 · coherencia matemática transversal

Fórmulas que aparecen en múltiples skills deben aparecer **idénticas**.

#### Lista de fórmulas globales del harness

| Nombre | Fórmula | Skills donde aparece |
|---|---|---|
| Epley | `1RM = peso × (1 + reps/30)` | epley-formula, amrap-tree, telegram-template-library |
| Mifflin hombre | `TMB = 10·peso + 6,25·altura − 5·edad + 5` | nutrition-complete |
| Mifflin mujer | `TMB = 10·peso + 6,25·altura − 5·edad − 161` | nutrition-complete |
| Cafeína estándar | `mg = peso_corporal × 3` | nutrition-complete, test-day-protocol |
| Cafeína test | `mg = peso_corporal × 6` | test-day-protocol |
| Ratio dual columna | `peso_col_baja = peso_col_alta × (1RM_baja / 1RM_alta)` | bench-dual-column, epley-formula |
| Apertura test (regla universal) | `max(PR_previo, 0.95 × target)` | test-day-protocol, plan-audit-checklist |
| Intermedio test | `(apertura + target) / 2` | test-day-protocol |
| Warm-up sets | depende intensidad work-set | warmup-calculator |

#### Verificación

```bash
# Epley aparece igual en todos
grep -h "1 + reps/30\|1 + reps / 30" skills/*/SKILL.md
# Todas las apariciones deben tener formato idéntico
```

### Capa 7 · coherencia de scope (cada skill cumple su YAML description)

Leer la `description:` YAML de cada skill y verificar que el contenido del cuerpo:
1. **Cumple** lo que promete el description (no under-deliver)
2. **NO excede** lo que promete (no scope creep)

#### Heurística

```bash
for f in skills/*/SKILL.md; do
    desc=$(grep -m1 "^description:" "$f" | sed 's/description: //')
    body_words=$(wc -w < "$f")
    desc_words=$(echo "$desc" | wc -w)

    # skill con description densa (≥30 palabras) debería tener ≥150 palabras de cuerpo
    if [ "$desc_words" -ge 30 ] && [ "$body_words" -lt 500 ]; then
        echo "UNDER-DELIVER: $f · desc=$desc_words words, body=$body_words"
    fi
done
```

## Output del audit

```
HARNESS SELF-AUDIT · YYYY-MM-DD

═══════════════════════════════════════════════════
HALLAZGOS CRÍTICOS (rompen el sistema)
═══════════════════════════════════════════════════
[N] Skill X usa cifras concretas sin nota de ejemplos ilustrativos
[N] Skill X contiene datos personales reales o un ejemplo fuera del perfil ficticio canónico
[N] Cross-reference [[skill-no-existe]] → roto
[N] Fórmula Epley en skill X usa /30 pero en skill Y usa /33

═══════════════════════════════════════════════════
HALLAZGOS MEDIOS (confunden o crean drift)
═══════════════════════════════════════════════════
[N] Solapamiento de contenido entre A y B
[N] Agent X no invoca skill Y aunque lo menciona 4 veces
[N] Skill X con scope creep (cubre más de lo prometido)

═══════════════════════════════════════════════════
HALLAZGOS MENORES (cosméticos)
═══════════════════════════════════════════════════
[N] Skill X tiene frontmatter description de 60 chars (recomendado ≥80)
[N] Naming kebab-case con guion bajo (debería ser solo guion)

═══════════════════════════════════════════════════
COBERTURA
═══════════════════════════════════════════════════
- Agentes con lista de skills actualizada: N/N_total
- Skills con nota de ejemplos ilustrativos correcta: N/N_total
- Skills sin datos personales y con ejemplos alineados al perfil ficticio: N/N_total
- Cross-references válidos: N/N_total
- Fórmulas consistentes: N/N_total
- Solapamientos detectados: N

Estado: [APTO · CLEAN] / [REQUIERE FIX]
```

## Criterios de severidad

| Severidad | Definición | Acción |
|---|---|---|
| Crítico | Rompe ejecución · refs rotos · fórmulas incoherentes · cifras sin etiqueta · datos personales reales | Bloquea release del harness · fix antes de seguir |
| Medio | Confunde · listas desactualizadas · scope creep · solapamientos | Fix en próxima iteración |
| Menor | Cosmético · descripciones cortas · naming sub-óptimo | Acumular y limpiar batch mensual |

## Anti-patrones documentados (incidentes históricos)

- ❌ **Crear nuevo skill sin actualizar agentes que lo invocan** (B5 del Plan 2)
- ❌ **Copiar contenido de otro skill sin delegar con `[[link]]`** (recovery-optimizer:71-77 duplicaba pre-session-mental-prep)
- ❌ **Usar cifras concretas sin nota de ejemplos ilustrativos** (plan-abc-knee y sleep-debt-protocol pre-Plan-1)
- ❌ **Dejar datos de una persona real en los ejemplos** en lugar del perfil ficticio canónico
- ❌ **Frontmatter `name:` distinto del nombre de carpeta del skill** (o del filename del agente)
- ❌ **Referenciar skills por la ruta plana antigua** en lugar de `skills/<name>/SKILL.md`
- ❌ **Cross-references con nombres en plural cuando el archivo es singular** (`[[skills]]` vs `[[skill-name]]`)
- ❌ **Fórmulas idénticas escritas distintas** (`/30` vs `/ 30` vs `÷ 30`)
- ❌ **Skills "comodín"** que cubren 5 temas distintos (debe dividirse)

## Aplicación · cuándo y por quién

- **Tras cualquier Plan de expansión** (como Plan 2 actual): ejecutar antes de cerrar
- **Tras corrección crítica** (como Plan 1): ejecutar para confirmar
- **Coach/desarrollador del harness**: ejecutar mensual
- **Antes de exponer el harness a un nuevo perfil de usuario**: ejecutar para garantizar generalidad

## Sinergias

- `[[plan-audit-checklist]]` · este skill ES el plan-audit-checklist del harness
- `[[surgical-4-pass-methodology]]` · aplicar los 4 pases al propio sistema
- `[[longitudinal-analysis-dimensions]]` · auditar el crecimiento del harness en el tiempo (líneas, skills, agentes)

## Tests automáticos completos · script all-in-one

```bash
#!/bin/bash
# harness-self-audit.sh · run desde HARNESS/

cd "$(dirname "$0")"
CRITICAL=0
MEDIUM=0
MINOR=0

echo "=== HARNESS SELF-AUDIT · $(date +%Y-%m-%d) ==="

# Capa 1 · layout + naming consistency
echo ""
echo "[Capa 1] Layout + naming consistency"
echo "  skills: $(ls -d skills/*/ | wc -l) · agentes: $(ls agents/*.md | wc -l)"
for f in skills/*.md; do
    [ -e "$f" ] && { echo "  ✗ LAYOUT ANTIGUO: $f"; CRITICAL=$((CRITICAL+1)); }
done
for f in skills/*/SKILL.md agents/*.md; do
    name_yaml=$(grep -m1 "^name:" "$f" | sed 's/name: //')
    case "$f" in
        skills/*) name_file=$(basename "$(dirname "$f")") ;;
        *)        name_file=$(basename "$f" .md) ;;
    esac
    [ "$name_yaml" != "$name_file" ] && { echo "  ✗ MISMATCH: $f"; CRITICAL=$((CRITICAL+1)); }
done

# Capa 3 · cross-references
echo ""
echo "[Capa 3] Cross-references"
python3 -c "
import re, os
refs = set()
skills = set(d for d in os.listdir('skills') if os.path.isfile(f'skills/{d}/SKILL.md'))
agents = set(f[:-3] for f in os.listdir('agents') if f.endswith('.md'))
for d in skills:
    refs |= set(re.findall(r'\[\[([a-z-0-9]+)\]\]', open(f'skills/{d}/SKILL.md').read()))
for a in agents:
    refs |= set(re.findall(r'\[\[([a-z-0-9]+)\]\]', open(f'agents/{a}.md').read()))
rotos = refs - skills - agents
print(f'  {len(refs)} refs · {len(rotos)} rotos')
if rotos: print(f'  ✗ ROTOS: {sorted(rotos)}')
"

# Capa 6 · fórmulas Epley consistentes
echo ""
echo "[Capa 6] Fórmula Epley"
forms=$(grep -hE "1 ?\+ ?reps ?/ ?30|peso ?\* ?\(1 ?\+ ?reps" skills/*/SKILL.md | sort -u | wc -l)
echo "  $forms variantes distintas detectadas"

echo ""
echo "=== RESUMEN ==="
echo "Críticos: $CRITICAL"
echo "Medios: $MEDIUM"
echo "Menores: $MINOR"
[ $CRITICAL -eq 0 ] && echo "Estado: CLEAN ✓" || echo "Estado: REQUIERE FIX ✗"
```
