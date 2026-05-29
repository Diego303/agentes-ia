---
name: harness-self-audit
description: Invoke after creating or modifying any skill/agent in this HARNESS to verify consistency (cabecera "perfil de referencia" present where needed, cross-references [[name]] valid, list of invoked skills up-to-date in each agent, no content duplication across skills, frontmatter complete, math formulas consistent across files). The plan-auditor audits external plans; this skill audits the HARNESS itself.
---

# Harness Self-Audit · meta-auditoría del propio harness

> **Nota · skill 100% general · meta-tooling del harness, no del entrenamiento.**

## Propósito

El plan-auditor audita planes externos. El surgical-report-builder analiza datos longitudinales. **Pero el harness mismo crece sin meta-checklist** · cada extracción nueva puede introducir gaps: skills sin cabecera de perfil, cross-references rotos, listas de skills invocados desactualizadas en agentes, contenido duplicado entre skills.

Este skill define **7 capas de meta-auditoría**. Ejecutarlo tras cada modificación importante previene los patrones de error documentados en la auditoría quirúrgica de may 2026.

## Cuándo invocar

- **Inmediatamente** tras crear un nuevo skill/agente
- **Tras editar** un skill que afecta múltiples agentes
- **Mensualmente** como review preventiva
- **Antes de declarar** el harness "production-ready" para un nuevo perfil de usuario

## Las 7 capas de meta-auditoría

### Capa 1 · estructura de archivos

- Cada skill en `skills/`, cada agente en `agents/`
- Naming kebab-case sin espacios ni acentos
- Frontmatter con `name:` (matches filename exacto) y `description:` (presente, ≥80 chars)
- Frontmatter opcional para agentes: `tools:`, `model:`
- Filename = `name` del frontmatter + `.md`

#### Script de validación

```bash
# Validar nombres
for f in skills/*.md agents/*.md; do
    name_yaml=$(grep -m1 "^name:" "$f" | sed 's/name: //')
    name_file=$(basename "$f" .md)
    if [ "$name_yaml" != "$name_file" ]; then
        echo "MISMATCH: $f · YAML name='$name_yaml' vs filename='$name_file'"
    fi
done

# Validar description ≥80 chars
for f in skills/*.md agents/*.md; do
    desc=$(grep -m1 "^description:" "$f" | sed 's/description: //')
    if [ ${#desc} -lt 80 ]; then
        echo "SHORT DESC ($((${#desc})) chars): $f"
    fi
done
```

### Capa 2 · cabeceras "perfil de referencia"

**Regla**: cada skill que mencione cifras específicas (kg, mg, fechas, %) DEBE tener cabecera de generalidad en las primeras 10 líneas tras el frontmatter.

Skills 100% generales (sin cifras concretas) NO la necesitan.

#### Detección

```bash
for f in skills/*.md; do
    # ¿tiene cifras específicas en kg/mg/fechas?
    has_numbers=$(grep -cE "[0-9]+ ?(kg|mg|sem|días|h|min|reps|%|cal|g/kg)" "$f")
    has_header=$(grep -c "perfil de referencia\|skill general aplicable" "$f")
    if [ "$has_numbers" -gt 10 ] && [ "$has_header" -eq 0 ]; then
        echo "FALTA cabecera: $f ($has_numbers cifras detectadas)"
    fi
done
```

### Capa 3 · cross-references `[[name]]` válidos

Toda referencia `[[skill-name]]` debe apuntar a un archivo real en `skills/`.

#### Script

```python
import re, os

ROOT = "skills"
refs = set()
for f in os.listdir(ROOT):
    if not f.endswith(".md"): continue
    content = open(f"{ROOT}/{f}").read()
    refs |= set(re.findall(r'\[\[([a-z-0-9]+)\]\]', content))

skills_existentes = set(f[:-3] for f in os.listdir(ROOT) if f.endswith(".md"))
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
    huerfanos = [n for n, c in counts.items() if c >= 3 and n not in declarados and os.path.exists(f"skills/{n}.md")]
    if huerfanos:
        print(f"{agente}: huérfanos {huerfanos}")
```

### Capa 5 · solapamiento de contenido

