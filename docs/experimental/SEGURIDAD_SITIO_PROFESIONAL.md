# Seguridad de un sitio profesional: guía y checklist para TortuScript

> **Estado: EXPERIMENTAL — guía de referencia, no implementada.** Hoy TortuScript es una app **local** (`127.0.0.1`, sin cuentas,
> sin internet). Casi todo lo de este documento se vuelve obligatorio **si algún día se publica como servicio en línea**,
> sobre todo si lo usan menores. Continúa [VISION_PLATAFORMA.md](VISION_PLATAFORMA.md) y
> [ACADEMIA_DE_JUEGOS_E_INTERESES.md](ACADEMIA_DE_JUEGOS_E_INTERESES.md).

## 0. Idea principal: no mezclar SEO con seguridad

| Cosa | Para qué sirve | ¿Es seguridad? |
|---|---|---|
| `robots.txt` | indica a los rastreadores qué pedir | **No.** No impide el acceso directo a una URL; no sirve para ocultar información privada |
| `sitemap.xml` | dice a los buscadores qué URLs importantes existen | No (SEO) |
| `noindex` / autenticación | evitar que algo aparezca en buscadores / protegerlo de verdad | Autenticación sí; `noindex` no |
| `security.txt` | publica un contacto para que investigadores reporten vulnerabilidades | Comunicación de seguridad (distinto de `robots.txt`) |

## 1. Transporte
- HTTPS en todo el sitio, redirección HTTP → HTTPS, TLS moderno, certificado con renovación automática.
- HSTS (`Strict-Transport-Security`; `includeSubDomains` cuando la arquitectura lo permita).
- Sin contenido mixto; nada sensible (contraseñas, tokens) por HTTP.

## 2. Cookies y sesiones (cuando haya cuentas)
Cookie de sesión mínima: `Set-Cookie: __Host-session=…; Secure; HttpOnly; SameSite=Lax; Path=/`

| Atributo | Función |
|---|---|
| `Secure` | solo viaja por HTTPS |
| `HttpOnly` | JavaScript no puede leerla |
| `SameSite=Lax/Strict` | reduce ataques cross-site (CSRF) |
| `Path=/` y prefijo `__Host-` | restringen el alcance |

Además: expiración, invalidar al cerrar sesión, rotar el identificador tras autenticarse, protección contra *session fixation*,
no guardar contraseñas ni datos sensibles en cookies.

## 3. Contraseñas
Nunca en claro ni con un hash rápido (`SHA256(password)`). Usar **Argon2id, bcrypt o scrypt**. Más: política razonable,
*rate limiting*, tokens de recuperación **temporales y de un solo uso**, jamás enviar contraseñas por email ni registrarlas en logs.

## 4. Ataques web (núcleo)
- **XSS:** escapar HTML, sanitizar solo cuando haga falta permitirlo, evitar `innerHTML`, usar CSP, no insertar datos de usuario directo en HTML/JS.
- **Inyección SQL:** consultas parametrizadas / ORM, nunca concatenar.
- **CSRF:** `SameSite`, tokens CSRF, validar `Origin`/`Referer`, no usar `GET` para acciones que modifican datos.
- **Clickjacking:** `Content-Security-Policy: frame-ancestors 'self'` (o `X-Frame-Options`).

## 5. Headers de seguridad HTTP
Base: `Strict-Transport-Security`, `Content-Security-Policy`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`.
Según la arquitectura: `X-Frame-Options`, `Cross-Origin-Opener-Policy`, `Cross-Origin-Resource-Policy`.
No agregarlos "porque sí": configurarlos según cómo funciona la app. Ejemplo conceptual de CSP a adaptar:

```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:;
                         connect-src 'self'; frame-ancestors 'self'
