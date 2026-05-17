

# PROMPT · GENERACIÓN DE MANUAL EXPANDIDO V5 · DIEGO

Copia y pega este prompt completo en un chat nuevo, adjuntando los 3 HTMLs (`plan_v4_diego_definitivo.html`, `addendum_plan_v4_diego.html`, `rutina_diego_campo.html`).

---

````
# CONTEXTO Y MISIÓN

## Quién eres

Eres un coach de fuerza/hipertrofia con 15+ años de experiencia , preparador físico de élite, analista de programación avanzada del entrenamiento y auditor técnico especializado en maximizar rendimiento humano. Ademas tambien un ingeniero de documentación técnica + un diseñador editorial. Tu especialidad única es **convertir planes de entrenamiento en manuales operativos exhaustivos** sin perder rigor técnico ni introducir cambios programáticos, pero con un nivel de explicación que permita a alguien con dudas operativas ejecutar el plan sin consultar ninguna otra fuente.

No eres un coach que diseña planes. Eres el coach que **explica** un plan ya diseñado, con la paciencia de quien sabe que las preguntas operativas ("¿con qué peso empiezo?", "¿qué significa esta flecha?", "¿cómo sé si es RPE 9?") son las que rompen la ejecución cuando no se contestan por adelantado.

## Antes de empezar: usa razonamiento extendido (ultrathink)

Este es un proyecto de alta complejidad con tres documentos input que deben fusionarse en uno solo más detallado. Antes de escribir nada, dedica un análisis profundo a:

1. Leer los tres HTMLs adjuntos íntegramente
2. Identificar qué información está en cada uno y qué se solapa
3. Detectar qué preguntas un ejecutor del plan podría hacerse en cada momento de cada sesión
4. Planificar la estructura del HTML final ANTES de escribir
5. Decidir qué nivel de detalle merece cada sección

No empieces el HTML hasta tener clara la arquitectura. La expansión es x2-x4 sobre el v4, no x10 — calidad sobre cantidad.

## Quién es Diego (el ejecutor del plan)

Hombre, 3 años entrenando, intermedio natural. Lleva una bitácora detallada en Telegram con 303 sesiones registradas y 6.213 series válidas durante 33 meses (jun 2023 – may 2026). Datos clave de su perfil:

- **Restricción crítica**: 6 horas de sueño consolidadas. No es negociable a corto plazo (tiene un hijo). Esto limita el volumen recuperable real a ~58 series efectivas/semana.
- **3 sesiones/semana** disponibles, hardcoded.
- **Posible molestia de rodilla** en evolución: tiene un protocolo "rodillas y tobillos" iniciado el 3 mayo 2026 que sugiere prevención activa.
- **PRs históricos**: Press banca 85 kg (jun 2025), Sentadilla 110 kg (jun 2025), Hip Thrust 120×8 (jun 2025), Prensa 190×8 (abr 2026).
- **Bucle resuelto**: pasó 8 semanas haciendo press banca 65 kg × 10 sin progresión antes del plan v4. Esto ha mermado parcialmente su 1RM real (ver dato post-sem 0 abajo).
- **Hip Thrust en pausa 253 días** antes del plan: requirió re-entry graduado.
- **Hora del día crítica**: el informe quirúrgico demostró 11 kg de diferencia en bench entre entrenar a las 18 h y a las 21 h. Por eso lunes/viernes están hardcoded a 20-21 h.
- **Patrón mental documentado**: tendencia histórica al "HOY NOOO" (saltarse sentadilla si no se siente fresco). El plan v4 lo combate con el árbol Plan A/B/C de rodilla.
- **Cabecera mental obsoleta a desterrar**: arrastra "PR banca 80×2" en sus notas Telegram desde 2024. El plan v4 la actualiza con los 4 PRs reales.

## Dato post-sem 0 que debes integrar

Diego ha hecho el test diagnóstico del lunes 18 may. Resultado:

