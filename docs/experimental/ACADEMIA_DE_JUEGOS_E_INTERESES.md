# Visión experimental: Academia de desarrollo de juegos y sistema de intereses

> **Estado: EXPERIMENTAL — brainstorming, no aprobado.** Continúa [VISION_PLATAFORMA.md](VISION_PLATAFORMA.md)
> (25/09/2026). Nada de lo que figura como "propuesto" está implementado. Ver lo que existe hoy en el
> [README](../../README.md).

## 1. Las dos preguntas

1. **¿Dónde encaja una orientación 100 % a desarrollo de juegos** (estilo Calabozos y Dragones, Warcraft, Pathfinder)?
2. **Más adelante:** que los usuarios **comuniquen sus intereses** dentro de la plataforma, para decidir qué construir.

**Respuesta corta:** los juegos pueden ser **una rama principal** ("Crear") y no solo un proyecto avanzado de Python; y el
registro de intereses conviene diseñarlo **desde ahora** como infraestructura mínima, aunque la interfaz llegue mucho después.

## 2. Referencia pedagógica

Se tomó como inspiración la **progresión conceptual** de un libro de programación por juegos (material que aportó el
autor del proyecto): variables, control de flujo y funciones → un primer juego de fantasía ("Reino de Dragones") →
depuración → diagramas de flujo → listas y diccionarios → IA → coordenadas → Pygame (eventos, animación, colisiones,
sprites, sonido, imágenes).

> **Regla:** se adopta la *secuencia de ideas*, **no el contenido** (textos, ejemplos, arte). Todo el material se escribe
> de cero, en el estilo de TortuScript. Mismo criterio que en el roadmap original: mecánicas sí, contenido ajeno no.

## 3. Estructura propuesta: "Aprender" y "Crear"

```
TORTUSCRIPT
├── APRENDER   Python · Web · SQL
├── CREAR      JUEGOS · Proyectos
└── EXPLORAR   Mundo
```

Rama de juegos:

```
🎮 Desarrollo de videojuegos
├── Fundamentos · Mundos y mapas · Combate · Personajes · Enemigos · Inventario
├── Vida y estadísticas · Habilidades · Economía · IA · Dados y azar
├── Misiones · Diálogos · Mazmorras · Bosses · Proyecto final
```

Géneros como contextos pedagógicos distintos:

| Género | Conceptos que enseña |
|---|---|
| 🏰 RPG (D&D, Pathfinder, JRPG, roguelike) | estadísticas, diccionarios, inventario, combate por turnos, dados, loot, experiencia |
| ⚔️ Acción (plataformas, beat'em up) | colisiones, movimiento, estados |
| 🏹 Estrategia (tower defense, RTS, tácticos) | oleadas, rangos, cooldowns, economía, IA, pathfinding |
| 🧩 Puzzle · 👾 Arcade · 🗺️ Aventura · 🃏 Cartas | lógica, listas, reglas, narrativa |

Ejemplo de ruta RTS (estilo Warcraft, en versión mini): unidades → recursos (oro, madera, población) → producción
(`crear_unidad`, `construir_edificio`) → IA (`si enemigo_cerca: atacar`) → pathfinding → economía → batallas → proyecto final.
No hace falta replicar Warcraft: alcanza con un sistema chico que el alumno pueda **entender entero**.

## 4. Principio pedagógico: el concepto aparece porque el juego lo necesita

No una lección de "listas" seguida de "Pygame", sino un objetivo del juego que exige el concepto:

| Necesidad del juego | Concepto | Ejemplo |
|---|---|---|
| "Creá la vida de tu guerrero" | variables | `vida = 100` |
| "Tu guerrero recibió un golpe" | operaciones | `vida = vida - 20` |
| "Si la vida llega a cero, muere" | condicionales | `if vida <= 0:` |
| Recorrer enemigos | bucles | `for enemigo in enemigos:` |
| Un ataque reutilizable | funciones | `def atacar(enemigo):` |
| Personajes | diccionarios | `{"nombre": "Tharok", "vida": 100}` |
| Inventario | listas | `["espada", "poción", "escudo"]` |
| Dados y loot | azar | `random` |

### Idea fuerte: el primer curso como RPG
El chico no ve "Curso Python — Lección 1" sino un mapa: **Tierras de Tortuaria** (aldea → bosque → cueva → mazmorra →
castillo → dragón). Cada zona enseña algo: aldea = variables, bosque = condicionales, cueva = bucles, mazmorra =
funciones, castillo = listas y diccionarios, dragón = proyecto integrador (un mini RPG).

### Ruta de ejemplo (a validar)
- **Python RPG I:** el héroe · sus estadísticas · el primer enemigo · el combate · los dados · el inventario · las pociones · el mapa · la mazmorra · el jefe → *BOSS: La Mazmorra del Bug*.
- **Python RPG II:** clases · objetos · herencia · estados · equipamiento · habilidades · NPC · misiones · guardado.
- **Game Development I:** Pygame.

## 4 bis. Dónde encaja en el proyecto actual

| Pieza | Hoy | Para juegos |
|---|---|---|
| **Contenido** (`contenido/cursos/*.json`) | 4 cursos como datos + validador | Un curso "Tortuaria" con los mismos 6 tipos de paso; el mapa por zonas se apoya en el camino y en `requiere`. Es lo primero que se puede hacer **sin tocar el motor**. |
| **Ejecutor educativo** (`tortuscript/executor.py`) | AST validado, sin `import`, builtins limitados, subproceso, tope de memoria | Suficiente para RPG por consola (variables, combate por turnos). **No** sirve para Pygame ni para `random`/`import` libres. |
| **Dibujos** (`tortuscript/tortuga.py`) | registro de órdenes + canvas | Modelo reutilizable: el servidor registra eventos y el navegador los anima (mapas, sprites simples) sin ejecutar gráficos en el servidor. |
| **Progreso** (`progreso.py`) | esquema aditivo, hoy v8 | Nuevos campos aditivos: intereses, votos, colección/avatar, guardado de partidas. |
| **Proyectos** (`proyectos.py`) | 30 por perfil, tipos `experimentar`/`tortuga` | Nuevo tipo `juego`. |
| **Logros / liga / XP** | 25 logros, liga local | Logros de género (primer combate, primer boss). |

## 5. Decisión técnica clave: dos runtimes

No meter un juego Pygame dentro del ejecutor educativo. Separar conceptualmente:

```
EDUCATIONAL RUNTIME  →  ejercicios pequeños        (¿aprendió `if`?)
GAME RUNTIME         →  proyectos completos        (¿puede construir un juego?)
```

Estructura tentativa del núcleo (ilustrativa):

```
tortuscript/
├── translator.py, executor.py, evaluacion.py     (actual)
└── game/  engine · scene · entity · collision · combat · inventory · dialogue · quests · save
```

### 5.1 Una API de juego propia (TortuGame)
En vez de exponer Pygame directamente, darle al niño una API pequeña y en español que después "se abre" hacia Python real:

```
TortuScript  →  TortuGame  →  Python  →  (opcional) Pygame
```

Ejemplo de la progresión: primero `si enemigo cerca: atacar`, luego
`jugador = crear_personaje("Guerrero")` / `cuando_colisionen(jugador, enemigo)`, y por último
`if enemy.distance_to(player) < attack_range: player.attack(enemy)`. Es la misma idea del puente TortuScript → Python real
que ya existe, aplicada a juegos.

### 5.2 Riesgos técnicos a evaluar antes de construir
- **Seguridad:** un runtime de juegos amplía la superficie (más builtins, tiempo de ejecución largo, bucles de juego). Hay que decidir
  si corre en el navegador (JS/canvas, sin servidor) o en un subproceso con límites; la primera opción encaja mejor con el modelo offline actual.
- **Evaluación:** hoy se compara texto o dibujo estático; un juego necesita evaluar comportamiento (simulaciones deterministas con semilla).
- **Alcance:** cada género multiplica contenido y mantenimiento; empezar por **un** género (RPG por turnos) y medir tracción.
- **Derechos:** nombres como Warcraft, Pathfinder o Dungeons & Dragons son marcas: usarlos solo como *referencia de género*
  en la comunicación; el contenido, los nombres y el arte propios.

## 6. Sistema de intereses ("¿Qué querés aprender?")

**Objetivo:** que los datos de uso digan qué construir después (RPG, estrategia, web, IA...) en lugar de decidir solo por intuición.

### 6.1 Cuándo preguntar (dentro del contexto)
- Al terminar un curso o un proyecto: *"Ahora que sabés programar… ¿qué te gustaría crear?"* (videojuegos, RPG, estrategia, web, IA, robots, apps, arte, bases de datos, ciberseguridad, simulaciones, música, otro).
- Segunda pregunta: *"¿Qué juego te gustaría hacer?"* (RPG, cartas, estrategia, plataformas, terror, multijugador, aventura, otro).
- Mucho más útil que una encuesta genérica anual.

### 6.2 Votación de futuros
Pantalla "El futuro de Tortuaria": lista de ideas con votos. Se comunica como *"tu opinión nos ayuda a decidir qué explorar"*,
**sin prometer** que la más votada se construya (no es un contrato de producto).

### 6.3 Privacidad (son menores)
Se guarda lo mínimo: **sin nombre real, edad exacta, ubicación, colegio ni redes**. Basta algo como:

```json
{"interests": ["games", "rpg", "strategy"], "feature_votes": ["rpg_engine", "javascript"]}
```

Coherente con el diseño actual: los perfiles guardan todo **localmente** y no hay cuentas. Punto a resolver: hoy nada sale de la compu, de modo que
**para "evaluar futuras implementaciones" hay que decidir cómo se agregan los datos** (opciones: exportación voluntaria y anónima que el
adulto envía; o, si algún día hay backend, envío con consentimiento parental). Esto es un cambio de arquitectura y de política, no un detalle.

### 6.4 Infraestructura mínima que se puede preparar ya
Reutilizando la idea de "contenido como datos":

```
contenido/encuestas/*.json      # preguntas y opciones, validables como los cursos
tortuscript/intereses.py        # registrar/consultar intereses y votos del perfil (puro, testeable)
progreso: campo "intereses" y "votos"   # aditivo, como los demás
```

Ejemplo de encuesta como dato:

```json
{"id": "future_games", "question": "¿Qué tipo de juegos querés aprender a crear?",
 "options": ["rpg", "strategy", "platformer", "card_game", "horror", "simulation"]}
```

Con eso la funcionalidad visible puede llegar más adelante sin rehacer nada.

## 7. Tres motores, un solo producto

```
Learning Engine            (existe: cursos, pasos, progreso, XP, repaso, proyectos)
Game Development Engine    (propuesto: extensión del anterior, no otro programa)
Interest / Feedback Engine (propuesto: preferencias, encuestas, votos, solicitudes)
```

**Recomendación del brainstorming:** no renombrar ni reescribir el motor todavía; preparar el terreno con los intereses y diseñar el
motor de juegos como **extensión** del de aprendizaje.

## 8. Próximos pasos posibles (sin compromiso)

1. Escribir un curso piloto de RPG por consola con el motor actual (solo datos + validación), para medir si a los chicos les interesa.
2. Agregar `intereses.py`, un campo aditivo en el progreso y una encuesta de un solo paso al terminar un curso (todo local).
3. Definir cómo se recolectarían los datos de intereses de forma agregada y con consentimiento.
4. Prototipar el "game runtime" en el navegador antes de tocar el ejecutor del servidor.
5. Validar todo con chicos reales antes de ampliar.
