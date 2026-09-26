/* Motor de lecciones: dibuja un paso por vez y le pregunta al servidor si está bien.
   Todo el texto que viene de los datos se pinta con textContent (nunca como HTML). */
"use strict";
(() => {
  const datos = JSON.parse(document.getElementById("datos-leccion").textContent);
  const pasos = datos.pasos;
  const cont = document.getElementById("lec-paso");
  const pie = document.getElementById("lec-pie");
  const mensaje = document.getElementById("lec-mensaje");
  const btnPrincipal = document.getElementById("lec-principal");
  const btnVer = document.getElementById("lec-ver");
  const barra = document.getElementById("lec-barra");
  const contador = document.getElementById("lec-contador");
  const progresoAria = document.getElementById("lec-progreso");
  const HUECO = "___";

  let actual = 0;
  let xpTotal = 0;
  let perfectos = 0;
  let hechos = 0;
  let accion = null;            // qué hace el botón principal ahora mismo
  let leerRespuesta = null;     // devuelve la respuesta armada por el chico (o null si falta algo)
  let resultadoFinal = null;    // último "leccion" que devolvió el servidor
  let editor = null;
  let teclas = null;            // atajos del paso actual (por ahora: 1 a 9 para elegir una opción)

  // ───────── utilidades de DOM ─────────
  function el(tag, clase, texto) {
    const e = document.createElement(tag);
    if (clase) e.className = clase;
    if (texto !== undefined) e.textContent = texto;
    return e;
  }
  function bloqueCodigo(codigo) {
    const pre = el("pre", "codigo-paso");
    pre.textContent = codigo;
    return pre;
  }

  // ───────── lienzos de la tortuga ─────────
  function lienzoNuevo() {
    const c = document.createElement("canvas");
    c.width = 600; c.height = 600; c.className = "lienzo-paso";
    c.setAttribute("role", "img");
    return c;
  }
  /** "Tenés que dibujar esto": el dibujo de la solución, ya pintado. */
  function cajaObjetivo(paso) {
    if (!paso.objetivo) return null;
    const caja = el("div", "objetivo-caja");
    caja.appendChild(el("div", "rotulo-zona", "🎯 Tenés que dibujar esto:"));
    const c = lienzoNuevo(); c.setAttribute("aria-label", "Dibujo que hay que lograr");
    caja.appendChild(c);
    const lienzo = Lienzo.crear(c);
    lienzo.usarVista(Lienzo.vistaPara(paso.objetivo));
    lienzo.dibujar(paso.objetivo);
    caja.lienzo = lienzo;                      // para volver a encuadrar junto al dibujo del alumno
    return caja;
  }
  /** Ejemplo ejecutable: con `lienzo` dibuja con la tortuga; si no, muestra el texto que imprime. */
  function bloqueEjecutable(paso, etiqueta) {
    const caja = el("div", "ejemplo-ejecutable");
    if (paso.tortu) {                                     // TortuScript y su Python, lado a lado
      const par = el("div", "par-codigo");
      for (const [rotulo, codigo, clase] of [["TortuScript", paso.tortu, "tortu-c"], ["Python", paso.codigo, "py-c"]]) {
        const c = el("div", `codigo-caja ${clase}`);
        c.appendChild(el("span", "rotulo", rotulo));
        c.appendChild(el("pre", "", codigo));
        par.appendChild(c);
      }
      caja.appendChild(par);
    } else {
      caja.appendChild(bloqueCodigo(paso.codigo));
    }
    const probar = el("button", "boton chico celeste", etiqueta || "▶ Probar");
    probar.type = "button";
    caja.appendChild(probar);
    if (paso.lienzo) {
      const c = lienzoNuevo(); c.setAttribute("aria-label", "Dibujo de la tortuga");
      const lienzo = Lienzo.crear(c); lienzo.reiniciar();
      caja.appendChild(c);
      probar.addEventListener("click", async () => {
        probar.disabled = true;
        try {
          const r = await Tortu.ejecutarConPreguntas("/api/tortuga", { codigo: paso.codigo });
          lienzo.usarVista(Lienzo.vistaPara(r.ordenes));
          await lienzo.reproducir(r.ordenes || [], { velocidad: 7 });
        } finally { probar.disabled = false; }
      });
    } else {
      const salida = el("pre", "consola mini");
      salida.appendChild(el("span", "tenue", "Tocá Probar para ver qué muestra."));
      caja.appendChild(salida);
      probar.addEventListener("click", async () => {
        probar.disabled = true;
        try {
          const r = await Tortu.ejecutarConPreguntas("/api/ejecutar", { codigo: paso.codigo });
          salida.textContent = r.error ? r.mensaje : (r.salida || "(no mostró nada)");
        } finally { probar.disabled = false; }
      });
    }
    return caja;
  }

  // ───────── barra de feedback ─────────
  function mostrarPie(clase, texto, principal, alPrincipal, verRespuesta) {
    pie.hidden = false;
    pie.className = `pie-leccion ${clase}`;
    mensaje.textContent = "";
    for (const linea of Array.isArray(texto) ? texto : [texto]) mensaje.appendChild(el("div", "", linea));
    btnPrincipal.textContent = principal;
    btnPrincipal.className = `boton ${clase === "mal" ? "amarillo" : "verde"}`;
    btnPrincipal.disabled = false;
    accion = alPrincipal;
    btnVer.hidden = !verRespuesta;
  }
  function ocultarPie() { pie.hidden = true; accion = null; }

  function pintarProgreso() {
    barra.style.width = `${Math.round((100 * hechos) / pasos.length)}%`;
    contador.textContent = `${Math.min(actual + 1, pasos.length)} / ${pasos.length}`;
    progresoAria.setAttribute("aria-valuenow", String(hechos));
  }

  // ───────── llamadas al servidor ─────────
  const rutaPaso = (i, que) => `/api/lecciones/${datos.id}/pasos/${i}/${que}`;
  const practica = datos.modo === "practica";

  async function comprobar(paso, respuesta) {
    btnPrincipal.disabled = true;
    try {
      const r = practica
        ? await Tortu.api("/api/practica/comprobar", { leccion: paso.leccion, paso: paso.indice, respuesta })
        : await Tortu.api(rutaPaso(paso.indice, "comprobar"), { respuesta });
      Tortu.actualizarEstado(r.estado_juego);
      Tortu.avisos(r.avisos);
      if (r.ok) {
        xpTotal += r.xp || 0;
        if (r.perfecto) perfectos += 1;
        hechos += 1; resultadoFinal = r.leccion;
        pintarProgreso();
        if (paso.tipo === "explicacion") { siguientePaso(); return { ok: true }; }   // leer no necesita aplauso
        Tortu.tocar(r.sube_nivel ? "level_up" : "success");
        const partes = ["✅ ¡Muy bien!"];
        if (r.xp) partes.push(`+${r.xp} XP`);
        mostrarPie("bien", partes, actual + 1 < pasos.length ? "Continuar" : "Terminar", siguientePaso, false);
        return { ok: true };
      }
      Tortu.tocar("error");
      mostrarPie("mal", ["🤔 Todavía no.", r.pista || ""].filter(Boolean), "Reintentar", reintentar, r.puede_ver_respuesta);
      return r;
    } catch (e) {
      mostrarPie("mal", ["😵 No pude comunicarme con TortuScript.", String(e)], "Reintentar", reintentar, false);
      return { ok: false };
    }
  }

  async function verRespuesta() {
    const paso = pasos[actual];
    try {
      const r = practica
        ? await Tortu.api("/api/practica/respuesta", { leccion: paso.leccion, paso: paso.indice })
        : await Tortu.api(rutaPaso(paso.indice, "respuesta"), {});
      Tortu.actualizarEstado(r.estado_juego);
      Tortu.avisos(r.avisos);
      hechos += 1; resultadoFinal = r.leccion;
      pintarProgreso();
      const texto = Array.isArray(r.respuesta) ? r.respuesta.join(paso.tipo === "ordenar" ? "\n" : "  ·  ") : r.respuesta;
      const partes = ["👀 La respuesta era:", texto];
      mostrarPie("info", partes, actual + 1 < pasos.length ? "Continuar" : "Terminar", siguientePaso, false);
      mensaje.lastChild.className = "respuesta-vista";
    } catch (e) {
      mostrarPie("mal", ["Todavía no se puede ver la respuesta. ¡Probá una vez más!"], "Reintentar", reintentar, false);
    }
  }
  btnVer.addEventListener("click", verRespuesta);

  function reintentar() {
    ocultarPie();
    if (typeof reactivar === "function") reactivar();
  }
  let reactivar = null;

  function siguientePaso() {
    actual += 1;
    ocultarPie();
    if (actual >= pasos.length) return pantallaFinal();
    dibujarPaso();
  }

  // ───────── pasos ─────────
  function dibujarPaso() {
    const paso = pasos[actual];
    cont.textContent = "";
    editor = null; leerRespuesta = null; reactivar = null;
    pintarProgreso();
    teclas = null;
    const dibujo = { explicacion, elegir, predecir: elegir, completar, ordenar, escribir }[paso.tipo];
    dibujo(paso);
    cont.classList.remove("entra"); void cont.offsetWidth; cont.classList.add("entra");
    const texto = textoParaLeer(paso);
    if (Tortu.hayVoz && texto) {
      const b = el("button", "boton-voz", "🔊");
      b.type = "button"; b.title = "Escuchar"; b.setAttribute("aria-label", "Escuchar la consigna");
      b.addEventListener("click", () => Tortu.leer(texto));
      cont.appendChild(b);
      if (Tortu.leerSolo()) Tortu.leer(texto); else Tortu.callar();
    }
    if (paso.tipo !== "escribir") { cont.setAttribute("tabindex", "-1"); cont.focus({ preventScroll: true }); }   // que el lector de pantalla empiece acá
  }

  /** Lo que se lee en voz alta de cada paso (el código no: se ve, y leerlo símbolo por símbolo confunde). */
  function textoParaLeer(paso) {
    if (paso.tipo === "explicacion") return paso.texto;
    if (paso.tipo === "elegir" || paso.tipo === "predecir") {
      return `${paso.pregunta}. Opciones: ${paso.opciones.map((o, i) => `${i + 1}, ${o}`).join(". ")}`;
    }
    return [paso.consigna, paso.forma ? `Forma: ${paso.forma}` : "", paso.nota || ""].filter(Boolean).join(". ");
  }

  function explicacion(paso) {
    cont.appendChild(el("h2", "", "💡 Para saber"));
    cont.appendChild(el("p", "texto-grande", paso.texto));
    if (paso.codigo) cont.appendChild(bloqueEjecutable(paso));
    mostrarPie("neutro", "¿Listo?", "Entendido", () => comprobar(paso, true), false);
    btnPrincipal.className = "boton violeta";
  }

  function elegir(paso) {
    cont.appendChild(el("h2", "", paso.tipo === "predecir" ? "🔮 Predecí" : "🎯 Elegí"));
    cont.appendChild(el("p", "texto-grande", paso.pregunta));
    if (paso.codigo) cont.appendChild(paso.lienzo ? bloqueEjecutable(paso, "▶ Ver qué dibuja") : bloqueCodigo(paso.codigo));
    const lista = el("div", "opciones");
    lista.setAttribute("role", "radiogroup");
    let elegida = null;
    const botones = paso.opciones.map((texto, k) => {
      const b = el("button", "opcion-paso", texto);
      b.type = "button"; b.setAttribute("role", "radio"); b.setAttribute("aria-checked", "false");
      b.dataset.n = String(k + 1);                          // el número se dibuja con CSS: no cambia el texto del botón
      b.addEventListener("click", () => {
        elegida = texto;
        botones.forEach((x) => { x.classList.toggle("elegida", x === b); x.setAttribute("aria-checked", String(x === b)); });
        habilitar();
      });
      lista.appendChild(b);
      return b;
    });
    cont.appendChild(lista);
    teclas = (ev) => {                                       // 1, 2, 3... eligen la opción
      const n = Number(ev.key);
      if (n >= 1 && n <= botones.length && !botones[n - 1].disabled) { ev.preventDefault(); botones[n - 1].click(); }
    };
    leerRespuesta = () => elegida;
    reactivar = () => { botones.forEach((x) => x.classList.remove("mala")); habilitar(); };
    function habilitar() { mostrarPie("neutro", elegida ? "¿Estás seguro?" : "Elegí una opción.", "Comprobar", enviar, false); btnPrincipal.disabled = !elegida; btnPrincipal.className = "boton violeta"; }
    async function enviar() {
      const r = await comprobar(paso, elegida);
      if (!r.ok) botones.forEach((x) => x.classList.toggle("mala", x.classList.contains("elegida")));
      else botones.forEach((x) => { x.disabled = true; x.classList.toggle("correcta", x.classList.contains("elegida")); });
    }
    habilitar();
  }

  function completar(paso) {
    cont.appendChild(el("h2", "", "🧩 Completá"));
    cont.appendChild(el("p", "texto-grande", paso.consigna));
    const objetivoC = cajaObjetivo(paso); if (objetivoC) cont.appendChild(objetivoC);
    const partes = paso.codigo.split(HUECO);
    const relleno = new Array(partes.length - 1).fill(null);     // ficha (índice) de cada hueco
    const pre = el("pre", "codigo-paso completar");
    const huecos = [];
    partes.forEach((trozo, i) => {
      pre.appendChild(document.createTextNode(trozo));
      if (i < partes.length - 1) {
        const h = el("button", "hueco"); h.type = "button";
        h.addEventListener("click", () => { if (relleno[i] !== null) { relleno[i] = null; pintar(); } });
        huecos.push(h); pre.appendChild(h);
      }
    });
    cont.appendChild(pre);
    const zona = el("div", "fichas-paso");
    const fichas = paso.fichas.map((texto, k) => {
      const f = el("button", "ficha-paso", texto); f.type = "button";
      f.addEventListener("click", () => {
        const libre = relleno.indexOf(null);
        if (libre === -1 || relleno.includes(k)) return;
        relleno[libre] = k; pintar();
      });
      zona.appendChild(f); return f;
    });
    cont.appendChild(zona);
    function pintar() {
      huecos.forEach((h, i) => {
        h.textContent = relleno[i] === null ? "     " : paso.fichas[relleno[i]];
        h.classList.toggle("lleno", relleno[i] !== null); h.classList.remove("mala");
      });
      fichas.forEach((f, k) => { f.disabled = relleno.includes(k); });
      const completo = relleno.every((x) => x !== null);
      mostrarPie("neutro", completo ? "¿Está bien así?" : "Tocá las fichas para llenar los huecos.", "Comprobar", enviar, false);
      btnPrincipal.disabled = !completo; btnPrincipal.className = "boton violeta";
    }
    reactivar = pintar;
    async function enviar() {
      const r = await comprobar(paso, relleno.map((k) => paso.fichas[k]));
      if (r.ok) { huecos.forEach((h) => { h.disabled = true; h.classList.add("correcta"); }); fichas.forEach((f) => { f.disabled = true; }); }
      else (r.malos || []).forEach((i) => huecos[i].classList.add("mala"));
    }
    pintar();
  }

  function ordenar(paso) {
    cont.appendChild(el("h2", "", "🔢 Ordená"));
    cont.appendChild(el("p", "texto-grande", paso.consigna));
    const objetivoO = cajaObjetivo(paso); if (objetivoO) cont.appendChild(objetivoO);
    const armado = [];                                           // índices de paso.lineas, en el orden elegido
    cont.appendChild(el("div", "rotulo-zona", "Tu programa:"));
    const zonaArmado = el("div", "zona-ordenar armado");
    cont.appendChild(zonaArmado);
    cont.appendChild(el("div", "rotulo-zona", "Líneas para ubicar:"));
    const zonaPool = el("div", "zona-ordenar pool");
    cont.appendChild(zonaPool);
    let malos = [];
    function pintar() {
      zonaArmado.textContent = ""; zonaPool.textContent = "";
      armado.forEach((k, pos) => {
        const b = el("button", "linea-paso"); b.type = "button"; b.textContent = paso.lineas[k];
        if (malos.includes(pos)) b.classList.add("mala");
        b.addEventListener("click", () => { armado.splice(pos, 1); malos = []; pintar(); });
        zonaArmado.appendChild(b);
      });
      if (!armado.length) zonaArmado.appendChild(el("span", "tenue", "Tocá una línea de abajo para empezar."));
      paso.lineas.forEach((texto, k) => {
        if (armado.includes(k)) return;
        const b = el("button", "linea-paso"); b.type = "button"; b.textContent = texto;
        b.addEventListener("click", () => { armado.push(k); malos = []; pintar(); });
        zonaPool.appendChild(b);
      });
      const completo = armado.length === paso.lineas.length;
      mostrarPie("neutro", completo ? "¿Está bien así?" : "Ubicá todas las líneas.", "Comprobar", enviar, false);
      btnPrincipal.disabled = !completo; btnPrincipal.className = "boton violeta";
    }
    reactivar = pintar;
    async function enviar() {
      const r = await comprobar(paso, armado.map((k) => paso.lineas[k]));
      if (r.ok) zonaArmado.querySelectorAll(".linea-paso").forEach((b) => { b.disabled = true; b.classList.add("correcta"); });
      else { malos = r.malos || []; zonaArmado.querySelectorAll(".linea-paso").forEach((b, i) => b.classList.toggle("mala", malos.includes(i))); }
    }
    pintar();
  }

  function escribir(paso) {
    const dibuja = Boolean(paso.tortuga);
    const python = paso.lenguaje === "python";
    cont.appendChild(el("h2", "", "⌨️ Escribí"));
    cont.appendChild(el("p", "texto-grande", paso.consigna));
    if (paso.forma) { const f = el("div", "forma-paso"); f.appendChild(el("span", "tenue", "Forma: ")); f.appendChild(el("code", "", paso.forma)); cont.appendChild(f); }
    if (paso.nota) cont.appendChild(el("p", "tenue", paso.nota));

    const zonaEditor = el("div", "columna-editor");
    const area = el("textarea"); area.id = "editor-paso";
    zonaEditor.appendChild(area);
    let lienzo = null;
    if (dibuja) {
      const duo = el("div", "duo-tortuga");
      const derecha = el("div", "columna-lienzos");
      var objetivo = cajaObjetivo(paso);
      if (objetivo) derecha.appendChild(objetivo);
      const propio = el("div", "objetivo-caja");
      propio.appendChild(el("div", "rotulo-zona", paso.laberinto ? "🧭 Llevá la tortuga hasta la 🏁:" : "🖼️ Tu dibujo:"));
      const c = lienzoNuevo();
      c.setAttribute("aria-label", paso.laberinto ? "Laberinto: la tortuga tiene que llegar a la bandera sin tocar las paredes" : "Tu dibujo");
      propio.appendChild(c); derecha.appendChild(propio);
      lienzo = Lienzo.crear(c);
      if (paso.laberinto) { lienzo.usarLaberinto(paso.laberinto); lienzo.usarVista(Lienzo.vistaLaberinto(paso.laberinto)); }
      if (paso.objetivo) lienzo.usarVista(Lienzo.vistaPara(paso.objetivo));
      lienzo.reiniciar();
      duo.append(zonaEditor, derecha);
      cont.appendChild(duo);
    } else {
      cont.appendChild(zonaEditor);
    }
    editor = CodeMirror.fromTextArea(area, {
      mode: python ? "python" : "tortuscript", lineNumbers: true, indentUnit: 4, tabSize: 4, indentWithTabs: false, autofocus: true,
      extraKeys: { "Ctrl-Enter": () => ejecutar(), "Cmd-Enter": () => ejecutar(), Tab: (cm) => cm.replaceSelection("    "),
                   Esc: () => run.focus() },
    });
    editor.setSize(null, dibuja ? 260 : 180);
    if (paso.inicial) {                                    // proyectos guiados: se sigue desde lo que ya estaba armado
      editor.setValue(paso.inicial + "\n");
      editor.setCursor(editor.lineCount(), 0);
    }
    const acciones = el("div", "acciones");
    const run = el("button", "boton verde", dibuja ? "▶ Dibujar" : "▶ Ejecutar"); run.type = "button";
    const pista = el("button", "boton amarillo", "💡 Pista (1/3)"); pista.type = "button";
    acciones.append(run, pista);
    zonaEditor.appendChild(acciones);
    zonaEditor.appendChild(el("p", "tenue ayuda-teclado", "Con el teclado: Tab escribe espacios · Esc sale del editor · Ctrl+Enter ejecuta."));
    const salida = el("pre", "consola mini");
    salida.appendChild(el("span", "tenue", dibuja ? "Si tu programa muestra algo, aparece acá." : "Acá vas a ver lo que muestra tu programa."));
    const cajaPista = el("div", "pista-caja");
    cont.append(salida, cajaPista);
    ocultarPie();

    let lineaChoque = null;                                  // laberinto: línea marcada donde chocó
    async function ejecutar() {
      if (run.disabled) return;
      run.disabled = true; ocultarPie();
      if (lineaChoque !== null) { editor.removeLineClass(lineaChoque, "background", "linea-actual"); lineaChoque = null; }
      try {
        const r = await Tortu.ejecutarConPreguntas(rutaPaso(paso.indice, "evaluar"), { codigo: editor.getValue() });
        salida.textContent = r.cancelado ? "" : (r.salida || "");
        if (!r.salida) {
          salida.textContent = "";
          const sinSalida = dibuja ? "(tu programa no mostró texto, ¡solo dibujó!)"
            : (r.error ? "(tu programa no llegó a mostrar nada)" : "(tu programa no mostró nada)");
          salida.appendChild(el("span", "tenue", sinSalida));
        }
        Tortu.actualizarEstado(r.estado_juego);
        Tortu.avisos(r.avisos);
        if (r.cancelado) return;
        if (dibuja) {
          const vista = paso.laberinto ? Lienzo.vistaLaberinto(paso.laberinto)
            : Lienzo.vistaPara(paso.objetivo, r.ordenes);                    // que entren los dos dibujos
          lienzo.usarVista(vista);
          if (objetivo && objetivo.lienzo) objetivo.lienzo.usarVista(vista);
          await lienzo.reproducir(r.ordenes || [], { velocidad: 9 });
        }
        const ev = r.evaluacion || {};
        if (r.error) { Tortu.tocar("error"); mostrarPie("mal", ["🔧 Hay algo para arreglar", r.mensaje], "Reintentar", reintentar, false); return; }
        if (ev.estado === "correcto") {
          const p = r.premio || {};
          hechos += 1; if (p.estrellas === 3) perfectos += 1;
          xpTotal += p.mejora ? p.xp : 0; resultadoFinal = r.leccion || resultadoFinal;
          pintarProgreso(); run.disabled = true; pista.disabled = true; editor.setOption("readOnly", true);
          Tortu.tocar(p.sube_nivel ? "level_up" : "success");
          const partes = ["✅ ¡Correcto!"];
          if (p.mejora) partes.push(`${"⭐".repeat(p.estrellas)}${"☆".repeat(3 - p.estrellas)}  +${p.xp} XP`);
          mostrarPie("bien", partes, actual + 1 < pasos.length ? "Continuar" : "Terminar", siguientePaso, false);
          return;
        }
        Tortu.tocar("error");
        if (ev.estado === "choque" && ev.linea) {
          lineaChoque = ev.linea - 1; editor.addLineClass(lineaChoque, "background", "linea-actual");
        }
        const parecido = ev.similitud !== undefined ? `Se parece un ${Math.round(100 * ev.similitud)}% al objetivo.` : "";
        const texto = {
          falta_preguntar: ["✏️ Este ejercicio pide usar preguntar."],
          sin_salida: ["🤫 Tu programa no mostró nada.", "Recordá usar mostrar (o print, si escribís Python)."],
          sin_dibujo: ["🤫 Tu programa no dibujó nada.", "Usá avanzar para que la tortuga deje una línea."],
          choque: [`💥 ¡La tortuga chocó con una pared en la línea ${ev.linea}!`, "Fijate cuánto avanza o para qué lado gira en esa línea."],
          no_llega: ["🧭 La tortuga no llegó a la 🏁.", "Tiene que terminar sobre la bandera. ¿Le falta un tramo?"],
          falta_usar: [`🎉 ¡Llegó! Pero este laberinto hay que resolverlo con ${(ev.usar || []).join(", ")}.`,
                       "Buscá lo que se repite y escribilo una sola vez."],
          incorrecto: dibuja ? ["🤔 ¡Casi! Tu dibujo no es igual al objetivo.", parecido, "Compará los tamaños, los giros y los colores."]
                             : ["🤔 ¡Casi! Tu programa corre, pero muestra otra cosa.", `Se esperaba:\n${ev.esperado}`],
        }[ev.estado] || ["Revisalo otra vez."];
        mostrarPie("mal", texto.filter(Boolean), "Reintentar", () => { ocultarPie(); editor.focus(); }, false);
      } catch (e) {
        mostrarPie("mal", ["😵 No pude comunicarme con TortuScript.", String(e)], "Reintentar", () => ocultarPie(), false);
      } finally { if (!editor.getOption("readOnly")) run.disabled = false; }
    }
    run.addEventListener("click", ejecutar);
    pista.addEventListener("click", async () => {
      const r = await Tortu.api(rutaPaso(paso.indice, "pista"), {});
      cajaPista.textContent = "";
      const caja = el("div", "veredicto info");
      caja.appendChild(el("h3", "", `💡 Pista ${r.nivel}: ${r.titulo}`));
      for (const clave of ["texto", "codigo", "python"]) {
        if (!r[clave]) continue;
        if (clave === "python") caja.appendChild(el("div", "", "🐍 En Python:"));
        caja.appendChild(el(clave === "texto" ? "div" : "pre", "", r[clave]));
      }
      cajaPista.appendChild(caja);
      pista.textContent = r.nivel >= 3 ? "💡 Pista (vista)" : `💡 Pista (${r.nivel + 1}/3)`;
      if (r.nivel >= 3) pista.disabled = true;
    });
  }

  // ───────── final ─────────
  function pantallaFinal() {
    cont.textContent = "";
    hechos = pasos.length; pintarProgreso();
    const perfecta = practica ? perfectos === pasos.length : (resultadoFinal ? resultadoFinal.perfecta : perfectos === pasos.length);
    cont.appendChild(el("div", "mascota gran", perfecta ? "🏆" : "🎉"));
    cont.appendChild(el("h2", "centrado", practica ? "¡Práctica terminada!" : (perfecta ? "¡Lección perfecta!" : "¡Lección completada!")));
    cont.appendChild(el("p", "tenue centrado", practica
      ? (perfecta ? "Todo al primer intento: esas tarjetas vuelven más tarde." : "Lo que falló vuelve mañana, para que se quede.")
      : (perfecta ? "Todo salió al primer intento. ¡Sos un crack!" : "Podés repetirla cuando quieras para lograr la lección perfecta.")));
    const stats = el("div", "mini-stats");
    for (const [valor, rotulo] of [[`${perfectos}/${pasos.length}`, "al primer intento"], [`+${xpTotal}`, practica ? "XP de práctica" : "XP en esta lección"]]) {
      const d = el("div"); d.appendChild(el("b", "", valor)); d.appendChild(el("span", "tenue", rotulo)); stats.appendChild(d);
    }
    cont.appendChild(stats);
    const acciones = el("div", "acciones"); acciones.style.justifyContent = "center";
    const sig = !practica && resultadoFinal && resultadoFinal.siguiente;
    if (sig) {
      const a = el("a", "boton verde grande", `▶ ${resultadoFinal.titulo_siguiente}`);
      a.href = `/leccion/${sig}`; acciones.appendChild(a);
    }
    const volver = el("a", "boton", "🏠 Volver al inicio"); volver.href = "/"; acciones.appendChild(volver);
    cont.appendChild(acciones);
    Tortu.celebrar(perfecta);
    Tortu.tocar("success");
  }

  btnPrincipal.addEventListener("click", () => { if (accion) accion(); });
  document.addEventListener("keydown", (ev) => {
    if (!teclas || ev.ctrlKey || ev.metaKey || ev.altKey) return;
    if (["TEXTAREA", "INPUT"].includes(document.activeElement.tagName) || !document.getElementById("modal-pregunta").hidden) return;
    teclas(ev);
  });
  document.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter" && !ev.shiftKey && !ev.ctrlKey && accion && !btnPrincipal.disabled
        && !["TEXTAREA", "INPUT", "BUTTON", "A"].includes(document.activeElement.tagName)
        && document.getElementById("modal-pregunta").hidden) {
      ev.preventDefault(); accion();
    }
  });
  dibujarPaso();
})();
