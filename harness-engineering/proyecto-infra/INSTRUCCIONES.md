# INSTRUCCIONES — proyecto-infra

> **Perfil**: `infra-only` — IaC pura (Terraform / Pulumi / k8s manifests
> / CloudFormation). **18 agentes**: 8 orquestación + 5 infra + 5 docs +
> 1 cross-cutting (security-auditor). **Con GATE#3 → Applier
> pre-apply.** **27 archivos.**

Este proyecto es el **único con GATE#3**, el gate humano antes de
operaciones irreversibles (`terraform apply`, `kubectl apply`,
`pulumi up`). Está diseñado para evitar que tu asistente IA aplique
cambios en producción sin tu aprobación explícita.

Es ideal para:
- **Proyectos IaC** (Terraform, Pulumi, k8s manifests, CloudFormation,
  Ansible).
- **Repos de infra compartidos** entre múltiples equipos (donde el
  cost-estimator y el drift-detector aportan valor).
- **Equipos que ya tuvieron incidentes con apply mal hecho** (o que
  quieren prevenirlos).

---

## Arranque (1 sola vez)

```bash
cd EJEMPLOS-BASE/proyecto-infra
./init.sh                      # git init + commit inicial
harness doctor                 # → 20 ok 0 warning(s) 0 error(s)
harness status                 # muestra DEMO-INFRA-001 con next: Explorer
```

Footer del status: `infra (with GATE#3 → Applier) flow`. Esto confirma
que el flujo extendido está activo.

---

## Flujo SDD específico de infra

A diferencia de los demás perfiles, infra-only tiene:

1. **Pre-flow obligatorio**: drift-detector corre **antes** de Explorer.
2. **Sub-agente del Designer**: iac-designer anexa "## IaC design" a
   design.md.
3. **Post-Verifier**: terraform-planner ejecuta `terraform plan` y
   produce `terraform-plan.md` con clasificación de cambios
   (add/update/replace/destroy).
4. **Cost-estimator**: anexa info informativa, no bloquea.
5. **GATE#3** (humano): aprueba el plan antes de aplicar.
6. **Applier**: el único agente con permiso para hacer cambios reales.

```
[drift-detector] → Explorer → Proposer → [GATE#1] → (Spec ‖ Designer + iac-designer)
                → Task-planner → Implementer → [GATE#2 + security-auditor + doc-reviewer]
                → Verifier → terraform-planner → cost-estimator → [GATE#3] → Applier → Archiver
```

---

## Cómo trabajar con Claude Code

### Setup

```bash
cd EJEMPLOS-BASE/proyecto-infra
claude
```

Antes de empezar, asegúrate de:

1. **Tener configurado tu cloud provider**: AWS CLI, GCP gcloud, Azure
   az, etc. con credenciales válidas.
2. **Tener Terraform instalado** (o Pulumi, kubectl, según tu stack).
3. **Tener `infracost` instalado** (opcional pero recomendado para
   cost-estimator).

### Trabajar la primera feature (DEMO-INFRA-001)

`DEMO-INFRA-001` es "VPC base con subredes públicas y privadas" — un
ejemplo realista que ejercita todo el flujo.

#### Fase 0 — Drift detector (PRE-flow obligatorio)

Antes de cualquier otra cosa:

```
Actúa como Drift Detector
(.claude/agents/infra/drift-detector.md). La feature es DEMO-INFRA-001
que tocará el módulo de networking. Ejecuta `terraform plan
-refresh-only` en el módulo (o equivalente para tu stack) y produce
progress/DEMO-INFRA-001/drift-report.md.
```

**Si el drift report es `crítico`**, **NO sigas** hasta reconciliar
manualmente.

#### Fase 1 — Explorer

```
Actúa como Explorer. Lee progress/DEMO-INFRA-001/drift-report.md y
mapea el repo. Produce exploration.md.
```

#### Fase 2 — Proposer → GATE#1

```
Actúa como Proposer. Produce proposal.md con: propuesta principal,
≥2 alternativas (ej. NAT Gateway vs NAT instance vs sin NAT con VPC
endpoints), trade-offs (coste, latencia, single-AZ failure),
preguntas abiertas (¿cuántas AZ? ¿IPv6?).
```

GATE#1: tú apruebas leyendo `proposal.md`.

#### Fase 3 — Spec-writer ‖ Designer + IaC Designer