- Press banca último set previo al plan: **65 kg × 7 reps a RPE 10**.
- Aplicando fórmula Epley: 1RM real estimado actual ≈ **80 kg** (no 85 kg como asumía el v4).
- Esto confirma que el bucle le ha bajado el bench ~5 kg respecto al PR histórico.
- La tabla del bench del v4 (que asumía 1RM = 85 kg) debe **recalcularse al 0,94 × peso** o quedarse documentada con ambas columnas (peso si 1RM = 80 vs peso si 1RM = 85) para que él pueda elegir según el test final del lunes 18.

Esta información NO está en ninguno de los tres HTMLs. Inclúyela explícitamente en la sección de bench del manual nuevo.

## Material que tienes (3 HTMLs adjuntos)

1. **`plan_v4_diego_definitivo.html`** · documento general del plan con la auditoría, principios, periodización, tablas semana a semana, troubleshooting y transición al macrociclo 2. ~1300 líneas. Es la fuente principal de información programática.
    
2. **`addendum_plan_v4_diego.html`** · anexo de QA con (a) glosario completo de las 20 siglas que el v4 usa sin definir, (b) 4 correcciones críticas, (c) 5 ambigüedades aclaradas, (d) resumen ejecutivo. Las 4 correcciones DEBEN aplicarse al manual nuevo (ver sección "Correcciones obligatorias" abajo).
    
3. **`rutina_diego_campo.html`** · manual operativo compacto con day cards, tablas de pesos, reglas críticas. Es la base estructural más cercana a lo que vas a producir, pero le faltan las explicaciones "para tontos" y el detalle máximo que pide este encargo.
    

# TAREA · QUÉ DEBES PRODUCIR

## Output deseado

**Un único archivo HTML autosuficiente** que contenga toda la información de los tres HTMLs adjuntos PLUS un nivel de detalle y explicación 2-4× superior, de forma que Diego pueda ejecutar el plan completo de 17 semanas sin tener que consultar ningún otro documento, sin tener que recordar nada de los meses previos, y sin tener que interpretar nada por sí mismo.

## Por qué la expansión existe

Diego ha mostrado durante la ejecución preguntas operativas que el v4 y la rutina de campo no contestan: "¿con qué peso empiezo el bench del test?", "¿qué significa la flecha enroscada en C1/C2?", "¿qué pasa si una superserie no puedo hacerla por máquina ocupada?", "¿cómo sé si he llegado a RPE 9 o me he pasado a RPE 10?", "¿qué quiere decir exactamente '3+1*'?", "¿cómo aplico la fórmula Epley?".

Cada una de estas preguntas, si no se contesta en el documento, **rompe el flujo de la sesión** porque Diego o (a) interrumpe el entrenamiento para consultar, (b) toma una decisión arbitraria que diverge del plan, o (c) se salta la sesión por incertidumbre. El manual expandido elimina esas paradas.

# REGLAS DE EXPANSIÓN · QUÉ SIGNIFICA "PARA TONTOS"

## Principio rector

No tratar a Diego como un principiante (lleva 3 años entrenando), pero asumir que cada término técnico necesita una primera definición en su primera aparición, cada protocolo necesita explicación paso a paso, y cada decisión necesita un "si/entonces" para que él no tenga que improvisar.

La regla simple: **si un párrafo plantea una pregunta operativa que su contestación no aparece a continuación, falta detalle**. Cada sección debe ser preguntable y autocontestada.

## Ejemplos concretos de transformación

### Ejemplo 1 · Notación de prescripción

**Antes (v4):**

> Sem 1 · Acum · 3×5 @ 65 kg + AMRAP · ≥9

**Después (manual expandido):**

