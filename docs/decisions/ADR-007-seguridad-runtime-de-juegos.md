# ADR-007: Seguridad del runtime de juegos

## Estado: Propuesta (26/09/2026) — **no autoriza implementación**

> Ver la regla de gobernanza en el [índice](README.md). Origen: revisión crítica de `docs/experimental/` (26/09/2026).

## Contexto
"Corre en el navegador" no significa "es seguro". **Un Web Worker no es por sí mismo un sandbox suficiente**: por
defecto tiene `fetch`, `WebSocket`, `IndexedDB` e `importScripts`.

## Decisión propuesta
```
Código TortuScript → parser → AST propio → validador → intérprete TortuGame → Web Worker → Canvas
```
y **nunca**:
```
TortuScript → JavaScript generado → eval() / new Function()
```
- El código del chico solo puede hacer lo que el intérprete expone mediante la API TortuGame: la seguridad es una
  propiedad del lenguaje/runtime, no de las restricciones del navegador.
- **Permitido:** Canvas (a través del hilo principal), API TortuGame, límites de memoria, tiempo, ticks/instrucciones,
  cantidad de entidades y salida.
- **Prohibido:** red (`fetch`, `XMLHttpRequest`, `WebSocket`), cookies, `localStorage`/`IndexedDB` arbitrarios, DOM,
  sistema de archivos, navegación, `import`/`importScripts`, APIs externas.
- Segunda barrera: CSP estricta para el worker (`connect-src 'none'`, sin `unsafe-eval`).
- Antes de implementar hace falta un **modelo de amenazas** escrito del runtime.

## Consecuencias
+ Superficie de ataque acotada y verificable con tests.
− Escribir un intérprete propio es más trabajo que generar JS.