```

## 6. Control de acceso (OWASP A01)
No alcanza con esconder un botón: el servidor comprueba **en cada operación** si *este* usuario puede acceder a *este* recurso
(`/users/123/projects` no debe abrirse cambiando la URL). Autenticación, autorización, roles, aislamiento entre usuarios **y
entre perfiles**, endpoints administrativos protegidos, comprobación de propiedad (*ownership*).

## 7. Rate limiting y bots
Límites en `/login`, `/register`, `/password-reset`, `/api/*`, `/feedback` (por IP y por cuenta, distintos por endpoint, sin bloquear
a usuarios legítimos detrás de NAT). CAPTCHA/Turnstile solo donde haya riesgo real, no en cada pantalla.

## 8. APIs y validación de entradas
Cada endpoint valida autenticación, autorización, formato, tamaño, tipo y estado de sesión. **Nunca** asumir que "solo la llama nuestra
interfaz": el navegador está bajo control del usuario. Todo dato es potencialmente malicioso: nombre, email, comentario,
nombre de proyecto, código, archivo, preferencias. Validar longitud, tipo, formato, *encoding*, valores permitidos y tamaño.

## 9. Subida de archivos (si algún día existe)
Límite de tamaño, tipos MIME y extensiones permitidos, **verificar el contenido real**, renombrar (no confiar en el nombre original),
no ejecutar lo subido, guardar fuera del directorio ejecutable, permisos restrictivos, escaneo de malware si corresponde.

## 10. Ejecución de código (lo más crítico en TortuScript)
Hoy: subproceso con límites (tiempo, y memoria en todos los sistemas), validación AST, builtins limitados, sin `import`, tope de pasos y de salida.
**Eso alcanza para el runtime educativo, no para un runtime de juegos con Pygame o `import` libre.** Un `import os` permitiría intentar
acceder al sistema. El futuro *Game Runtime* necesita aislamiento mucho más serio (contenedores/VM o equivalente, o ejecutar en el
navegador sin servidor), según el modelo de despliegue.

## 11. Dependencias y cadena de suministro (OWASP A03)
Fijar versiones, actualizar, revisar vulnerabilidades, eliminar las innecesarias, *lockfiles*, revisar cada paquete antes de agregarlo,
escaneo automatizado, no ejecutar código descargado de fuentes desconocidas.

## 12. Secretos
Nunca en el repositorio (`SECRET_KEY`, `API_KEY`, `JWT_SECRET`, contraseñas de base de datos, tokens). Variables de entorno o gestor de
secretos; `.env` fuera de Git; rotación; secretos distintos en desarrollo y producción; nada de secretos en logs.

## 13. Logs, auditoría y monitoreo (OWASP A09)
Registrar login exitoso/fallido, logout, cambios de contraseña/email/permisos, creación/borrado de proyectos, errores internos y actividad
administrativa, con timestamp, evento, identificador interno, IP si corresponde, resultado y *request ID*. **Sin** datos sensibles. Además:
alertas (muchos logins, picos de requests, ráfagas de 500, scraping, abuso de API, accesos no autorizados).

## 14. Backups, base de datos y errores
- **Backups** automáticos, cifrados, fuera del servidor, con retención y **restauraciones probadas**.
- **Base de datos:** credenciales separadas, privilegios mínimos, conexión cifrada, consultas parametrizadas, migraciones versionadas,
  restricciones e integridad referencial.
- **Errores:** en producción nunca mostrar trazas, rutas del servidor, secretos ni consultas; un "Error 500 — código de referencia 8F72A1"
  y el detalle en los logs.

## 15. CORS, CSRF y cookies (se diseñan juntos)
Cookies = sesión; CSRF = evitar acciones cross-site no autorizadas; CORS = qué orígenes pueden hacer solicitudes cross-origin.
Con frontend y API separados, listar orígenes explícitos; **no** usar `Access-Control-Allow-Origin: *` en endpoints autenticados.

## 16. Dominio, DNS y email
HTTPS, DNS bien configurado, sin subdominios abandonados, registrador protegido con MFA y bloqueo de transferencia. Si se envía email:
**SPF, DKIM y DMARC**, tokens con expiración, enlaces HTTPS, sin contraseñas ni datos sensibles.

## 17. Privacidad y menores
Definir qué datos se recopilan, para qué, por cuánto tiempo, quién accede, cómo se eliminan y se exportan, con una política clara.
Para menores hay que diseñar el tratamiento de datos y revisar las obligaciones legales de cada país **desde el principio, no al final**.
**Terceros y analítica:** separar cookies necesarias, analítica, publicidad y preferencias; minimizar scripts de terceros (cada uno suma
dependencia, superficie de ataque, impacto de privacidad y problemas de CSP).

## 18. Servidor, repositorio y CI/CD
- **Servidor:** sistema actualizado, firewall, puertos mínimos, SSH con claves y sin root, MFA administrativo, permisos mínimos, servicios separados, monitoreo.
- **Repositorio:** `.gitignore` con `.env`, `*.pem`, `*.key`, `secrets/`, volcados de base de datos; ramas protegidas, PR y revisión, *secret scanning*, *dependency scanning*.
- **CI/CD:** tests → lint → tipos → auditoría de dependencias → escaneo de seguridad → build → deploy; **si falla una etapa crítica, no hay deploy**.

## 19. Pruebas de seguridad antes de abrir al público
SAST, DAST, escaneo de dependencias y de secretos, pentesting. Pruebas manuales: ¿puedo acceder a otro usuario? ¿modificar otro proyecto?
¿saltearme una lección? ¿ejecutar código prohibido? ¿subir un archivo peligroso? ¿manipular XP? ¿votar varias veces? ¿llamar directo a una API?

## 20. Específico de TortuScript
- **Integridad de la gamificación:** el cliente nunca dice "tengo 999999 XP". Solo puede decir "terminé la lección 18"; el servidor decide si estaba
  desbloqueada, si la completó, cuál es su mejor resultado y qué XP corresponde. Igual para niveles, logros, rachas, ligas, votos y certificados.
- **Sistema de intereses/votación:** limitar los votos repetidos (`POST /vote` mil veces); guardar solo el evento agregable y lo mínimo, y separar
  los datos educativos de los de producto.

## 21. Estándares de referencia
No inventar un concepto propio de "sitio seguro": usar **OWASP Top 10:2025** como base — Broken Access Control, Security Misconfiguration,
Software Supply Chain Failures, Cryptographic Failures, Injection, Insecure Design, Authentication Failures, Software/Data Integrity Failures,
Security Logging & Alerting Failures, Mishandling of Exceptional Conditions — y **OWASP ASVS** como checklist técnica; para headers,
el proyecto OWASP Secure Headers.

## 22. Estado actual de TortuScript frente a esa lista (auditoría del código, 25/09/2026)

| Tema | Estado hoy | Nota |
|---|---|---|
| HTTPS / HSTS | N/A | corre en `http://127.0.0.1`; obligatorio si se publica |
| Cookies y sesiones | N/A | no usa cookies ni sesiones |
| Contraseñas / cuentas | N/A | no hay cuentas |
| XSS | **PASS** | plantillas con autoescape; el JS pinta con `textContent` (no hay `innerHTML`, `eval` ni `document.write`); los datos viajan como JSON escapado; hay tests con `<script>` |
| Inyección SQL | N/A | no hay base de datos |
| CSRF | **Parcial** | toda la API exige un token secreto por sesión en un encabezado propio (no lo puede mandar una página ajena) y se rechazan `Host` no locales (anti *DNS rebinding*); falta modelo para cuentas reales |
| Security headers / CSP | **FAIL** | no se envía ninguno (CSP, `X-Content-Type-Options`, `Referrer-Policy`, `frame-ancestors`…) |
| Control de acceso | Parcial | hay perfiles locales sin aislamiento de seguridad entre ellos (misma PC, mismo servidor); no hay roles |
| Rate limiting | **FAIL** | no hay (irrelevante en local; obligatorio en línea) |
| Validación de entradas | PASS (local) | nombres, colores, tamaños de proyecto, valores de ajustes y respuestas se validan en el servidor |
| Subida de archivos | N/A | no existe |
| Ejecución de código | PASS para el runtime educativo | subproceso, AST, builtins limitados, sin `import`, tope de pasos, salida, tiempo y memoria; **insuficiente para un runtime de juegos** |
| Integridad de la gamificación | **PASS** | XP, estrellas, logros y progreso los calcula el servidor; el cliente no manda valores de XP |
| Dependencias | PASS (mínimo) | una sola (Flask, versión fijada); librerías del navegador guardadas localmente, nada desde CDN; faltan auditoría automática y *lockfile* |
| Secretos | PASS | no hay secretos en el repo; el token de sesión se genera al arrancar |
| Logs | Parcial | errores internos a `logs/tortuscript.log` (rotación); sin auditoría de eventos |
| Backups | Parcial | cada guardado deja `.bak` y se recupera si el archivo se daña; no hay backups externos |
| Manejo de errores | Parcial | se explican los errores del chico sin trazas; el detalle técnico queda aparte; falta una página 500 genérica con código de referencia |
| `robots.txt` / `sitemap.xml` / `security.txt` | N/A / TODO | no aplican a una app local; sí si se publica |
| CI/CD, SAST/DAST | TODO | hoy hay tests y un validador de contenido, sin pipeline ni escaneos |
| Privacidad y menores | Parcial | todo el progreso queda en la PC, sin datos personales ni terceros; falta política formal |

## 23. Cómo convertirlo en una especificación verificable
Crear en el repositorio `docs/security/` (cuando se decida publicar) con, al menos: `SECURITY.md`, `SECURITY_CHECKLIST.md`, `THREAT_MODEL.md`,
`CODE_EXECUTION.md`, `PRIVACY.md`, `DATA_RETENTION.md`, `INCIDENT_RESPONSE.md` y, según se necesiten, `AUTHENTICATION.md`, `SESSIONS.md`,
`COOKIES.md`, `CSRF.md`, `CSP.md`, `API_SECURITY.md`, `FILE_UPLOADS.md`; y en la raíz pública `robots.txt`, `sitemap.xml` y `security.txt`.

La `SECURITY_CHECKLIST.md` tendría tres niveles, y se auditaría punto por punto con `[PASS] / [FAIL] / [N/A] / [TODO]`:

| Nivel | Significado | Ejemplos |
|---|---|---|
| **P0** | obligatorio antes de producción | HTTPS + HSTS, headers y CSP, rate limiting, manejo de errores, logs, backups, aislamiento del runtime de código, secretos fuera del repo |
| **P1** | obligatorio antes de cuentas reales | hashing de contraseñas, sesiones y cookies seguras, CSRF, control de acceso/ownership, email (SPF/DKIM/DMARC), política de privacidad y datos de menores |
| **P2** | endurecimiento posterior | monitoreo y alertas, SAST/DAST, pentesting, CAPTCHA selectivo, auditoría de dependencias en CI |

Arquitectura objetivo (esquema):

```
INTERNET → HTTPS/TLS → Security Headers → Rate Limiting → WEB/API
                                                            ├─ Auth/ACL · CSRF · Validación de entradas
                                                            └─ APLICACIÓN → Base de datos → Backups
                                                                          → Proyectos
                                                                          → Game Runtime (SANDBOX → recursos)
                                        Logs y monitoreo transversales
```

> **Importante:** no implementar todo de golpe. Convertir la seguridad en una lista verificable (P0/P1/P2) permite auditar el proyecto punto por punto en lugar de pedir "hacelo seguro".