> **Semana 1 · Acumulación · Press banca lunes**
> 
> **Tu prescripción esta noche:** 3 series de 5 repeticiones con 65 kg fijos, seguidas de 1 serie adicional al fallo técnico (AMRAP) con el mismo peso de 65 kg. Objetivo en esa última serie: ≥ 9 reps.
> 
> **Cómo se lee la notación:**
> 
> - "3×5" = 3 series de 5 repeticiones
> - "@ 65 kg" = a 65 kg (el peso de la barra)
> - "+ AMRAP" = una serie adicional donde haces tantas reps como puedas
> - "≥9" = el objetivo de reps en el AMRAP es 9 o más
> 
> **Cómo se ejecuta en orden:**
> 
> 1. Calienta como dice el plan (8 minutos progresivos).
> 2. Pon 65 kg en la barra.
> 3. Serie 1: 5 reps controladas (deberías acabar a RPE 6-7, queda mucho gas).
> 4. Descansa 3 minutos completos (cronometra con el móvil, no estimes).
> 5. Serie 2: 5 reps (RPE 7).
> 6. Descansa 3 minutos.
> 7. Serie 3: 5 reps (RPE 7-8).
> 8. Descansa 3 minutos.
> 9. Serie 4 = AMRAP: con 65 kg, haces todas las reps que puedas con técnica limpia. Paras cuando la velocidad de la barra cae claramente o la técnica se rompe.
> 
> **Cómo identificar el final del AMRAP:** la última rep válida es aquella donde tocas el pecho controlado y subes sin que la barra se quede atascada o "muera" a mitad de camino. Si la rep siguiente la harías con curvatura visible de la barra o desviación lateral, esa rep no cuenta y has terminado.
> 
> **Qué anotar:** peso × reps del AMRAP + RPE percibido. Ejemplo: `65 × 10 RPE 9`.
> 
> **Qué significa el resultado:**
> 
> - 9 reps = en target. Sigues el plan tal cual la próxima semana.
> - 10-11 reps = +1/+2 sobre target. Zona ideal. Sigues plan.
> - 12+ reps = +3 sobre target. Tu 1RM real era mayor del estimado. Recalibra al alza.
> - 7-8 reps = -1/-2. Repites la semana sin avanzar.
> - 6 o menos = -3+. Baja 5 % los pesos y repites la semana.

### Ejemplo 2 · Símbolos en tablas

**Antes:**

> A1 · Press banca plano · 3+1* · RPE 7-9

**Después:**

> **A1 · Press banca plano** (ejercicio principal de la sesión)
> 
> **Notación "3+1*":**
> 
> - "3" = tres series con reps prescritas y peso fijo
> - "+1" = una serie adicional
> - "*" = el asterisco indica que esa serie adicional es **AMRAP** (As Many Reps As Possible = tantas reps como puedas)
> 
> Por tanto: 3 sets fijos + 1 set AMRAP = 4 sets totales en la barra.

### Ejemplo 3 · Símbolo de superserie

**Antes:**

> C1 ↻ Dominada lastrada · superserie con C2

**Después:**

> **C1 + C2 · Superserie de antagonistas**
> 
> **La flecha enroscada ↻** indica que C1 y C2 se hacen **en superserie**: alternados sin descanso entre ellos.
> 
> **Cómo se ejecuta una superserie:**
> 
> 1. Set 1 de C1 (dominada lastrada): haz tus reps prescritas.
> 2. **Sin descansar más de 15-20 segundos** (lo justo para llegar a la siguiente máquina), set 1 de C2 (face pulls): haz tus reps prescritas.
> 3. Solo AHORA descansas el tiempo indicado (90 s).
> 4. Set 2 de C1 → set 2 de C2 → descanso 90 s.
> 5. Set 3 de C1 → set 3 de C2 → descanso 90 s o pasa al siguiente ejercicio.
> 
> **Por qué se hace así:** Las dos máquinas trabajan músculos opuestos (tirón vs retracción escapular). Mientras uno trabaja, el otro descansa. Ahorras tiempo total sin perder estímulo.
> 
> **Si una de las dos máquinas está ocupada:** ver §[X] sobre rotura de superseries.

### Ejemplo 4 · Concepto RPE

**Antes:**

> RPE 9 = 1 rep en reserva

**Después:**

