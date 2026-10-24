# Caducidad de certificados TLS

## Síntomas

- Alerta `CertificateExpiresSoon` (menos de 14 días) o errores de handshake TLS en los clientes.

## Diagnóstico

1. Identifica el certificado: dominio, emisor y fecha de caducidad.
2. Comprueba si la renovación automática (cert-manager) está configurada para ese certificado y por qué falló.

## Mitigación

- Renueva el certificado mediante cert-manager forzando la renovación del recurso Certificate.
- Si la renovación automática falla por el challenge ACME, revisa el DNS y la ingress class.
- Nunca subas claves privadas a repositorios ni a tickets.

## Escalado

Equipo de plataforma. SEV2 si caduca un certificado de un endpoint público tier 0.
