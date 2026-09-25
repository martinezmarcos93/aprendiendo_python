/* Resumen: cambiar la meta diaria. */
"use strict";
(() => {
  for (const b of document.querySelectorAll("[data-meta]")) {
    b.addEventListener("click", async () => {
      try {
        const r = await Tortu.api("/api/config", { meta_min: Number(b.dataset.meta) });
        if (r.ok) location.reload();
      } catch (e) { console.warn(e); }
    });
  }
})();