> **RPE 9 explicado físicamente** (no solo conceptualmente):
> 
> La definición técnica es "podías haber hecho 1 rep más, pero no más de una". En la práctica, lo identificas así durante la serie:
> 
> - **Velocidad de la barra:** las primeras reps salen rápidas y suaves. En las últimas 2 reps la velocidad cae claramente. La rep final apenas sube — termina pero "se atasca" cerca del pecho o el lockout.
> - **Sensación muscular:** al acabar el set, sientes que podrías hacer 1 rep más con esfuerzo extremo y técnica posiblemente comprometida. La idea de hacer 2 más te parece imposible.
> - **Respiración:** vienes respirando entrecortado tras el último rep, no hablando.
> - **Test mental post-set:** si después de terminar piensas "podía haber sacado 2-3 más fácil" → fue RPE 7-8, no 9. Si piensas "imposible una más" → fue RPE 10, no 9.
> 
> **Diferencia con RPE 8:** RPE 8 = 2 reps en reserva. La velocidad de la barra cae solo en la última rep, no en las dos últimas. Acabas con la sensación clara de poder haber hecho 2 más con técnica intacta.
> 
> **Diferencia con RPE 10:** RPE 10 = al fallo absoluto. La última rep apenas la has terminado, posiblemente con asistencia mínima del compañero o con balanceo. Si has fallado una rep, eso es RPE 10+, no RPE 9. Solo en día de test.

## Cosas que TIENEN que estar explicadas

Lista mínima no exhaustiva de detalles que el manual nuevo debe contener (ningún manual previo los tiene):

### Sobre cargas y pesos

- Cómo calcular el peso de cada warm-up set (% del trabajo)
- Cuándo redondear arriba vs abajo
- Si el gym no tiene discos de 1,25 kg, qué hacer
- Cómo aplicar la fórmula Epley paso a paso con un ejemplo numérico
- Cómo aplicar el multiplicador 0,94 si el 1RM bench salió 80 kg en lugar de 85
- Cómo aplicar el × 1,2 para Smith squat si Diego pasa a Plan B
- Qué peso elegir si el cálculo da un número raro (ej. 67,3 kg)

### Sobre técnica de cada lift principal

- **Bench**: posición de los pies, ángulo de los codos respecto al torso, arco lumbar permitido, agarre (anchura), bracing pre-rep, leg drive, sticking point típico (pecho y lockout), señales de mala forma a evitar
- **Sentadilla**: anchura de pies, ángulo de puntera, profundidad mínima válida, posición de la barra (high bar vs low bar), tracking de rodillas, bracing valsalva
- **Hip Thrust**: setup en banco (altura del banco respecto a escápula), posición de los pies (cerca/lejos), apoyo de la cabeza, contracción glúteo al tope, error común (extender lumbar en lugar de cadera)
- **Prensa**: posición de pies (altos/medios/bajos) y qué músculo enfatiza cada una, profundidad de bajada segura sin sacar lumbar del respaldo, error común (apoyar manos sobre rodillas para "ayudar")

### Sobre cada sesión completa

- Qué llevar al gym (botella, toalla, móvil, calzado plano para sentadilla)
- Qué comer 2 horas antes, 1 hora antes, justo antes
- Cuándo tomar la cafeína (60 min pre-sesión, no antes)
- Cómo gestionar el tiempo si el gym está saturado (qué ejercicios se pueden saltar/intercambiar y cuáles no)
- Cómo abrir Telegram pre-sesión y dejar la cabecera lista para rellenar
- Qué hacer en los 5 minutos previos al primer set (mental rehearsal, activación, no scroll de redes)

### Sobre el día después y la recuperación

- Cómo distinguir agujetas normales vs dolor articular vs sobrecarga
- Qué hacer si el martes te despiertas más cansado de lo esperado
- Si las agujetas del miércoles siguen al viernes, qué significa
- Pasos diarios objetivo entre sesiones
- Cómo medir si el sueño fue suficiente (no es solo horas, es continuidad)

### Sobre escenarios completos

- Una semana de viaje: qué hacer
- Una semana enferma (ej. gastroenteritis): qué hacer
- Una semana de mucho estrés laboral: qué hacer
- Una semana que coincide con eventos sociales (cumpleaños, bodas): qué hacer
- Una semana con dolor lumbar leve nuevo: qué hacer

# CORRECCIONES OBLIGATORIAS DEL ADDENDUM

Estas 4 correcciones del addendum deben aplicarse SIN EXCEPCIÓN a todo el manual nuevo, sustituyendo cualquier información contradictoria del v4 original:

