# Instrucciones para Claude

Este proyecto sigue **Spec-Driven Development (SDD)** orquestado por agentes
especializados en `.claude/agents/`.

## Trabajar en una feature

1. **Selecciona** una feature de `feature_list.json` con `status: proposed`.
2. **Crea** la carpeta `progress/<feature-id>/` si no existe.
3. **Ejecuta los agentes en orden**:
   Explorer → Proposer → **[GATE#1]** → (Spec-writer ‖ Designer)
   → Task-planner → Implementer → **[GATE#2]** → Verifier → Archiver.
4. **Para en cada gate** y espera aprobación humana antes del siguiente agente.
5. Cuando Archiver termina, marca la feature en `feature_list.json` como
   `status: archived`.

## Contrato de agentes

Cada `.claude/agents/<nombre>.md` tiene 5 secciones fijas: **Rol**, **Inputs
esperados**, **Procedimiento**, **Output**, **Anti-patterns**.

La sección **Output** lleva al final dos sub-bloques estandarizados:

- **Siguiente paso**: indica quién leerá el artefacto y cuándo.
- **Cuándo parar y pedir ayuda**: lista escenarios de fallo (inputs
  faltantes, ambigüedad irreductible, dependencia externa caída).

Al invocar un agente:

- Lee su MD primero. No lo resumas, síguelo literalmente.
- No fusiones responsabilidades entre agentes.
- No saltes el output declarado: si dice "escribe `progress/<id>/spec.md`",
  ese archivo debe existir antes de continuar.
- **Nunca invoques al siguiente agente desde dentro de uno**. Sólo deja
  el artefacto; el orquestador (humano o `harness status`) decide qué se
  ejecuta a continuación.

## Verificación

`profile.yaml` declara el `verify_stack` (lista ordenada de herramientas que
deben pasar antes del archivo). El agente **Verifier** ejecuta cada
herramienta y registra resultados en `progress/<id>/verification.md`. Si una
herramienta falla, NO continúes con Archiver: vuelve a Implementer.

## Persistencia

Los artefactos en `progress/<id>/` son **append-only**. Si encuentras una
contradicción con un artefacto anterior, escribe la tuya con referencia
explícita al previo en lugar de editar el anterior.

## Memoria a largo plazo

`feature_list.json` es la fuente de verdad de qué features existen, su estado
y prioridad. No la dupliques en otros archivos. Los agentes la leen al
arrancar.

Ver `AGENTS.md` para el contrato completo de orquestación.
