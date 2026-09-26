# Cómo escribir un curso

Los cursos son **datos**: archivos JSON en `contenido/cursos/`. Un motor los muestra (`tortuscript/leccion.py` + `web/static/js/leccion.js`) y un **validador** los revisa solo. No hace falta tocar código para agregar una lección.

```bash
python herramientas/validar_contenido.py            # todos los cursos
python herramientas/validar_contenido.py tortuga    # uno solo
python -m unittest tests.test_contenido             # el validador también corre dentro de los tests
```

El validador sale con código 1 si hay un ❌ (error); los ⚠️ son avisos para revisar a mano.

## Estructura

```json
{
  "id": "mi-curso", "titulo": "Mi curso", "icono": "🚀", "descripcion": "Una línea.", "version": 1,
  "requiere": {"leccion": "par-o-impar"},
  "secciones": [
    {"id": "basico", "nivel": 1, "titulo": "Lo básico", "lecciones": [
      {"id": "mi-leccion", "titulo": "1. Mi lección", "requiere": "otra-leccion",
       "pasos": [ {"tipo": "explicacion", "texto": "..."} ]}
    ]}
  ]
}
```

- `id` de curso, sección y lección: únicos (las lecciones, entre **todos** los cursos).
- `requiere` (curso): el curso está cerrado hasta completar esa lección. `requiere` (lección): queda bloqueada hasta completar la otra; las que siguen esperan (el camino nunca se saltea una lección).
- Un curso nuevo aparece solo en el camino; para fijar su lugar, agregalo a `ORDEN_CURSOS` en `tortuscript/contenido.py`.
- El título de la lección lleva el número: `"3. Dos líneas"`.

## Los 6 tipos de paso

| Tipo | Campos | Qué hace el chico |
|---|---|---|
| `explicacion` | `texto`, `codigo`?, `tortu`?, `forma`?, `lienzo`?, `entradas_prueba`? | Lee y puede **Probar** el ejemplo. Con `tortu` + `codigo` se muestran lado a lado TortuScript y Python (el Python **tiene que ser exactamente la traducción**: el validador lo comprueba). Con `lienzo` el ejemplo dibuja con la tortuga. |
| `elegir` | `pregunta`, `opciones[]`, `correcta` (índice), `codigo`?, `pista`?, `lienzo`? | Toca la opción correcta. |
| `predecir` | `codigo`, `opciones[]`, `correcta`, `pregunta`?, `pista`?, `entradas_prueba`?, `cuenta`? | Dice qué muestra el programa. El validador **corre el código** y exige que la opción correcta sea lo que muestra. Con `"cuenta": "trazos"` la respuesta es cuántas líneas dibuja. |
| `completar` | `consigna`, `codigo` (con `___`), `fichas[]`, `respuesta[]`, `salida`?, `pista`?, `tortuga`? | Toca fichas para llenar los huecos. Si otra combinación muestra lo mismo (o dibuja lo mismo), también vale. |
| `ordenar` | `consigna`, `lineas[]` (en el orden correcto), `pista`?, `tortuga`? | Toca las líneas en orden. Otro orden que dé el mismo resultado también vale. |
| `escribir` | `consigna`, `solucion`, `forma`?, `nota`?, `inicial`?, `entradas_prueba`?, `tortuga`?, `lenguaje`?, `palabras_pista`? | Escribe el programa. Se compara **lo que muestra** (o el dibujo) con lo que muestra la solución; hay 3 pistas (palabras clave, primera línea, solución). |

Detalles:

- **La opción correcta va donde quieras** en `opciones`: en pantalla se mezclan siempre igual para cada paso (no cambian al recargar). La respuesta correcta **nunca** viaja al navegador.
- `forma` es la sintaxis que se presenta por primera vez (se muestra aparte). La primera vez que aparece una palabra de TortuScript tiene que haber una `forma` o un ejemplo en una `explicacion`: el validador marca ❌ si se usa antes de enseñarla.
- `entradas_prueba` son las respuestas para `preguntar()` cuando el validador corre el paso. Obligatorias si la solución pregunta.
- `tortuga: true` (en `completar`, `ordenar`, `escribir`) compara **dibujos** en vez de texto: se considera igual si cubre las mismas celdas de 3×3 con los mismos colores (no importa el orden ni cuántos `avanzar` se usen; 89° en vez de 90° ya falla). En la pantalla aparece el dibujo objetivo.
- `laberinto` (en `escribir` con `tortuga: true`): `{"paredes": [[x1, y1, x2, y2], ...], "salida": [x, y]}`, en las coordenadas
  del dibujo (la tortuga sale de 0,0 mirando hacia arriba; hacia arriba es `y` negativo). **No hay dibujo objetivo**: vale
  cualquier recorrido que no toque una pared (a menos de 6 unidades, con el lápiz arriba o abajo) y termine a menos de 20
  de la salida. Si choca, el chico ve la línea que la hizo chocar. La `solucion` se usa para las pistas y el validador
  comprueba que cumpla las reglas. Conviene dejar pasillos de 60 de ancho con el camino por el medio.
- **Azar con `dado(caras)`** (ADR-009): devuelve un número de 1 a `caras` (6 si no se dice). Al evaluar y al validar se
  usa siempre la misma semilla (`SEMILLA_EVALUACION`), así que el programa del chico y la solución tiran los mismos
  números **si los piden en el mismo orden**. Un `predecir` con `dado` es válido: la opción correcta es la que sale con esa
  semilla (el validador la comprueba). Como cualquier palabra, `dado` hay que presentarlo antes de usarlo.
- `usar` (solo en laberintos): palabras que el recorrido tiene que usar, p. ej. `["repetir"]`. Si llega sin usarlas, no vale.
- `lienzo: true` en `explicacion`, `elegir` y `predecir` agrega el botón para ver qué dibuja el código.
- `inicial` (en `escribir`): el editor arranca con ese código (proyectos guiados). Sus líneas tienen que aparecer, en orden, dentro de la solución.
- `lenguaje: "python"` (en `escribir`): el chico escribe Python real. Agregá `palabras_pista` (por ejemplo `["print", "="]`) porque la pista 1 sale del traductor.

## Reglas de estilo (las revisa el validador como avisos)

- Frases cortas (≤ 25 palabras) y textos de hasta 200 caracteres; voseo rioplatense ("Mirá", "Escribí").
- Sin jerga (`string`, `float`, `sintaxis`, `iterar`...) ni palabras que suelen escribirse sin tilde (`línea`, `número`, `función`).
- Una palabra de TortuScript dentro de un texto va entre comillas si el validador la marca (`"funcion"`).
- Pistas específicas donde el error es típico (comillas, indentación, mayúsculas, condición falsa).

## Lo que no hay que romper

- **El orden de los pasos `escribir` del curso `primeros-pasos`**: su posición (0 a 29) es la clave del progreso guardado (`ejercicios`). Un test lo verifica. Se puede agregar contenido antes o entre pasos que no sean `escribir`, pero no reordenar ni sacar ejercicios.
- Los ids de lección aparecen en el progreso (`lecciones`), en los logros y en `requiere`: renombrarlos borra el avance de esa lección.
- Los logros de cursos completos se enganchan a los ids `primeros-pasos`, `tortuga` y `python-real` (`tortuscript/logros.py`).

## XP y niveles

Un paso de práctica vale 5 XP al primer intento, 2 con reintentos y 0 si se vio la respuesta; leer no da XP. Un `escribir` vale 30/20/10/5 según las pistas usadas. `leccion.xp_maximo(curso)` calcula lo que da una pasada perfecta y `tests/test_progreso.py` exige que el nivel máximo siga siendo alcanzable (y no a mitad del curso).

## Flujo de trabajo recomendado

1. Escribí la lección (copiá una parecida) y corré el validador: te dice qué paso está mal y por qué.
2. Corré los tests: `python -m unittest discover tests`.
3. Con Playwright, `python herramientas/jugar_cursos.py mi-curso` juega la lección completa por la interfaz real.