```
Actúa como Spec-writer. Produce spec.md con criterios de aceptación
verificables (CIDR ranges, número de subredes, tags requeridas,
política de routing).
```

```
Actúa como Designer. Produce design.md con "## Architecture (Designer)".
```

```
Actúa como IaC Designer (.claude/agents/infra/iac-designer.md). Anexa
"## IaC design" a design.md con: grafo de módulos, state backend,
secrets, blast radius, rollback plan.
```

**Importante**: si el blast radius del IaC Designer es "alto" y ya
tienes `gate3_pre_apply` en este perfil, todo OK. Si fuera otro perfil
sin GATE#3, IaC Designer marcaría una pregunta abierta.

#### Fase 4 — Task-planner → Implementer

```
Actúa como Task-planner. Produce task-plan.md con tareas tipo:
- [1] crear módulo terraform/network/main.tf con vpc + subnets
- [2] añadir variables.tf con cidr_block, az_count, tags
- [3] añadir outputs.tf con vpc_id, subnet_ids
- [4] terraform fmt + validate
```

```
Actúa como Implementer. Sigue task-plan.md tarea a tarea. Para cada
tarea, ejecuta `terraform fmt` y `terraform validate`. Recuerda:
implementation.md es OBLIGATORIO.
```

#### Fase 5 — GATE#2 + revisores paralelos

En infra-only corren **2 revisores en paralelo**:

```
Actúa como Security Auditor. Audita el diff IaC. Detecta:
- IAM policies demasiado amplias (`*` en Action o Resource)
- Security groups con 0.0.0.0/0 en puertos no-HTTP
- S3 buckets sin encriptación
- Secrets hard-coded
Produce security-audit.md con veredicto.
```

```
Actúa como Doc Reviewer. Revisa los docs producidos por
technical-writer (si los hay). Produce doc-review.md.
```

GATE#2: tú revisas `git diff` + ambos reviews.

#### Fase 6 — Verifier

```
Actúa como Verifier. Ejecuta el verify_stack de infra-only:
- tflint
- terraform validate
- tfsec
- markdownlint

Produce verification.md.
```

#### Fase 7 — Terraform Planner (PRE-GATE#3)

```
Actúa como Terraform Planner (.claude/agents/infra/terraform-planner.md).
Ejecuta `terraform plan` en cada módulo afectado. Captura el output.
Para cada recurso clasifica: add / update / replace / destroy.
Marca como "alto riesgo": replaces de recursos con datos, destroys
críticos, cambios IAM/networking de prod.
Produce terraform-plan.md con veredicto ok-to-apply / block.
```

#### Fase 8 — Cost Estimator

```
Actúa como Cost Estimator. Lee terraform-plan.md y ejecuta
`infracost breakdown --path .` (o estima manualmente con tablas de
pricing). Produce cost-estimate.md con tabla recurso → coste mensual.
Si delta > $100/mes (default), marca over-threshold.
```

#### Fase 9 — GATE#3 (humano, **crítico**)

**Aquí paras de verdad**. Lee:
- `terraform-plan.md` recurso por recurso.
- `cost-estimate.md`.
- Plan de rollback en `design.md::IaC design`.

Si apruebas:

```bash
echo "Aprobado por <tu-nombre> $(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  > progress/DEMO-INFRA-001/gate3-approved.md
```

**Sin este archivo, Applier rechaza ejecutar.**

#### Fase 10 — Applier

```
Actúa como Applier (.claude/agents/infra/applier.md). Verifica:
1. progress/DEMO-INFRA-001/gate3-approved.md existe y timestamp < 24h.
2. terraform plan actual coincide con terraform-plan.md (no stale).
3. Aprobación humana presente.

Si todo OK, ejecuta `terraform apply` con el plan binario guardado.
Captura stdout/stderr/exit code.
Si apply falla a media ejecución, registra estado parcial y PARA.

Produce apply.md.
```

#### Fase 11 — Archiver

```
Actúa como Archiver. Cierra el ciclo: archive.md (## Summary) +
update feature_list.json::status a archived.
```

---

## Cómo trabajar con Codex

```bash
cd EJEMPLOS-BASE/proyecto-infra
codex
```

