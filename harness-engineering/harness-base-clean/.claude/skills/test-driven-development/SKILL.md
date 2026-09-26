---
name: test-driven-development
description: Disciplina rojo-verde-refactor para implementar features y corregir bugs con pruebas que demuestran el comportamiento. Úsala antes de escribir código de producción en un proyecto con framework de pruebas, al corregir un bug (primero la prueba que lo reproduce) o al juzgar si las pruebas de un cambio prueban algo real.
---

# Test-Driven Development

> Adaptada al harness a partir de `test-driven-development` de obra/superpowers (MIT).

## Regla

No hay código de producción sin una prueba que haya fallado antes. Si no la
viste fallar, no sabes si prueba lo que crees.

## Ciclo

1. **Rojo**: escribe una prueba mínima de un comportamiento del requisito:
   nombre claro, código real, mocks solo si son inevitables.
2. **Verifica el rojo**: ejecútala. Debe fallar porque falta la funcionalidad,
   no por un error de sintaxis. Si pasa a la primera, estás probando algo que
   ya existe: corrige la prueba.
3. **Verde**: escribe el código mínimo que la hace pasar. Sin opciones ni
   generalizaciones que la prueba no pide.
4. **Verifica el verde**: pasa esa prueba y la suite completa del proyecto, no
   solo tu archivo, con la salida limpia. Cualquier fallo que veas, aunque no
   lo hayas causado tú, va al informe con su nombre.
5. **Refactor**: limpia con todo en verde, sin añadir comportamiento.
6. Repite con el siguiente comportamiento.

## Pruebas que valen

- Una conducta por prueba; si el nombre lleva "y", divídela.
- Antes de escribirla, nombra el cambio de producción que la haría fallar.
- Asertos sobre el comportamiento real, nunca sobre el mock.
- Utilidades de prueba fuera del código de producción.
- Entiende los efectos de una dependencia antes de sustituirla por un doble.

## Bugs

Primero la prueba que reproduce el bug (rojo), después el arreglo (verde). La
prueba queda como regresión.

## En el harness

- Relaciona cada prueba con su requisito (`FR-NN` en el nombre o en un
  comentario) para que el reviewer vea la cobertura.
- Si el proyecto no tiene framework de pruebas, no lo instales por tu cuenta:
  apóyate en `acceptance.yaml` y anota la carencia en `implementation.md`.
- Nunca cambies `acceptance.yaml` para que encaje con tus pruebas.

## Racionalizaciones que indican que te estás saltando el ciclo

| Excusa | Realidad |
| --- | --- |
| "Es demasiado simple para probarlo" | El código simple también se rompe y la prueba cuesta segundos. |
| "Lo pruebo después" | Una prueba escrita después pasa a la primera y no demuestra nada. |
| "Ya lo probé a mano" | No es repetible ni deja registro. |
| "Borrar lo hecho es desperdiciar trabajo" | Coste hundido: el código sin prueba previa no es fiable. |
| "Primero necesito explorar" | Bien: descarta la exploración y empieza con el ciclo. |

Señales de alarma: código antes que la prueba, una prueba que pasa a la
primera, no saber por qué falla, "solo esta vez". Ante cualquiera, vuelve al paso 1.
