# Producto completo: qué falta y modelo de cuentas (padre → hijos)

> **Estado: EXPERIMENTAL — brainstorming, no aprobado.** Continúa [RECORRIDO_DEL_USUARIO.md](RECORRIDO_DEL_USUARIO.md),
> [VISION_PLATAFORMA.md](VISION_PLATAFORMA.md) y [SEGURIDAD_SITIO_PROFESIONAL.md](SEGURIDAD_SITIO_PROFESIONAL.md).
> Hoy TortuScript es local, sin cuentas: los perfiles viven en la misma PC.

## 1. Decisión de producto (registrada)

> **Los padres crean la cuenta** (son mayores de edad) y **cada hijo tiene un perfil dentro de la cuenta del padre**.
> Un padre puede tener varios hijos.

```
Cuenta del adulto (email + contraseña)
 ├── Perfil hijo A  (apodo, avatar, progreso, proyectos, ajustes)
 ├── Perfil hijo B
 └── Panel de padres (progreso, tiempo, privacidad, datos, suscripción)
```

### Consecuencias directas
- **El niño no tiene email ni contraseña propios.** Se identifica eligiendo su perfil dentro de la sesión del adulto. Esto reduce los datos personales
  de menores, que es el punto más sensible del proyecto.
- **El perfil actual ya es la unidad correcta:** hoy cada perfil guarda progreso, ajustes y proyectos por separado. Pasa a ser *perfil hijo*;
  la cuenta es una capa nueva por encima. El progreso aditivo (ADR-002) no cambia su forma.
- **Dos niveles de acceso:** *modo niño* (aprender, crear, ver su progreso) y *modo adulto* (ajustes de cuenta, datos, privacidad, pagos). Entrar al modo
  adulto desde una sesión abierta debería pedir una confirmación (contraseña o PIN parental), para que el chico no cambie la cuenta.
- **El consentimiento lo da el adulto** (términos, privacidad, analítica, comunicaciones, publicación de proyectos), por separado y no en un único "Aceptar".
- **Casos a resolver:** adulto que comparte la cuenta con otro adulto, tutor distinto del padre, escuela o docente con varios alumnos (rol "Escuela"),
  hijo que crece y quiere independencia, eliminación de un perfil sin borrar la cuenta.
- **Normativa:** al haber datos de menores en línea hay que revisar con asesoramiento legal lo aplicable en cada país (consentimiento parental verificable,
  derechos de acceso/eliminación, retención). Es un requisito de diseño, no un trámite posterior.

### Decisión de arquitectura: **opción C (híbrido), elegida el 25/09/2026**

> **Actualización 26/09/2026:** el modelo padre → hijos y la opción C pasaron a [ADR-012](../decisions/ADR-012-cuenta-adulto-perfiles-hijo.md)
> y [ADR-013](../decisions/ADR-013-desktop-y-cloud.md) en estado **Propuesta**: son la dirección elegida, pero su implementación **no está autorizada**.
| Opción | Cómo funciona | Pros | Contras |
|---|---|---|---|
| **A. Local con "cuenta del hogar"** | Un perfil de adulto protege el modo padres; todo sigue en la PC | Mantiene el modelo offline y la privacidad; costo cero | Sin sincronización entre equipos; no permite cobro ni multi-dispositivo |
| **B. Online con sincronización** | Cuenta en servidor; progreso y proyectos en base de datos | Multi-dispositivo, panel de padres real, pagos, escuelas | Requiere backend, seguridad completa (P0/P1), normativa de menores, código de usuarios ejecutándose en servidor |
| **C. Híbrido (recomendado a evaluar)** | Aprendizaje y ejecución locales/en el navegador; la cuenta solo sincroniza progreso y datos del padre | Superficie de seguridad y datos mínima; se puede cobrar | Sincronización y resolución de conflictos |

> **Decidido: opción C.** Sigue siendo experimental (no hay implementación ni fecha). Fundamento de la recomendación: si el modelo de negocio es que el padre paga, la opción C evita ejecutar código infantil en servidores públicos,
> que es el mayor riesgo de seguridad (ver §10 del documento de seguridad).

## 2. Qué falta en el mapa del producto

Legenda de estado: **Existe** / **Parcial** / **Propuesto** / **Solo si es online**.

