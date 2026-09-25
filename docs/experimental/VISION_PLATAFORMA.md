# Visión experimental: de curso de Python a plataforma educativa

> **Estado: EXPERIMENTAL — brainstorming, no aprobado.** Este documento recoge ideas para escalar TortuScript
> (25/09/2026). No es un compromiso ni un roadmap: nada de lo que figura como "propuesto" está implementado.
> Cada idea debería validarse con chicos reales antes de construirse. Para lo que sí existe hoy, ver el
> [README](../../README.md), el [CHANGELOG](../../CHANGELOG.md) y [ADR-002](../decisions/ADR-002-cursos-como-datos-y-progreso-aditivo.md).

> Continúa en [ACADEMIA_DE_JUEGOS_E_INTERESES.md](ACADEMIA_DE_JUEGOS_E_INTERESES.md): rama de desarrollo de juegos (RPG, estrategia) y sistema de intereses.

> Secuencia completa vista por el usuario: [RECORRIDO_DEL_USUARIO.md](RECORRIDO_DEL_USUARIO.md).

> Plan consolidado por fases y estimación de magnitud: [ROADMAP_MAESTRO.md](ROADMAP_MAESTRO.md).

## 1. Punto de partida

**La idea:** llevar el proyecto a un siguiente nivel: un curso de programación para chicos, **gratis hasta cierto punto**
y con niveles y funciones que se desbloquean con un pago; divertido, similar a Mimo pero centrado en la experiencia del
niño; y posiblemente con más lenguajes (HTML, CSS, JS, SQL), no solo Python.

**Lo que ya existe** (estado real de la rama `main`):

| Capacidad | Estado |
|---|---|
| Motor de cursos basado en datos (JSON) + validador automático | ✅ hecho |
| 4 cursos: fundamentos, tortuga, proyectos guiados, puente a Python real (51 lecciones) | ✅ hecho |
| XP, niveles, racha con congeladores, logros (25), liga local, meta diaria | ✅ hecho |
| Práctica del día (repaso espaciado), Mis proyectos, certificado | ✅ hecho |
| Perfiles, accesibilidad (letra, contraste, teclado, voz) | ✅ hecho |
| Ejecución segura en subproceso con límites; funciona offline y en local | ✅ hecho |
| Pagos, cuentas, panel de padres, avatar, mundos, bosses, otros lenguajes | ❌ no existe |

## 2. Cambio conceptual: de curso a plataforma

Separar tres capas:

- **Plataforma:** perfiles, progreso, XP, niveles, logros, ligas, inventario, avatar, configuración.
- **Academia:** las disciplinas (Python, HTML, CSS, JavaScript, SQL, algoritmos).
- **Mundo:** personajes, misiones, desafíos, proyectos, historia, coleccionables.

Python pasa a ser *una* disciplina. Estructura propuesta ("Tortuverse"):

```
TORTUVERSE
├── Academia      Python · HTML · CSS · JavaScript · SQL · Algoritmos
├── Laboratorio   Experimentar · Proyectos · Tortuga · Web · Base de datos
├── Aventuras     Misiones · Desafíos · Bosses
├── Comunidad     Liga · Ranking · Amigos
└── Perfil        Nivel · Logros · Colección · Certificados
```

**Principio rector:** *Mimo enseña programación; TortuScript permite vivir la programación.* El chico aprende Python
porque necesita resolver una misión y construye algo porque quiere mostrarlo.

## 3. Prioridad: primero profundizar, después ampliar

No sumar lenguajes enseguida (riesgo: una biblioteca de cursos). El diferencial es la **experiencia de aprendizaje**.
Primero llevar Python "de `mostrar Hola` a crear algo propio", con cada curso terminando en **un proyecto**:

| Nivel | Contenido propuesto |
|---|---|
| Python I — Aprendiz | variables, condiciones, bucles, funciones, listas, diccionarios |
| Python II — Constructor | archivos, módulos, random, fechas, errores, programación estructurada |
| Python III — Creador | juegos simples, simulaciones, generadores, mini herramientas, interfaces |
| Python IV — Hacker | algoritmos, estructuras de datos, debugging, optimización, criptografía conceptual, APIs simuladas |
| Python V — Maestro | proyectos completos |