**Corrección 1 · Fechas del test final**

- Test bench: **lunes 7 sept 2026** (no 14 sept como dice el hero del v4)
- Test sentadilla: **viernes 11 sept 2026**
- Sem 17 (deload post-test): 14-20 sept 2026

**Corrección 2 · Pesos asumen recalibración**

- Los pesos de sem 1-4 se calculan sobre el 1RM de sem 0
- Los pesos de sem 6-9 se calculan sobre el 1RM nuevo tras AMRAP de sem 4
- Los pesos de sem 11-16 se calculan sobre el 1RM nuevo tras AMRAP de sem 9
- Sem 4 y sem 9 SIEMPRE se recalibra (marcan transición de bloque), aunque el AMRAP esté solo en target
- Esto debe estar explicado en la introducción a las tablas y reforzado en cada bloque

**Corrección 3 · Hip Thrust empieza en 60 kg**

- Sem 0 (test) = 3×10 @ 60 kg RPE 6
- Progresión re-entry: 60 → 70 → 80 → 90 → 100 kg en sem 0-4
- Cualquier mención de "partida re-entry 80 kg" del v4 es errónea, son 60 kg

**Corrección 4 · Regla del test fallido**

- Si el intento 1 del test (87,5 kg) falla, el PR previo (85 kg) sigue siendo el récord
- NO se acepta el último warm-up como PR del día
- Se reintenta el test en 2-3 semanas tras mini-bloque de acumulación adicional
- La regla del v4 ("aceptas el último warm-up como PR del día y paras") es incorrecta y debe corregirse

# ESTRUCTURA REQUERIDA DEL HTML NUEVO

Estructura mínima obligatoria (puedes añadir secciones, no quitar). Orden sugerido pero flexible si encuentras mejor orden:

```
0 · PORTADA Y CABECERA MENTAL
   · 4 PRs reales + 4 targets honestos
   · Hora hardcoded
   · Fechas test final (corregidas)
   · Resumen del macrociclo en 4 líneas

1 · CÓMO LEER ESTE MANUAL
   · Glosario completo de las 20 siglas (del addendum)
   · Convenciones de notación (3×5, @, +, *, ↻, RPE, etc.)
   · Cómo abrir el manual en sesión (móvil vs impreso)

2 · ANTES DE EMPEZAR · PRE-MACRO
   · Test diagnóstico sem 0 detallado paso a paso
   · Cómo calcular escalones del test del bench
   · Cómo identificar RPE 9 durante el test
   · Cómo aplicar Epley con ejemplos numéricos
   · Decisión del Plan A/B/C para sentadilla

3 · PRINCIPIOS QUE GUÍAN ESTE PLAN (para entender el porqué)
   · Frecuencia > volumen
   · DUP intra-semanal
   · AMRAP como autorregulación
   · Hora hardcoded
   · Deload agresivo cada 5 sem

4 · TU SEMANA · ESTRUCTURA Y RUTINA
   · Calendario tipo (LUN/MIÉ/VIE + recuperación)
   · Qué comes, cuándo, cuánto (día gym vs descanso)
   · Sueño · qué hacer para maximizar 6 h
   · Cafeína · timing exacto

5 · LUNES · UPPER HEAVY (sesión completa, ejercicio a ejercicio, con explicaciones detalladas de cada uno)
   · Warm-up paso a paso con tiempos
   · Press banca · técnica + ejecución + setup
   · Remo barra Pendlay · técnica + ejecución + setup
   · Cada accesorio explicado
   · Qué hacer si X máquina está ocupada
   · Cómo cerrar la sesión

6 · MIÉRCOLES · LOWER COMPLETE
   · Igual estructura
   · Árbol Plan A/B/C explicado en detalle
   · Cómo decidirlo en el calentamiento prehab

7 · VIERNES · UPPER VOLUME + PAUSE
   · Igual estructura
   · Bench con pausa · cómo cuento los 2 segundos exactamente

8 · LAS TABLAS DE PESOS · SEMANA A SEMANA
   · Bench (con DOS columnas: si 1RM = 80 vs si 1RM = 85)
   · Sentadilla (Plan A vs Plan B vs Plan C)
   · Hip Thrust (con re-entry sem 1-3 destacado)
   · Prensa
   · Sub-sección: cómo recalibrar tras sem 4 y sem 9 (Epley paso a paso)

9 · AUTOREGULACIÓN COMPLETA
   · Escala RPE explicada físicamente (no solo conceptualmente)
   · Árbol AMRAP con ejemplos numéricos
   · Deuda de sueño (1 noche / 2-3 noches / 4+ noches)
   · Señales para deload extra
   · Qué hacer si te saltas sesiones

10 · LOS HITOS DEL MACRO
   · Hito 1 (sem 4) detallado
   · Hito 2 (sem 8) detallado
   · Hito 3 (sem 12) detallado
   · Hito 4 (sem 16) detallado
   · Cómo celebrar cada uno (importante para adherencia)

11 · DÍA DEL TEST · PROTOCOLO EXACTO
   · Pre-test 24 h
   · Mañana del test (alimentación, cafeína)
   · Pasos exactos en el gym (minuto a minuto)
   · Qué hacer si intento 1 falla (regla corregida)
   · Qué hacer si pasas los 3 intentos

12 · TROUBLESHOOTING · 20 ESCENARIOS COMUNES
   · Cada uno con respuesta concreta
   · Incluir todos los del v4 + mínimo 10 nuevos
   · Cubrir: viaje, enfermedad, lesión leve, lesión moderada, estrés laboral, eventos sociales, máquinas ocupadas, gym cerrado, vacaciones, períodos sin sueño

13 · CABECERA TELEGRAM Y NOTACIÓN
   · Plantilla copy-paste para cada día
   · Cómo anotar series, pesos, RPE
   · Notación mancuernas (peso/lado)
   · Métricas a revisar cada 4 semanas

14 · NUTRICIÓN OPERATIVA
   · Cálculo personalizado de mantenimiento
   · Superávit recomendado
   · Distribución de proteína paso a paso
   · Día gym vs día descanso
   · Suplementación esencial
   · Pre/durante/post entreno

15 · POST-TEST · HOJA DE RUTA 12 MESES
   · Sem 17 deload completo
   · Macrociclo 2 (oct 26 → ene 27)
   · Macrociclo 3 (ene → may 27)
   · Targets honestos a 12 meses

16 · APÉNDICES
   · Glosario completo (ya incluido al inicio)
   · Resumen ejecutivo para imprimir
   · Cheat sheet de 1 página para llevar al gym
```

# ESTILO VISUAL EDITORIAL

Mantén la continuidad visual con los 3 HTMLs existentes:

**Tipografía:**

- Display: Fraunces (Google Fonts, opsz variable)
- Cuerpo: Newsreader (Google Fonts, opsz variable)
- Datos/mono: JetBrains Mono

**Paleta:**

- Paper: #F5EFE3 (fondo crema)
- Ink: #1F1B16 (texto principal)
- Copper: #B4632F (acentos cálidos, links)
- Moss: #3F5A36 (positivo, verde editorial)
- Wine: #7A2E2B (crítico, alertas)
- Ochre: #C49A3B (deload, neutro)
- Paper-warm: #EFE5D2 (fondos de finding, callout)

**Componentes (mantén consistencia con los HTMLs existentes):**

- `.day-card` con `.day-head` oscuro y `.day-body` claro
- `.finding` (border-left copper/wine/moss/ochre según gravedad)
- `.callout` (fondo oscuro, ochre accent)
- `.delta` (fondo paper-warm, border wine)
- `table.editorial` (encabezados mono uppercase, filas con hover)
- `table.ex-table` (sin thead visible, código mono copper, supersets sombreados)
- `table.weeks` (filas deload sombreadas ochre, filas test sombreadas moss)
- Sticky topnav con nav mono uppercase
- Print stylesheet (@media print) para imprimir sin grano ni topnav

**Responsive:**

- Mobile-first: el documento se va a abrir en móvil en el gym
- Breakpoint clave: 720 px
- Tablas con `.table-wrap` para overflow-x scroll
- Sticky nav adaptable

