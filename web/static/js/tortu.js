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
    if (!r.ok) throw new Error(`Error ${r.status} en ${ruta}`);
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

  // ───────── barra superior ─────────
  function actualizarEstado(e) {
    if (!e) return;
    document.getElementById("e-racha").textContent = e.racha;
    document.getElementById("e-nivel").textContent = `${e.titulo} · Nv.${e.nivel}`;
    document.getElementById("e-xp").textContent = `${e.xp} XP`;
    document.getElementById("e-barra").style.width = `${Math.round(100 * e.xp_actual / e.xp_max)}%`;
  }

  function celebrar(grande) {
    if (typeof confetti !== "function") return;
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

  return { api, crearEditores, ejecutarConPreguntas, mostrarConsola, veredicto,
           limpiarResultado, actualizarEstado, celebrar };
})();