Detectar párrafos copiados textualmente entre 2+ skills.

**Regla**: si dos skills explican el mismo protocolo, uno debe ser **canónico** y el otro debe **delegar** con `[[link]]`.

#### Detección heurística

```bash
# Buscar frases idénticas de ≥80 caracteres en 2+ archivos
for skill in skills/*.md; do
    grep -oE ".{80,}" "$skill" | sort -u > /tmp/frases_$(basename $skill .md).txt
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
grep -h "1 + reps/30\|1 + reps / 30" skills/*.md
# Todas las apariciones deben tener formato idéntico
```

### Capa 7 · coherencia de scope (cada skill cumple su YAML description)

Leer la `description:` YAML de cada skill y verificar que el contenido del cuerpo:
1. **Cumple** lo que promete el description (no under-deliver)
2. **NO excede** lo que promete (no scope creep)

#### Heurística

```bash
for f in skills/*.md; do
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
[N] Skill X usa cifra "80 kg" sin cabecera de perfil
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
- Skills con cabecera de perfil correcta: N/N_total
- Cross-references válidos: N/N_total
- Fórmulas consistentes: N/N_total
- Solapamientos detectados: N

Estado: [APTO · CLEAN] / [REQUIERE FIX]
```

## Criterios de severidad

| Severidad | Definición | Acción |
|---|---|---|
| Crítico | Rompe ejecución · refs rotos · fórmulas incoherentes · cifras sin etiqueta | Bloquea release del harness · fix antes de seguir |
| Medio | Confunde · listas desactualizadas · scope creep · solapamientos | Fix en próxima iteración |
| Menor | Cosmético · descripciones cortas · naming sub-óptimo | Acumular y limpiar batch mensual |

## Anti-patrones documentados (incidentes históricos)

- ❌ **Crear nuevo skill sin actualizar agentes que lo invocan** (B5 del Plan 2)
- ❌ **Copiar contenido de otro skill sin delegar con `[[link]]`** (recovery-optimizer:71-77 duplicaba pre-session-mental-prep)
- ❌ **Usar cifras del perfil sin cabecera de etiquetado** (plan-abc-knee y sleep-debt-protocol pre-Plan-1)
- ❌ **Frontmatter `name:` distinto del filename**
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

# Capa 1 · naming consistency
echo ""
echo "[Capa 1] Naming consistency"
for f in skills/*.md agents/*.md; do
    name_yaml=$(grep -m1 "^name:" "$f" | sed 's/name: //')
    name_file=$(basename "$f" .md)
    [ "$name_yaml" != "$name_file" ] && { echo "  ✗ MISMATCH: $f"; CRITICAL=$((CRITICAL+1)); }
done

# Capa 3 · cross-references
echo ""
echo "[Capa 3] Cross-references"
python3 -c "
import re, os
refs = set()
for f in os.listdir('skills'):
    refs |= set(re.findall(r'\[\[([a-z-0-9]+)\]\]', open(f'skills/{f}').read()))
for f in os.listdir('agents'):
    refs |= set(re.findall(r'\[\[([a-z-0-9]+)\]\]', open(f'agents/{f}').read()))
skills = set(f[:-3] for f in os.listdir('skills'))
agents = set(f[:-3] for f in os.listdir('agents'))
rotos = refs - skills - agents
print(f'  {len(refs)} refs · {len(rotos)} rotos')
if rotos: print(f'  ✗ ROTOS: {sorted(rotos)}')
"

# Capa 6 · fórmulas Epley consistentes
echo ""
echo "[Capa 6] Fórmula Epley"
forms=$(grep -hE "1 ?\+ ?reps ?/ ?30|peso ?\* ?\(1 ?\+ ?reps" skills/*.md | sort -u | wc -l)
echo "  $forms variantes distintas detectadas"

echo ""
echo "=== RESUMEN ==="
echo "Críticos: $CRITICAL"
echo "Medios: $MEDIUM"
echo "Menores: $MINOR"
[ $CRITICAL -eq 0 ] && echo "Estado: CLEAN ✓" || echo "Estado: REQUIERE FIX ✗"
```