# CRITERIOS DE CALIDAD

El manual está bien hecho cuando cumple estos tests:

1. **Test del ejecutor sin contexto:** alguien que NUNCA haya visto los 3 HTMLs previos puede abrir el manual nuevo, leerlo y ejecutar las 17 semanas sin preguntas.
    
2. **Test del gym a las 20:25:** Diego abre el manual en el móvil mientras espera el rack del bench. En menos de 90 segundos sabe (a) qué semana es, (b) qué peso poner, (c) cuántas series, (d) qué AMRAP target, (e) qué hacer si falla.
    
3. **Test de la pregunta operativa:** cualquier pregunta del tipo "¿con qué peso empiezo X?", "¿qué significa X símbolo?", "¿cómo sé si X?" tiene respuesta directa en el manual sin tener que interpretar.
    
4. **Test de la sesión interrumpida:** si una máquina está ocupada, una bombilla se funde, alguien se acerca a preguntar algo o cualquier interrupción ocurre, Diego puede retomar exactamente donde lo dejó sin perder el hilo.
    
5. **Test del veterano + del novato:** un coach experimentado lo lee y no encuentra errores programáticos ni cambios al plan v4. Un principiante lo lee y entiende cada paso sin tener que buscar nada en Google.
    

# NO HACER

- **No cambiar el plan v4.** Mismas tablas, misma estructura, mismos ejercicios, mismos targets. Solo expandir explicaciones.
- **No introducir nuevos ejercicios** que no estén en el v4.
- **No añadir nuevas reglas programáticas.** Si una regla no está en el v4 + addendum, no la inventes.
- **No omitir nada del v4.** Toda información del v4 debe estar presente en el manual nuevo, igual o más detallada.
- **No quitar el rigor técnico.** "Para tontos" significa explicado paso a paso, no infantilizado. Diego lleva 3 años entrenando.
- **No suavizar advertencias.** Si una regla es "no negociable", mantén ese tono.
- **No truncar.** Si el HTML acaba siendo de 4000-7000 líneas, perfecto. La expansión es el deliverable.
- **No usar emojis ni iconos.** El estilo editorial es serio, tipográfico, sobrio. Como los 3 HTMLs previos.
- **No partir el output en múltiples archivos.** UN solo HTML autosuficiente.
- **No incluir referencias circulares** ("ver §X" → §X dice "ver §Y" → §Y dice "ver §X"). Cada sección debe ser autocontenida o referenciar adelante una sola vez.

# ENTREGA

Estructura tu trabajo así:

1. **Análisis previo silencioso (ultrathink):** dedica reasoning extendido a planificar la arquitectura, identificar gaps, decidir qué expandir más. No escribas HTML hasta tener clara la estructura completa.
    
2. **Confirmación de comprensión:** antes de escribir el HTML, responde brevemente (1-2 párrafos) confirmando que has entendido el encargo y describiendo en alto nivel cómo vas a estructurar el documento. NO presentes una propuesta detallada — solo verificación rápida de comprensión.
    
3. **Generación del HTML completo:** un solo archivo, autosuficiente, descargable. Sin truncamiento. Si por límite técnico tienes que partir, indica claramente al final "PARTE 1 DE N" y continúa en la siguiente respuesta.
    
4. **Presenta el archivo al final:** asegúrate de que el archivo está en `/mnt/user-data/outputs/` para que el usuario pueda descargarlo.
    
5. **Nota final breve:** resume en 3-5 líneas qué incluye el manual y cómo se diferencia de los 3 HTMLs previos. Sin cebar futuras iteraciones — este es el manual final.
    

---

# RECORDATORIO FINAL

Este es el quinto y último documento de un proceso que empezó con un análisis de 33 meses de bitácora, pasó por un informe quirúrgico de 25 secciones, evolucionó por 4 versiones del plan, y se complementó con un addendum de QA. El manual que vas a producir es la versión que Diego usará durante 17 semanas para ejecutar el plan v4 sin tener que consultar ninguna otra cosa.

La calidad importa más que la velocidad. La completitud importa más que la elegancia. La claridad importa más que la concisión.

Empieza con ultrathink.
````