| Área | Qué falta considerar | Estado hoy |
|---|---|---|
| **Identidad** | Registro, login, logout, recuperar y cambiar contraseña, verificación de email, sesiones ("recordarme", cerrar otras), gestión y eliminación de cuenta, 2FA en cuentas administrativas | Solo si es online (hoy solo perfiles locales) |
| **Recuperar progreso** | Exportar/importar datos; sincronización si es online. El usuario piensa "¿qué pasa si cambio de compu?", no en JSON | Existe (26/09/2026): exportar el progreso a un archivo e importarlo como perfil nuevo, con validación; falta sincronización (solo si es online) |
| **Onboarding ampliado** | Experiencia previa, intereses, tiempo diario, accesibilidad, dispositivo (edad solo si es necesaria) | Parcial (meta diaria, accesibilidad) |
| **Estado al volver** | "Hola, Marcos. Ayer completaste Variables (+40 XP). Hoy te espera Preguntar. **[Continuar]**": recordar última lección, paso, proyecto, práctica pendiente | Parcial (hay Camino y siguiente ejercicio; falta la pantalla de retorno) |
| **Navegación global** | Barra fija: Inicio · Camino · Crear (Experimentar, Tortuga, Juegos) · Proyectos + perfil y ajustes | Parcial |
| **Notificaciones** | Dentro de la app (logro, racha, repaso pendiente); email solo al adulto. Con chicos: evitar mecanismos de engagement manipuladores | Parcial (avisos internos) |
| **Ayuda del producto** | Distinta de la Referencia: cómo empiezo, cómo guardo, cómo recupero mi progreso, reportar problema | Propuesto |
| **Errores del sistema** | Mensajes humanos ("Tu último guardado sigue disponible") + registro interno; sin "500 Internal Server Error" | Existe (log interno, recuperación del progreso y páginas de error propias con código de referencia, 26/09/2026) |
| **Privacidad en la UX** | Qué se recopila, por qué, cuánto tiempo, quién lo ve, cómo se elimina; visible en la interfaz, no solo en una página legal | Propuesto |
| **Consentimientos** | Separados: términos, comunicaciones, analítica, cookies no esenciales, publicación de proyectos | Solo si es online |
| **Proyectos privado / compartido / público** | Publicar, autor, versión, imagen, remixes | Propuesto (los proyectos son locales y privados) |
| **Moderación** | Reportar, bloquear, revisar, eliminar, antispam. **Desaparece casi por completo si nada se publica** | Solo si hay contenido compartido |
| **Administración** | Panel para usuarios, cursos, lecciones, reportes, feedback, errores, versiones; roles (administrador, editor, moderador, soporte) | Propuesto (los cursos son JSON con validador; a largo plazo, un CMS) |
| **Actualizaciones** | Aviso de nueva versión, actualizar, rollback, migración del progreso (ya aditivo) y de proyectos | Parcial (versionado del esquema; sin mecanismo de actualización) |
| **Seguridad** | HTTPS, sesiones, autorización, validación y sandbox. El README indica que el ejecutor **no** pretende ser sandbox para código hostil | Ver documento de seguridad |
| **Facturación** | Suscripciones, comprobantes, cancelación, plan Escuela/Institución. No implementar hasta definir el modelo de negocio | Propuesto |
| **SEO y descubrimiento** | `robots.txt`, `sitemap.xml`, títulos, metadescripciones, canonical, Open Graph, favicon, 404, `security.txt` (solo páginas públicas) | Solo si es sitio público |
| **Contacto y soporte** | Ayuda, contacto, reportar error, sugerir contenido, "¿Qué te gustaría que agreguemos?" (alimenta el roadmap con los intereses) | Propuesto |
| **Cierre del ciclo** | Aprender → practicar → crear → terminar proyecto → guardar → compartir → feedback → nuevo interés → nuevo camino | Propuesto |

## 3. Panel de padres (nuevo, deriva de la decisión)

- **Ver:** progreso por hijo y por tema, racha, tiempo de uso semanal, proyectos, últimas habilidades.
- **Controlar:** límites de tiempo opcionales, publicación de proyectos (por defecto **privada**), analítica opt-in, nombre visible anónimo.
- **Administrar:** agregar/quitar hijos, exportar y eliminar datos, gestionar suscripción, cambiar contraseña, cerrar sesiones.
- **Comunicación:** resúmenes semanales por email al adulto (opt-in); nada de emails directos al niño.

## 4. Mapa de áreas

```
TORTUSCRIPT
 ├── IDENTIDAD (cuenta del adulto · perfiles hijo · sesiones · panel de padres)
 ├── APRENDIZAJE (onboarding · diagnóstico · camino · lecciones · práctica · progreso)
 ├── CREACIÓN (experimentar · tortuga · proyectos · juegos · portfolio)
 ├── PERSONALIZACIÓN (intereses · recomendaciones)
 ├── COMUNIDAD (compartir/publicar: solo con controles parentales y moderación)
 └── FEEDBACK → ROADMAP → NUEVO CONTENIDO
Capas invisibles: seguridad · privacidad · backups · monitoreo · analítica · administración · actualizaciones · soporte · infraestructura
```

## 5. Lo más importante: definir el estado completo del usuario
Qué ve el adulto y el niño al llegar, al volver al día siguiente, a la semana y a los seis meses; y dónde vive ese estado (JSON local, cuenta online,
base de datos o una combinación). Esa definición condiciona todo lo demás.

## 6. Preguntas abiertas
1. ~~¿Opción A, B o C?~~ Resuelto: **C**. Falta definir qué se sincroniza exactamente y cómo se resuelven los conflictos.
2. ¿Habrá contenido compartido/público entre chicos, o el producto se mantiene privado por diseño?
3. ¿Se contempla el rol docente/escuela desde el inicio o más adelante?
4. ¿Qué edad mínima y máxima se apunta (10–14 en el material actual) y cómo se comunica a los padres?
5. ¿Cómo se migran los perfiles locales existentes a una cuenta (importación desde el archivo de progreso)?