## 4. Mecánicas de juego propuestas

### 4.1 Mapa de mundos en lugar de lista de lecciones
Avanzar por un mundo visual (ciudad digital, bosque de algoritmos, torre de funciones) en vez de "Lección 1, 2, 3".
Hoy el camino es lineal en zig-zag; un mapa navegable sería la evolución.

### 4.2 Bosses como resolución de problemas
Después de varias lecciones, un desafío con contexto que exige razonar, no solo recordar. Ejemplos:
- **El Dragón del Bucle Infinito:** arreglar un `mientras energia > 0` que nunca termina para que escape.
- **El Cofre de las Variables:** construir un programa que abra el cofre usando lo aprendido.
- **Boss final:** construí tu propio juego.

### 4.3 Proyectos como corazón del producto
Hoy existe *Mis proyectos* (guardar, abrir, duplicar, borrar) y 3 proyectos guiados. Propuesta: proyectos largos por
etapas, p. ej. **"Mi primer juego"** (personaje → variables → enemigos → puntuación → condiciones → bucles →
funciones → pantalla final), cerrando con "🏆 Creaste tu primer juego". Valor percibido: *creé algo*, no *completé 17 lecciones*.

### 4.4 Árbol de habilidades en vez de curso lineal
Habilidades con niveles propios (Lógica, Código, Creatividad; Python, Web, Diseño, SQL), mostradas como barras de
progreso en el perfil: representación del avance, no evaluación escolar.

### 4.5 Economía interna
- **XP** → subir de nivel (aprendizaje).
- **Monedas (p. ej. "Tortus")** → comprar cosméticos.
- **Logros** → insignias.
- Regla clave: **el dinero real no compra XP ni ventaja competitiva**; solo desbloquea contenido.

### 4.6 Avatar, colección y mentores
- Avatar personalizable (casco, capa, mascota, efectos) que se **desbloquea por aprender** (completar Python I → capa de aprendiz; 5 proyectos → mascota; 10 desafíos → espada).
- Personajes mentores por disciplina: 🐢 Torto (Python), 🦊 Pixel (Web), 🤖 SQL-7 (bases de datos), 🧙 Algor (algoritmos).
- Historia mínima: en el mundo digital *Tortuaria*, los Bugs destruyen los sistemas y el jugador los repara programando. Python reconstruye el mundo, HTML construye ciudades, CSS las decora, JavaScript les da vida, SQL recupera información, los algoritmos derrotan bugs.

## 5. Otras disciplinas (después de que Python sea excelente)

| Academia | Enfoque propuesto |
|---|---|
| 🌐 **HTML + CSS** | Editor de tres paneles (HTML / CSS / vista previa en vivo); resultados visibles al instante, más satisfactorio que la consola. |
| ⚡ **JavaScript** | Progresión natural desde la web: calculadora → juego de memoria → página propia → sitio propio. |
| 🗄️ **SQL** | Presentado como **investigación detectivesca** ("¿quién estuvo en el castillo la noche del 17 de octubre?") sobre una base de registros. |
| 🧠 **Algoritmos** | Forma de pensar; encaja con los bosses. |

Cada una representa "una forma distinta de pensar": Python construye, HTML estructura, CSS diseña, JavaScript interactúa,
SQL investiga, los algoritmos piensan.

## 6. Modelo de negocio (freemium)

Evitar "todo bloqueado hasta que pagues": el chico tiene que sentir *"ya aprendí algo"* antes del muro de pago.

- **Gratis:** Python inicial completo (~30 lecciones), Tortuga, Experimentar, primer proyecto, logros iniciales, racha, liga local.
- **Premium:** Python avanzado, Web, JavaScript, SQL, proyectos avanzados, mundos especiales, certificados avanzados, contenido nuevo.

**Cliente doble:** el niño usa, el **padre paga**. Requiere, eventualmente, un **panel para padres** (tiempo de uso por
semana, progreso por tema, últimas habilidades, racha, proyectos) y controles de privacidad (nombre anónimo, sin
interacción social pública).

