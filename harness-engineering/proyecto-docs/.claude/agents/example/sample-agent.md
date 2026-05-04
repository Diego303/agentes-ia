# Agent: Sample Agent (ejemplo)

> **Reemplaza este archivo con tu propio agente.** Sigue el contrato de 5
> secciones que usan los agentes de orquestación en `.claude/agents/`.

## Rol
[Una frase describiendo la responsabilidad **única** de este agente. Si
necesitas dos frases, probablemente son dos agentes.]

## Inputs esperados
- [Qué archivo o artefacto del paso anterior necesita.]
- [Qué partes del repo necesita leer.]
- [Qué información humana asume disponible.]

## Procedimiento
1. [Primer paso concreto.]
2. [Segundo paso.]
3. [Continúa numerando hasta el último paso. Cada paso debe ser observable
   por un humano que mira tu output.]

## Output
- [Ruta exacta del archivo que escribe, con sus secciones esperadas.]
- [Otros side-effects bien acotados.]

**Siguiente paso**: [Quién lee tu artefacto. Sé explícito: nombre del
agente o el gate humano. Ej.: "**Proposer** lee tu `mi-output.md` para
formular la propuesta".]

**Cuándo parar y pedir ayuda**:
- [Inputs faltantes: ¿qué artefacto previo es bloqueante? Documenta el
  fallback si lo hay; si no, para.]
- [Ambigüedad irreductible: ¿qué tipo de pregunta no debes resolver tú?]
- [Dependencia externa caída: ¿qué pasa si el comando/herramienta falla?]

## Anti-patterns
- ❌ [Algo que este agente NO debe hacer aunque sea tentador.]
- ❌ [Otra cosa.]
- ❌ [Mezclarse con la responsabilidad de otro agente — dilo explícito.]
