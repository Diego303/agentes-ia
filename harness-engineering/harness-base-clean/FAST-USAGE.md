# FAST-USAGE.md — Prompts esenciales

> Copia, pega y edita lo que va entre `< >`. Configuración actual: flujo
> `simple`, perfil `clean`, modo en `.claude/harness.toml`.

## 1. Tengo una idea → feature especificada hasta GATE#1

```text
<Describe la idea: objetivo, alcance, restricciones y cualquier evidencia útil.>

Conviértela en una feature del harness (feature-kickoff) y, cuando la
confirme, planifícala hasta GATE#1 (sdd-feature-planning).
```

## 2. Arrancar una feature ya registrada

```text
Arranca <ID> siguiendo HARNESS.md.
[Opcional] Usa también estos especialistas: <nombre (punto de inserción)>.
```

## 3. Decidir en GATE#1

```text
/approve <ID> <comentario o alternativa elegida>
/reject <ID> <cambios concretos que pides>
```

Confirma el comando `feature.py transition ... --by human` cuando Claude Code
te lo pida: es tu firma.

## 4. Continuar una feature interrumpida

```text
Reanuda <ID> desde el último estado seguro (feature-resume). Antes de lanzar
nada, dime en qué fase está, qué falta y qué vas a hacer.
```

## 5. Estado y costes

```text
¿Cómo va <ID> y cuánto ha costado hasta ahora? (feature-cost)
```

o directamente:

```bash
python3 .claude/tools/feature.py status
python3 .claude/tools/ledger.py cost <ID>
```

## 6. Revisar la salud del harness

```text
/harness-doctor
```

## Atajos

| Comando | Efecto |
| --- | --- |
| `/feature-kickoff` | idea → feature registrada |
| `/sdd-feature-planning <ID>` | exploración y diseño hasta GATE#1 |
| `/approve <ID> [...]` · `/reject <ID> <...>` | decisión humana en GATE#1 |
| `/feature-resume <ID>` | reanudar con seguridad |
| `/feature-cost [ID]` | informe de coste y presupuesto |
| `/harness-doctor` | validar el harness |
| `/project-bootstrap` | adaptar el harness a este repositorio |
