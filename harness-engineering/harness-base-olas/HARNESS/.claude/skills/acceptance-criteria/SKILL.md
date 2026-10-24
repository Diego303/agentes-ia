---
name: acceptance-criteria
description: Esquema y reglas para escribir SDD/acceptance.yaml del harness - checks ejecutables (command, file) e inspecciones con evidencia, trazados a FR/NFR, seguros y no triviales. Úsala al diseñar o revisar criterios de aceptación, al interpretar acceptance-results.json o cuando el validador marque errores de acceptance o de trazabilidad.
---

# Acceptance criteria

## Por qué importa

`acceptance.yaml` es la definición de "terminado". El humano lo aprueba en
GATE#1, queda congelado (`spec.lock.json`), `run_acceptance.py` lo ejecuta tal
cual y el reviewer decide el veredicto con esa evidencia. Un check vago o
trivial convierte un PASS en una opinión; un check peligroso se ejecutaría sin
más confirmación.

## Esquema v1

```yaml
version: 1
feature_id: AUTH-003              # el ID real de la feature
checks:
  - id: AC-001                    # AC-NNN, único
    title: Login rechaza contraseñas incorrectas
    covers: [FR-01]               # IDs de requirements.md (FR-NN / NFR-NN)
    kind: command
    required: true
    command: pytest -q tests/test_login.py::test_wrong_password
    cwd: .                        # relativo al repo, sin '..'
    timeout_seconds: 120          # 1-3600
    expected_exit_code: 0
  - id: AC-002
    title: No quedan contraseñas en claro en el módulo
    covers: [NFR-02]
    kind: file
    required: true
    path: src/auth/login.py
    expected: exists              # exists | absent
    not_contains: "password\\s*=\\s*['\"]"   # regex opcional (contains / not_contains)
  - id: AC-003
    title: El mensaje de error no revela si el usuario existe
    covers: [FR-03]
    kind: inspection
    required: true
    procedure: Intenta entrar con un usuario inexistente y con uno existente con clave errónea.
    expected: Ambos casos muestran el mismo mensaje genérico.
```

`run_acceptance.py` marca cada check como `pass`, `fail`, `blocked`
(herramienta ausente: exit 126/127) o `manual` (inspecciones). Exit 0 si pasan
todos los obligatorios ejecutables, 1 si alguno falla, 2 si hay bloqueo.

## Reglas

1. **Trazabilidad**: cada FR y NFR de `requirements.md` aparece en el `covers`
   de algún check, `covers` solo usa IDs existentes y cada FR tiene al menos
   una tarea en `tasks.md`. El validador lo comprueba.
2. **Evidencia ejecutable**: al menos un check obligatorio `command` o `file`.
   Prefiere `command` que ejecute pruebas del comportamiento; usa `file` para
   artefactos (docs, config, migraciones) y patrones prohibidos.
3. **Inspecciones solo si no hay alternativa** automática (textos, UX). Con
   `procedure` reproducible y `expected` observable; el reviewer anota la
   evidencia en `verification-result.yaml`.
4. **Un buen check falla hoy y pasa cuando la feature está hecha** (salvo la
   regresión). Nada de `echo`, `true`, `exit 0` ni comprobar que existe un
   archivo que el builder puede crear vacío sin un `contains`.
5. **Comandos seguros**: no interactivos (stdin cerrado), deterministas,
   idempotentes, rápidos, sin red salvo necesidad real, sin efectos
   destructivos y sin leer secretos. El validador rechaza `sudo`, `rm -r` sobre
   raíz/home, git que escribe, `curl ... | sh` y cualquier referencia a
   secretos (`.env`, claves, `~/.ssh`...; `.env.example` sí se permite).
   Marca como **sensibles** la red externa y el código en línea
   (`python -c`, `node -e`, `bash -c`, `eval`): son válidos, pero solo el
   humano puede aprobarlos. Prefiere un test o un script versionado del
   proyecto antes que código en línea.
6. **Regresión del proyecto**: incluye el comando de pruebas detectado en
   `context.md` o `bash .claude/bootstrap/verify.sh` si está configurado
   (sin la marca `HARNESS_VERIFY_PLACEHOLDER`).
7. **Obligatorio de verdad**: `required: true` solo si su fallo debe impedir el
   archivo; lo demás, `false`.
8. **YAML estricto**: entrecomilla valores con `": "` o `" #"`; sin anclas ni
   varios documentos. En regex dentro de comillas dobles, escapa `\\`.

## Validar

```bash
python3 .claude/tools/validate_harness.py --feature <ID> --pre-gate
```
