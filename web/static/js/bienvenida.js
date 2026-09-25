/* Bienvenida: nombre → experiencia → meta diaria. Un POST al final. */
"use strict";
(() => {
  const paso = (n) => document.querySelector(`.paso-bv[data-paso="${n}"]`);
  const nombre = document.getElementById("bv-nombre");
  const error = document.getElementById("bv-error");
  const errorFinal = document.getElementById("bv-error-final");
  const respuestas = { experiencia: null, meta_min: 10 };

  function ir(n) {
    for (const i of [1, 2, 3]) paso(i).hidden = i !== n;
    document.getElementById("bv-barra").style.width = `${Math.round(100 * n / 3)}%`;
    document.getElementById("bv-contador").textContent = `${n} / 3`;
    document.getElementById("bv-progreso").setAttribute("aria-valuenow", String(n));
    const foco = paso(n).querySelector("input, .opcion-paso[aria-checked='true'], .opcion-paso");
    if (foco) foco.focus();
  }

  // opciones tipo radio: una sola elegida por grupo
  for (const grupo of document.querySelectorAll('[role="radiogroup"]')) {
    grupo.addEventListener("click", (ev) => {
      const b = ev.target.closest(".opcion-paso");
      if (!b) return;
      for (const x of grupo.querySelectorAll(".opcion-paso")) {
        x.classList.toggle("elegida", x === b);
        x.setAttribute("aria-checked", String(x === b));
      }
      if (paso(2).contains(b)) { respuestas.experiencia = b.dataset.valor; document.getElementById("bv-sig-2").disabled = false; }
      else respuestas.meta_min = Number(b.dataset.valor);
    });
  }
  document.querySelector('[data-valor="10"]').classList.add("elegida");

  document.getElementById("bv-sig-1").addEventListener("click", () => {
    error.textContent = "";
    if (nombre.value.trim() && !/[A-Za-z0-9ñáéíóúüÑÁÉÍÓÚÜ]/.test(nombre.value)) {
      error.textContent = "Usá letras o números para el nombre."; return;
    }
    ir(2);
  });
  nombre.addEventListener("keydown", (ev) => { if (ev.key === "Enter") document.getElementById("bv-sig-1").click(); });
  document.getElementById("bv-sig-2").addEventListener("click", () => ir(3));

  document.getElementById("bv-empezar").addEventListener("click", async () => {
    const boton = document.getElementById("bv-empezar");
    boton.disabled = true; errorFinal.textContent = "";
    try {
      const r = await Tortu.api("/api/onboarding", {
        nombre: nombre.value.trim(), experiencia: respuestas.experiencia, meta_min: respuestas.meta_min,
      });
      if (r.ok) location.href = "/";
    } catch (e) {
      errorFinal.textContent = "No pude guardar tus respuestas. Revisá el nombre y probá de nuevo.";
      boton.disabled = false; ir(1);
    }
  });
  nombre.focus();
})();