**ATENCIÓN**: Codex no respeta los hooks de `.claude/settings.json`.
Si quieres validación automática antes de cada `terraform apply` (para
forzar GATE#3 incluso si el agente "olvida"), usa `git hooks` o un
wrapper:

```bash
# .git/hooks/pre-commit
#!/bin/bash
# Si el commit toca .tf/.yaml de IaC, exige gate3-approved.md actualizado
if git diff --cached --name-only | grep -qE '\.(tf|tfvars)$'; then
  if ! ls progress/*/gate3-approved.md 2>/dev/null; then
    echo "Error: no gate3-approved.md found. Run GATE#3 before applying."
    exit 1
  fi
fi
```

El flujo con Codex es secuencial. Cada agente del flujo lo invocas con
prompt directo. Para los reviewers paralelos en GATE#2, abre 2
terminales con `codex`, una para cada uno.

---

## Cómo trabajar con Cursor

Cursor es buen ambiente para IaC porque:
- Tiene buen autocompletado de Terraform.
- Composer puede ver múltiples `.tf` a la vez.

Setup:

```bash
mkdir -p .cursor/rules
cat > .cursor/rules/iac-safety.md <<'EOF'
# IaC Safety

NUNCA ejecutes `terraform apply` o `pulumi up` automáticamente.
NUNCA modifiques recursos en cloud sin pasar por:
1. terraform-planner produce plan.
2. cost-estimator estima coste.
3. GATE#3 humano aprueba (archivo gate3-approved.md).
4. Applier ejecuta.

Si el usuario pide aplicar cambios, recuérdale el flujo SDD del harness
y pídele aprobar GATE#3 explícitamente antes.
EOF
```

---

## Cómo trabajar con GPT-4 / Claude.ai (chat web)

Para IaC vía chat web es **especialmente importante** controlar el
flujo manualmente, porque el chat web no puede ejecutar `terraform`
directamente.

Workflow típico:

1. Tú ejecutas `terraform plan` localmente.
2. Pegas el output en el chat junto con el MD del Terraform Planner.
3. Pides al chat actuar como Terraform Planner y producir el análisis.
4. Lees su veredicto.
5. Si `ok-to-apply`, tú apruebas GATE#3 y tú ejecutas `terraform apply`.
6. Pegas el output del apply al chat para que actúe como Archiver.

---

## Cómo modificar este proyecto

### Adaptar a Pulumi en lugar de Terraform

Edita los MDs de los agentes infra para reemplazar comandos:

```bash
# En .claude/agents/infra/terraform-planner.md, busca y reemplaza:
sed -i 's/terraform plan/pulumi preview/g' .claude/agents/infra/terraform-planner.md
sed -i 's/terraform apply/pulumi up/g' .claude/agents/infra/applier.md
```

O renombra los agentes:

```bash
mv .claude/agents/infra/terraform-planner.md .claude/agents/infra/pulumi-previewer.md
```

(Y edita el contenido para que mencione Pulumi.)

### Adaptar a kubectl / Kustomize / Helm

```bash
# Cambia las herramientas en cada MD de infra:
# - terraform-planner → kubectl-diff
# - terraform-validate → kubeconform / kustomize build
# - tfsec → checkov / kubesec / polaris
```

Y edita `USAGE.md` o el verify_stack si hace falta.

### Añadir un agente "Drift Reconciler"

Cuando drift-detector reporta crítico, alguien tiene que reconciliar.
Añade un agente:

```bash
cat > .claude/agents/infra/drift-reconciler.md <<'EOF'
# Agent: Drift Reconciler (infra)

## Rol
Reconcilia drift detectado por drift-detector. NO modifica infra real
— sólo propone los cambios al .tf que reflejen el estado actual.

## Inputs esperados
- progress/<id>/drift-report.md con drift crítico.
- Acceso al state backend y al código IaC.

## Procedimiento
1. Para cada drift crítico, decide la estrategia: aceptar como nuevo
   baseline (actualizar .tf) o revertir (apply el .tf actual).
2. Si aceptas como baseline: actualiza el .tf para coincidir con el
   estado real.
3. Si revertir: documenta los cambios necesarios para que el siguiente
   apply los descarte.
4. Anexa "## Reconciliation plan" a drift-report.md.

## Output
- drift-report.md con sección de reconciliación.

**Siguiente paso**: humano revisa y aprueba el plan; luego flujo SDD
normal puede empezar.

**Cuándo parar y pedir ayuda**:
- Drift afecta a recursos con datos (DB, bucket): para; reconciliar
  sin pérdida de datos requiere humano.
- Drift causado por incidente de seguridad: escala a security
  inmediatamente.

## Anti-patterns
- ❌ Hacer apply del plan reconciliador sin GATE#3.
- ❌ Borrar el state file "para empezar limpio".
EOF
```

Luego documenta en `AGENTS.md` cómo encaja (entre drift-detector y
Explorer).

### Configurar Applier para usar workspace

Si tu repo usa Terraform workspaces:

```bash
# Edita .claude/agents/infra/applier.md y añade en Procedimiento:
# 1.5. Verifica workspace activo: `terraform workspace show`. Si no es
#      el esperado para esta feature, para.
```

### Hook para forzar GATE#3 en `.claude/settings.json`

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE \"terraform apply|pulumi up|kubectl apply -f\"; then if ! ls progress/*/gate3-approved.md 2>/dev/null | head -1 | xargs -I{} sh -c \"test \\$((($(date +%s) - $(stat -c %Y {})) / 3600)) -lt 24\"; then echo \"GATE#3 not approved or stale (>24h). Aborting.\"; exit 2; fi; fi'"
          }
        ]
      }
    ]
  }
}
```

(Hook complejo pero efectivo: bloquea cualquier `terraform apply` sin
gate3 aprobado o con gate3 viejo de >24h.)

---

## Primera feature recomendada

`DEMO-INFRA-001` ("VPC base") es excelente para tu primer ciclo
porque:

- **Ejercita los 5 agentes infra**: drift-detector + iac-designer +
  terraform-planner + cost-estimator + applier.
- **Tiene blast radius medio** (toca networking pero es módulo nuevo,
  no edita recursos existentes).
- **Tag `security-critical`** activa security-auditor en modo más
  estricto.
- **Coste estimable**: 2 NAT Gateways ≈ $80/mes, dispara cost-estimator
  con números reales.

Tras completarla:
- La VPC está real en tu cloud.
- Tienes archivos `.tf` en el repo.
- `progress/DEMO-INFRA-001/` es tu historial completo de la decisión.

---

## Troubleshooting específico de infra

### "terraform plan dice 'no changes' pero drift-detector dice crítico"

`terraform plan` (sin `-refresh-only`) no detecta drift en config no
controlada por TF (p. ej. tags añadidas en consola).
`-refresh-only` sí. Verifica que drift-detector está usando el flag
correcto.

### "Applier se ejecutó pero terraform apply falló a media ejecución"

Sigue el procedimiento del MD: documenta el estado parcial,
**no** intentes "recuperar" automáticamente. El humano decide rollback
o forward-fix.

```bash
# Estado partial: revisa qué se aplicó
terraform state list

