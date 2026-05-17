---
name: sleep-debt-protocol
description: Invoke when the user reports poor sleep (1 night, 2-3 nights, 4+ nights below threshold) or persistent fatigue signs. Provides graduated training adjustments and "plan pause" rules.
---

# Sleep Debt Protocol · qué hacer cuando no has dormido

## Asunción base

El plan asume **6 h consolidadas** como mínimo recuperable. Si cae por debajo, el plan se adapta antes de la siguiente sesión.

Lo importante: distinguir entre **1 noche aislada** (gestionable) y **deuda acumulada** (el plan se pausa).

## Tabla de decisión

| Situación | Acción HOY | Volumen | Intensidad | RPE max | AMRAP |
|---|---|---|---|---|---|
| 1 noche < 5 h aislada | Mantén sesión | -1 serie en compuesto | -10 % | 7 | Sí pero peso reducido |
| 2-3 noches < 5 h en 7 días | 1 sesión "técnica" esa semana (la elige el usuario) | 50 % vol en esa sesión técnica | -25 % en sesión técnica | 6-7 | Off en sesión técnica |
| 4+ noches ≤ 5 h en 7 días (DEUDA REAL) | **El plan se pausa toda la semana** | -20 % toda la semana | -10 % | 7 | **OFF toda la semana** |
| Deuda persiste 2 sem seguidas | Deload completo extra 1 sem | 50 % vol | -25 % | 6-7 | Off |

## Lógica programática

- **1 noche**: cuerpo recupera con micro-ajustes. Mantener estímulo es OK.
- **2-3 noches**: empieza acumulación · una sesión técnica baja la carga sin perder patrón motor.
- **4+ noches**: estás en sobrecarga sistémica · cortisol elevado · síntesis proteica comprometida · entrenar fuerte = perdida neta. **NO se ejecuta el plan**, solo se mantiene patrón.
- **Persistencia 2 sem**: el cuerpo necesita reset completo antes de retomar. Deload extra.

## Cómo medir "buen sueño"

No es solo horas, es **continuidad**:
- **0-1 interrupción** = sueño consolidado · cuenta horas reales
- **2+ interrupciones** = sueño fragmentado · resta -1 h del total real

Ejemplo: 6,5 h con 3 despertares ≈ 5,5 h efectivas.

### Métricas diarias (al despertar, 60 s)

1. **Horas totales** (meta > 6 h)
2. **Continuidad 0-10** (10 = sin despertar, 1 = fragmentado total)
3. **Test mental despertar**: "¿abro los ojos pensando ya está o todavía me quedaba?"
   - "Ya está" = consolidado
   - "Todavía me quedaba" = deuda
4. **FC reposo al despertar** vs media móvil 30 días
   - +5 bpm sostenido 3-4 días = sobrecarga
5. **Sensación subjetiva 1-10**

Plantilla Telegram diaria:
```
DD/MM · FC: XX bpm · Sueño: X h · Continuidad __/10 · Sensación: __/10
[Notas: dolor, motivación]
```

## Las 5 reglas de las 6 horas (maximizar lo que sí tienes)

1. **Cafeína cutoff 12 h pre-sueño**. Si te acuestas 23, último café 11 h máximo.
2. **Cena ≥ 2 h antes de acostarte** + proteína lenta 30 min antes (caseína/yogur griego/requesón).
3. **Pantallas off 30 min antes** o luz cálida (modo nocturno).
4. **Habitación 18-20 °C** + oscuridad completa (cortinas opacas o antifaz).
5. **Magnesio glicinato 200-400 mg** 30-45 min antes de dormir.

Bonus regla: **misma hora de acostarse todos los días** ± 1 h, también fin de semana. Regularidad > total.

## Trigger de deload extra (independientemente del sueño)

Si **2 o más** de estas señales aparecen, próxima semana = deload extra:

1. Peso planificado se siente RPE 9-10 dos sesiones consecutivas cuando debería ser RPE 8
2. FC reposo +5 bpm sobre media 30 días durante 3-4 días
3. Dolor articular nuevo (hombro/rodilla/codo) que no es agujetas
4. Pérdida clara de motivación (la cabeza es parte del cuerpo)
5. Sueño consolidado < 5,5 h dos días seguidos sin causa externa (no hijo enfermo, no estrés laboral puntual)
6. Pulso visible en el ojo o párpado que tiembla varios días
7. Caída de fuerza inexplicable en accesorios (dominadas que hacías limpias ahora cuestan)

## Aplicación · agente coach-realtime

Cuando el usuario dice "dormí mal":
1. ¿Cuántas h? ¿Cuántas interrupciones?
2. ¿Es una noche aislada o llevas varias?
3. Cuenta noches < 5 h en últimos 7 días
4. Aplica fila de la tabla correspondiente
5. NO escales agresivamente · es mejor pausa parcial que sesión basura

## Casos típicos resueltos

### "Dormí 4 h anoche, ¿hago la sesión?"
- 1 noche aislada · mantén sesión · -1 serie · intensidad -10 % · RPE max 7 · AMRAP con peso reducido.

### "Llevo 3 noches a 5 h por trabajo"
- 1 sesión técnica esta semana. Elige la que se cae peor (típico viernes si la sem ha sido dura).
- Las otras 2 sesiones normales.

### "Llevo 5 noches a 4 h (hijo enfermo)"
- Plan en pausa toda la semana. Mantén estímulo mínimo con paseos + 1 sesión técnica si quieres.
- La semana se repite cuando vuelva el sueño.

### "Llevo 2 semanas durmiendo mal"
- Deload extra 1 sem (50 % vol, -25 % intensidad, RPE 6-7, sin AMRAP)
- Después de la sem deload, retoma el plan donde lo dejaste.
- Si tras deload sigue mal sueño: revisa causas externas (estrés laboral · cafeína · pantallas · cuarto · pareja)
