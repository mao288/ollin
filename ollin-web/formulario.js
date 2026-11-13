/* Formulario de bandas: contadores de caracteres, borrador local y envío a Netlify Forms */
(function () {
  "use strict";
  var form = document.getElementById("bandas-form");
  if (!form) return;
  var KEY = "ollin-bandas-borrador";

  // Contadores para los campos con límite
  Array.prototype.forEach.call(form.querySelectorAll("[data-count]"), function (el) {
    var out = form.querySelector('.ff__count[data-for="' + el.id + '"]');
    var max = parseInt(el.getAttribute("maxlength"), 10);
    function upd() {
      if (!out) return;
      var n = el.value.length;
      out.textContent = n + " de " + max;
      out.classList.toggle("is-near", n > max * 0.9);
    }
    el.addEventListener("input", upd); upd();
  });

  // Borrador: si cierran la página, no pierden lo escrito (solo en este navegador)
  function save() {
    try {
      var data = {};
      new FormData(form).forEach(function (v, k) { if (k !== "form-name" && k !== "bot-field") data[k] = v; });
      localStorage.setItem(KEY, JSON.stringify(data));
    } catch (e) {}
  }
  function restore() {
    try {
      var data = JSON.parse(localStorage.getItem(KEY) || "{}");
      Object.keys(data).forEach(function (k) {
        var el = form.elements[k];
        if (!el) return;
        if (el.type === "checkbox") el.checked = data[k] === el.value;
        else el.value = data[k];
        el.dispatchEvent(new Event("input"));
      });
    } catch (e) {}
  }
  restore();
  form.addEventListener("input", save);

  var status = document.getElementById("bandas-status");
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (!form.checkValidity()) { form.reportValidity(); return; }
    var btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;
    status.className = "form__status";
    status.textContent = "Enviando…";
    var body = new URLSearchParams(new FormData(form)).toString();
    fetch("/", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: body })
      .then(function (res) {
        if (!res.ok) throw new Error(res.status);
        try { localStorage.removeItem(KEY); } catch (e2) {}
        form.reset();
        status.className = "form__status is-ok";
        status.textContent = "Recibido. Antes de publicar les mandamos cómo quedó su ficha. 🖤";
      })
      .catch(function () {
        status.className = "form__status is-error";
        status.textContent = "No se pudo enviar. Lo que escribieron sigue guardado aquí; revisen su conexión e inténtenlo otra vez.";
      })
      .then(function () { btn.disabled = false; });
  });
})();