# Si quieres rollback:
git checkout <commit-anterior>
terraform apply  # vuelve al estado anterior
```

### "cost-estimator dice $0/mes pero sé que el cambio cuesta"

Probablemente `infracost` no está instalado o no tiene tablas de
pricing actualizadas. Verifica:

```bash
infracost --version
infracost configure get currency
```

Si no usas infracost, edita el MD del agente para que use otra fuente
(AWS Pricing API, manual lookup, etc.) y márquelo claramente.

### "GATE#3 stale (>24h)"

Por seguridad, el agente Applier rechaza aprobaciones con timestamp
>24h. Si tarrdaste mucho desde aprobar:

```bash
# Re-ejecuta terraform-planner para confirmar que el plan no cambió
terraform plan -out=tfplan.binary
diff <(terraform show -json tfplan.binary) <(terraform show -json terraform-plan.binary.old)

# Si idéntico, re-aprueba GATE#3
echo "Re-aprobado tras verificación $(date -u)" >> progress/<id>/gate3-approved.md
```

### "drift-detector reporta drift crítico pero no estoy listo para resolver"

Para el flujo. Documenta en `progress/<id>/blockers.md`:

```markdown
## Bloqueo: drift crítico no reconciliado

Detalle: ver drift-report.md.
Decisión: posponer feature DEMO-INFRA-001 hasta resolver drift.
Acción: crear feature INFRA-FIX-001 (status: proposed) para reconciliar.
```

---

## Próximos pasos

1. Lee [`../../docs/best-practices.md`](../../docs/best-practices.md)
   sección "Cuándo invocar drift-detector".
2. Configura los hooks de `.claude/settings.json` para forzar GATE#3
   automáticamente.
3. Si trabajas en multi-cloud, considera tener un proyecto
   por-cloud (no mezclar AWS + GCP en el mismo repo IaC).
