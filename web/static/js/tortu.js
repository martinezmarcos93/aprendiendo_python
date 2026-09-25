/* TortuScript — funciones compartidas por todas las páginas. */
"use strict";

const Tortu = (() => {
  // ───────── API (con el token de esta sesión) ─────────
  async function api(ruta, datos) {
    const r = await fetch(ruta, {
      method: datos === undefined ? "GET" : "POST",
      headers: { "Content-Type": "application/json", "X-Tortu-Token": window.TORTU.token },
      body: datos === undefined ? undefined : JSON.stringify(datos),
    });
    if (!r.ok) {
      const error = new Error(`Error ${r.status} en ${ruta}`);
      error.estado = r.status;
      try { error.datos = await r.json(); } catch (e) { error.datos = null; }   // el servidor explica lo que se puede corregir
      throw error;
    }
    return r.json();
  }

  // ───────── resaltado de TortuScript (acepta tildes y mayúsculas) ─────────
  const PALABRAS = "mostrar|mostrá|preguntar|funci[oó]n|devolver|repetir|veces|mientras|sino|si|para|en|es|clase|hereda|de|y|o|no";
  const TORTUGA = "avanzar|retroceder|girar_der|girar_izq|color|bajar_lapiz|subir_lapiz";
  CodeMirror.defineSimpleMode("tortuscript", {
    start: [
      { regex: /#.*/, token: "comment" },
      { regex: /f?"(?:[^\\"]|\\.)*"?|f?'(?:[^\\']|\\.)*'?/, token: "string" },
      { regex: new RegExp(`(?:${PALABRAS})(?![\\wáéíóúñ])`, "i"), token: "keyword" },
      { regex: /(?:verdadero|falso)(?![\wáéíóúñ])/i, token: "atom" },
      { regex: new RegExp(`(?:${TORTUGA})(?![\\wáéíóúñ])`, "i"), token: "builtin" },
      { regex: /\d+(?:\.\d+)?/, token: "number" },
      { regex: /[-+*/%=<>!]+/, token: "operator" },
      { regex: /[A-Za-z_áéíóúñÁÉÍÓÚÑ][\wáéíóúñÁÉÍÓÚÑ]*/, token: "variable" },
    ],
    meta: { lineComment: "#" },
  });

  function crearEditores(alEjecutar) {
    const editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
      mode: "tortuscript", lineNumbers: true, indentUnit: 4, tabSize: 4,
      indentWithTabs: false, autofocus: true,
      extraKeys: {
        "Ctrl-Enter": () => alEjecutar(), "Cmd-Enter": () => alEjecutar(),
        Tab: (cm) => cm.replaceSelection("    "),
        Esc: () => { const b = document.getElementById("btn-ejecutar"); if (b) b.focus(); },   // sale del editor con el teclado
      },
    });
    const campoPython = document.getElementById("python");
    const python = campoPython && CodeMirror.fromTextArea(campoPython, {
      mode: "python", lineNumbers: true, readOnly: true,
    });
    let espera = null;
    if (python) editor.on("change", () => {
      clearTimeout(espera);
      espera = setTimeout(async () => {
        try { python.setValue((await api("/api/traducir", { codigo: editor.getValue() })).python); }
        catch (e) { console.warn(e); }
      }, 250);
    });
    // ?codigo=... precarga el editor (lo usa "Probarlo" de la Referencia)
    const precarga = new URLSearchParams(location.search).get("codigo");
    if (precarga) editor.setValue(precarga.slice(0, 5000));
    return { editor, python };
  }

  // ───────── ventana de preguntar() ─────────
  function pedirRespuesta(pregunta) {
    const modal = document.getElementById("modal-pregunta");
    const campo = document.getElementById("mp-campo");
    document.getElementById("mp-texto").textContent = (pregunta || "").trim() || "Escribí un valor:";
    campo.value = "";
    modal.hidden = false;
    setTimeout(() => campo.focus(), 30);
    return new Promise((resolver) => {
      const cerrar = (valor) => {
        modal.hidden = true;
        campo.removeEventListener("keydown", tecla);
        ok.removeEventListener("click", aceptar);
        cancelar.removeEventListener("click", anular);
        resolver(valor);
      };
      const aceptar = () => cerrar(campo.value);
      const anular = () => cerrar(null);
      // key "Enter" cubre el Enter normal y el del teclado numérico
      const tecla = (ev) => {
        if (ev.key === "Enter") { ev.preventDefault(); aceptar(); }
        else if (ev.key === "Escape") { ev.preventDefault(); anular(); }
      };
      const ok = document.getElementById("mp-ok");
      const cancelar = document.getElementById("mp-cancelar");
      campo.addEventListener("keydown", tecla);
      ok.addEventListener("click", aceptar);
      cancelar.addEventListener("click", anular);
    });
  }

  /** Ejecuta en el servidor; si el programa pregunta algo, muestra la ventana y
   *  vuelve a ejecutar con las respuestas acumuladas. */
  async function ejecutarConPreguntas(ruta, datos) {
    const entradas = [];
    for (let vuelta = 0; vuelta < 30; vuelta++) {
      const r = await api(ruta, { ...datos, entradas });
      if (r.pregunta === null || r.pregunta === undefined || r.error) return r;
      const respuesta = await pedirRespuesta(r.pregunta);
      if (respuesta === null) return { ...r, cancelado: true };
      entradas.push(respuesta);
    }
    throw new Error("Demasiadas preguntas seguidas");
  }

  // ───────── pintar resultados (siempre como TEXTO, nunca HTML) ─────────
  function mostrarConsola(r) {
    const consola = document.getElementById("consola");
    consola.textContent = "";
    if (!r.salida) {
      const s = document.createElement("span");
      s.className = "tenue";
      s.textContent = r.error ? "(tu programa no llegó a mostrar nada)" : "(tu programa no mostró nada)";
      consola.appendChild(s);
    } else {
      consola.textContent = r.salida;
    }
  }

  function veredicto(clase, titulo, partes = []) {
    const caja = document.getElementById("veredicto");
    caja.textContent = "";
    const div = document.createElement("div");
    div.className = `veredicto ${clase}`;
    const h = document.createElement("h3");
    h.textContent = titulo;
    div.appendChild(h);
    for (const [tipo, texto] of partes) {
      const el = document.createElement(tipo === "codigo" ? "pre" : "div");
      el.className = tipo === "premio" ? "premio" : tipo === "mensaje" ? "mensaje" : "";
      el.textContent = texto;
      div.appendChild(el);
    }
    caja.appendChild(div);
    div.scrollIntoView({ behavior: "smooth", block: "nearest" });
    return div;
  }

  function limpiarResultado() {
    document.getElementById("veredicto").textContent = "";
  }

  // ───────── sonidos (WebAudio; mismas melodías que la app de escritorio) ─────────
  const MELODIAS = {
    success: [[523, 100], [659, 100], [784, 150], [1046, 300]],
    error: [[300, 200], [200, 400]],
    level_up: [[440, 150], [554, 150], [659, 150], [880, 400]],
  };
  const sonido = {
    activo: (() => { try { return localStorage.getItem("tortu-sonido") !== "no"; } catch (e) { return true; } })(),
    ctx: null,
  };
  function tocar(tipo) {
    if (!sonido.activo || !MELODIAS[tipo]) return;
    try {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return;
      sonido.ctx = sonido.ctx || new AC();
      if (sonido.ctx.state === "suspended") sonido.ctx.resume();
      let t = sonido.ctx.currentTime;
      for (const [hz, ms] of MELODIAS[tipo]) {
        const osc = sonido.ctx.createOscillator(), vol = sonido.ctx.createGain();
        osc.type = tipo === "error" ? "sawtooth" : "triangle";
        osc.frequency.value = hz;
        vol.gain.setValueAtTime(0.0001, t);
        vol.gain.exponentialRampToValueAtTime(0.18, t + 0.01);
        vol.gain.exponentialRampToValueAtTime(0.0001, t + ms / 1000);
        osc.connect(vol).connect(sonido.ctx.destination);
        osc.start(t); osc.stop(t + ms / 1000 + 0.02);
        t += ms / 1000;
      }
    } catch (e) { console.warn(e); }
  }
  function pintarSonido() {
    const b = document.getElementById("btn-sonido");
    if (!b) return;
    b.textContent = sonido.activo ? "🔊" : "🔇";
    b.setAttribute("aria-pressed", String(sonido.activo));
    b.title = sonido.activo ? "Sonido activado (tocá para silenciar)" : "Sonido silenciado (tocá para activar)";
  }
  document.getElementById("btn-sonido").addEventListener("click", () => {
    sonido.activo = !sonido.activo;
    try { localStorage.setItem("tortu-sonido", sonido.activo ? "si" : "no"); } catch (e) { /* sin almacenamiento */ }
    pintarSonido();
    tocar("success");
  });
  pintarSonido();

  // ───────── avisos (logros, congelador, meta, liga) ─────────
  function textoAviso(a) {
    switch (a.tipo) {
      case "logro": return [`${a.icono} ¡Nuevo logro: ${a.titulo}!`, a.descripcion];
      case "congelador_ganado": return ["❄️ ¡Ganaste un congelador de racha!", "Te protege si un día no podés programar."];
      case "congelador_usado": return ["❄️ Tu congelador salvó tu racha", `Ya llevás ${a.racha} días seguidos.`];
      case "meta_cumplida": return ["🎯 ¡Cumpliste la meta de hoy!", `${a.xp} XP en el día.`];
      case "mensaje": return [a.titulo, a.detalle];
      case "liga_asciende": return [`${a.icono} ¡Subiste a la liga de ${a.liga}!`, `Terminaste la semana en el puesto ${a.puesto}.`];
      default: return null;
    }
  }
  function avisos(lista) {
    if (!lista || !lista.length) return;
    let caja = document.getElementById("avisos");
    if (!caja) {
      caja = document.createElement("div");
      caja.id = "avisos"; caja.className = "avisos"; caja.setAttribute("aria-live", "polite");
      document.body.appendChild(caja);
    }
    let festejar = false;
    for (const a of lista) {
      const t = textoAviso(a);
      if (!t) continue;
      festejar = festejar || ["logro", "liga_asciende", "congelador_ganado"].includes(a.tipo);
      const div = document.createElement("div");
      div.className = `aviso ${a.tipo}`;
      const h = document.createElement("b"); h.textContent = t[0];
      const p = document.createElement("span"); p.textContent = t[1] || "";
      div.append(h, p);
      caja.appendChild(div);
      setTimeout(() => { div.classList.add("saliendo"); setTimeout(() => div.remove(), 400); }, 6500);
    }
    if (festejar) celebrar(false);
  }

  // ───────── barra superior ─────────
  function actualizarEstado(e) {
    if (!e) return;
    document.getElementById("e-racha").textContent = e.racha;
    const cong = document.getElementById("e-cong");
    if (cong) { cong.textContent = e.congeladores ? ` ❄${e.congeladores}` : ""; }
    document.getElementById("e-nivel").textContent = `${e.titulo} · Nv.${e.nivel}`;
    document.getElementById("e-xp").textContent = `${e.xp} XP`;
    document.getElementById("e-barra").style.width = `${Math.round(100 * e.xp_actual / e.xp_max)}%`;
  }

  function celebrar(grande) {
    if (typeof confetti !== "function") return;
    if (document.documentElement.dataset.movimiento === "reducido") return;
    confetti({ particleCount: grande ? 180 : 90, spread: grande ? 100 : 70, origin: { y: 0.7 } });
  }

  // ───────── perfiles ─────────
  async function abrirPerfiles() {
    const modal = document.getElementById("modal-perfil");
    const lista = document.getElementById("pf-lista");
    const campo = document.getElementById("pf-campo");
    const error = document.getElementById("pf-error");
    const datos = await api("/api/perfiles");
    lista.textContent = "";
    error.textContent = "";
    campo.value = "";
    for (const p of datos.perfiles) {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "boton chico" + (p === datos.actual ? " violeta" : "");
      b.textContent = p;
      b.addEventListener("click", () => cambiar(p));
      lista.appendChild(b);
    }
    modal.hidden = false;
    campo.focus();
    async function cambiar(nombre) {
      try {
        const r = await api("/api/perfil", { nombre });
        if (r.ok) location.reload();
      } catch (e) { error.textContent = "Usá letras o números para el nombre."; }
    }
    document.getElementById("pf-ok").onclick = () => campo.value.trim() && cambiar(campo.value);
    document.getElementById("pf-cancelar").onclick = () => { modal.hidden = true; };
    campo.onkeydown = (ev) => {
      if (ev.key === "Enter" && campo.value.trim()) cambiar(campo.value);
      if (ev.key === "Escape") modal.hidden = true;
    };
  }
  document.getElementById("btn-perfil").addEventListener("click", abrirPerfiles);
  avisos(window.TORTU.avisos);                 // lo que quedó pendiente desde la última vez

  // ───────── voz (Web Speech: usa las voces del sistema, sin internet) ─────────
  const hayVoz = "speechSynthesis" in window && typeof SpeechSynthesisUtterance === "function";
  const VELOCIDADES = { lenta: 0.8, normal: 1, rapida: 1.25 };
  function vozEspanola() {
    const voces = hayVoz ? speechSynthesis.getVoices() : [];
    return voces.find((v) => /^es[-_]AR/i.test(v.lang)) || voces.find((v) => /^es/i.test(v.lang)) || null;
  }
  /** Lee un texto en voz alta. Devuelve false si el navegador no tiene voz. */
  function leer(texto) {
    if (!hayVoz || !texto) return false;
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(texto);
    u.lang = "es-AR";
    const v = vozEspanola();
    if (v) u.voice = v;
    u.rate = VELOCIDADES[document.documentElement.dataset.velocidad] || 1;
    speechSynthesis.speak(u);
    return true;
  }
  function callar() { if (hayVoz) speechSynthesis.cancel(); }
  const leerSolo = () => document.documentElement.dataset.voz === "si";

  // ───────── ajustes de accesibilidad ─────────
  function iniciarAjustes() {
    const modal = document.getElementById("modal-ajustes");
    const abrir = document.getElementById("btn-ajustes");
    const aviso = document.getElementById("aj-aviso");
    const cerrar = () => { modal.hidden = true; callar(); abrir.focus(); };
    abrir.addEventListener("click", () => {
      aviso.textContent = hayVoz && !vozEspanola()
        ? "Este navegador no tiene una voz en español: se va a usar la que haya." : (hayVoz ? "" : "Este navegador no puede leer en voz alta.");
      modal.hidden = false;
      modal.querySelector(".opcion-ajuste[aria-checked='true']").focus();
    });
    document.getElementById("aj-cerrar").addEventListener("click", cerrar);
    document.getElementById("aj-probar").addEventListener("click", () => {
      if (!leer("Hola, esta es mi voz. Así te voy a leer las consignas.")) aviso.textContent = "Este navegador no puede leer en voz alta.";
    });
    modal.addEventListener("keydown", (ev) => { if (ev.key === "Escape") { ev.preventDefault(); cerrar(); } });
    for (const grupo of modal.querySelectorAll(".ajuste")) {
      grupo.addEventListener("click", async (ev) => {
        const b = ev.target.closest(".opcion-ajuste");
        if (!b) return;
        const clave = grupo.dataset.ajuste, valor = b.dataset.valor;
        document.documentElement.dataset[clave] = valor;                       // se ve al instante
        for (const x of grupo.querySelectorAll(".opcion-ajuste")) x.setAttribute("aria-checked", String(x === b));
        try { await api("/api/ajustes", { [clave]: valor }); }
        catch (e) { aviso.textContent = "No pude guardar el ajuste (se ve, pero no se recuerda)."; }
      });
    }
  }
  iniciarAjustes();

  // El foco se queda adentro de la ventana abierta (con Tab y Shift+Tab)
  document.addEventListener("keydown", (ev) => {
    if (ev.key !== "Tab") return;
    const abierta = document.querySelector(".modal:not([hidden])");
    if (!abierta) return;
    const focos = [...abierta.querySelectorAll("button:not([disabled]), input, a[href], [tabindex]:not([tabindex='-1'])")]
      .filter((e) => e.offsetParent !== null);
    if (!focos.length) return;
    const primero = focos[0], ultimo = focos[focos.length - 1];
    if (ev.shiftKey && document.activeElement === primero) { ev.preventDefault(); ultimo.focus(); }
    else if (!ev.shiftKey && document.activeElement === ultimo) { ev.preventDefault(); primero.focus(); }
    else if (!abierta.contains(document.activeElement)) { ev.preventDefault(); primero.focus(); }
  });

  return { api, leer, callar, leerSolo, hayVoz, crearEditores, ejecutarConPreguntas, mostrarConsola, veredicto,
           limpiarResultado, actualizarEstado, celebrar, tocar, avisos };
})();