## 7. Comunidad y privacidad (menores)

- **No** construir una red social infantil al principio.
- La **liga local** actual simula competencia sin exponer a los chicos en internet: mantenerla como base.
- Un sistema online (amigos, rankings globales) solo más adelante y con controles parentales, moderación y
  cumplimiento de privacidad para menores.

## 8. Arquitectura: hacia un motor agnóstico al lenguaje

El motor ya sabe *lección → paso → ejercicio → respuesta → recompensa → progreso → desbloqueo* y no depende de Python
en sus reglas. Propuesta de organización del contenido:

```
contenido/
├── python/      fundamentos.json · tortuga.json · proyectos.json
├── html/        fundamentos.json · estructura.json
├── css/         fundamentos.json · layouts.json
├── javascript/  fundamentos.json · interactividad.json
└── sql/         fundamentos.json · detectives.json
```

Lo que habría que generalizar (hoy está acoplado a TortuScript/Python): el evaluador (comparación de salida de texto y de
dibujos; para web haría falta comparar DOM/estilos/render; para SQL, resultados de consultas), el ejecutor seguro por
lenguaje, y los tipos de paso.

**Course Builder / CMS educativo:** herramienta interna para crear lecciones sin editar JSON a mano (título,
explicación, tipo de ejercicio, guardar), apoyada en el validador que ya existe. Permite, más adelante, **packs
temáticos** ("Programá tu videojuego", "Creá tu página web", "Construí un chatbot", "Detective SQL", "Simulación espacial").

## 9. Hoja de ruta propuesta (a validar)

| Fase | Objetivo | Contenido |
|---|---|---|
| **1. Convertir TortuScript en producto** | Que Python sea excelente y un chico lo use sin explicación | más lecciones, proyectos, bosses y desafíos; avatar; mapa visual; mejor onboarding y tutorial; pulido visual; sistema de recompensas; free/premium |
| **2. Python creativo** | "¿Qué puedo construir con Python?" | juegos, arte, simulaciones, historias, proyectos |
| **3. Web** | Resultados inmediatamente visibles | HTML, CSS, JavaScript y un editor visual de páginas |
| **4. Academia completa** | Ampliar | SQL, algoritmos, Git, computación, IA (no todos como lenguajes) |
| **5. TortuScript Studio** (horizonte) | Entorno de **creación**, no solo de estudio | archivos (`main.py`, `index.html`, `style.css`, `game.js`), vista previa y terminal en un mismo espacio |

## 10. Preguntas abiertas y riesgos

- ¿Qué parte del contenido gratuito hace falta para que un chico *sienta* valor antes del pago? (medir con usuarios reales).
- **Pagos y cuentas:** hoy el proyecto es offline y sin cuentas. Cobrar implica identidad, licencias, pasarela de pago,
  y decidir si el contenido premium se descarga o se sirve en línea. Es un cambio de arquitectura importante, no un agregado.
- **Datos de menores:** cualquier cuenta o dato en línea obliga a evaluar la normativa aplicable de protección de datos
  y consentimiento parental antes de construir.
- **Derechos:** al copiar mecánicas de Mimo, mantener contenido, arte y marca propios (ya se aplica en el roadmap original).
- **Alcance:** cada nueva academia multiplica contenido, evaluación y mantenimiento; conviene medir la tracción de Python antes.
- **Ejecución en el navegador vs. local:** SQL y web pueden resolverse en el cliente (SQLite en WebAssembly, `<iframe>` con
  vista previa), evitando nuevos ejecutores en el servidor: a evaluar.

## 11. Cómo se relaciona con lo ya construido

Casi todo el trabajo previo es base directa: motor de cursos como datos y validador (Academia), perfiles/XP/logros/liga
(Plataforma), proyectos guardables y guiados (Laboratorio), certificados y accesibilidad (Perfil). Lo genuinamente nuevo
es: **mundo/mapa y bosses, avatar y economía cosmética, panel de padres, freemium/pagos, y el editor multi-lenguaje.**
