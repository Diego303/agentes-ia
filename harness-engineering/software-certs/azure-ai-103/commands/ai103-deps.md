---
description: Dado un slug, muestra (1) archivos que referencian ESTE (in-degree) y (2) archivos que ESTE referencia (out-degree). Útil para entender dependencias antes de editar o estudiar.
allowed-tools: Read, Bash, Glob, Grep
---

# /ai103-deps — Dependencies de un archivo

## Argumento

- **$ARGUMENTS** = slug obligatorio (sin .md).

## Pasos

1. Verificar que `<slug>.md` existe en el vault (`Glob`).
2. **In-degree** (¿quién me referencia?): `grep -rl "\[\[<slug>\]\]" --include="*.md" .`
3. **Out-degree** (¿a quién referencio yo?): extraer wikilinks del archivo `<slug>.md` con `grep -oE "\[\[[a-zA-Z0-9_.-]+(\|[^]]+)?\]\]"`.
4. Mostrar al usuario:

```
🔗 Dependencias de [[<slug>]]

📥 Referenciado por (in-degree: N):
  - [[archivo1]] (carpeta X)
  - [[archivo2]] (carpeta Y)
  - ...

📤 Referencia a (out-degree: N):
  - [[archivoA]]  ✅ existe
  - [[archivoB]]  ✅ existe
  - [[archivoC]]  ⚠️ aún no creado (en INDICE como ⬜)

💡 Interpretación:
  - In-degree alto: este archivo es foundational. Cuidado al cambiarlo.
  - Out-degree alto: este archivo es agregador / overview. Léelo después de sus deps.
```

## Reglas

- Solo análisis local.
- Output al usuario directo, sin escribir archivo.
- Si in-degree = 0 → marca como posible "orphan" y sugiere /ai103-validate.

$ARGUMENTS
