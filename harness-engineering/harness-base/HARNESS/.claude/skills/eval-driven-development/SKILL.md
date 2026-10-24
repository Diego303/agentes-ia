---
name: eval-driven-development
description: Diseña evaluaciones reproducibles para aplicaciones, prompts, agentes o workflows con IA. Usala cuando se pida medir calidad, comparar versiones, prevenir regresiones o decidir si una mejora de IA funciona; no sustituye tests deterministas ordinarios.
---

# Eval-Driven Development

## Procedimiento

1. Define la decision que la evaluacion debe informar y el fallo que debe
   detectar.
2. Reune casos representativos, bordes y negativos sin contaminar el conjunto
   de prueba con la respuesta esperada.
3. Prioriza asserts deterministas. Usa rubricas o jueces de IA solo para
   propiedades que no admiten comprobacion objetiva.
4. Conserva una linea base y compara la nueva version con las mismas entradas.
5. Registra resultados por caso, falsos PASS, coste, latencia y varianza cuando
   esten disponibles.
6. Revisa manualmente muestras y desacuerdos antes de convertir la puntuacion
   en gate.
7. Añade al conjunto de regresion los fallos reales que se repitan.

## Limites

- No reduzcas calidad a una unica nota generada por otro modelo.
- No optimices contra el conjunto de prueba hasta sobreajustarlo.
- No uses evals probabilisticas donde un test determinista basta.

## En este harness

- Para skills y agentes del bundle, los casos y la línea base se montan con la
  skill `skill-creator` (`evals/evals.json`, con y sin la skill); para plugins,
  con `claude plugin eval` (skill `plugin-eval`).
- Las evaluaciones lanzan sesiones reales de Claude y gastan dinero: acuerda el
  presupuesto con el humano antes de ejecutarlas.
