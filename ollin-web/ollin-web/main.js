/* =========================================================
   Ollin — interacciones
   1. Cuenta regresiva en noches
   2. Cielo: estrellas en profundidad, fugaces y nebulosa viva
   3. Formulario "Avísame" (Netlify Forms)
   ========================================================= */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- 1. Cuenta regresiva en lunas ----------
     Cuenta las lunas llenas que faltan para el evento y dibuja la fase de hoy.
     Luna nueva de referencia: 6 ene 2000 18:14 UTC; mes sinódico: 29.530588853 días. */
  var EVENT_DATE = new Date("2027-07-11T19:00:00-06:00");   // EDITAR si cambia la hora
  var SYN = 29.530588853 * 86400000;
  var NEW0 = Date.UTC(2000, 0, 6, 18, 14);

  function phaseAt(t) { var p = ((t - NEW0) % SYN) / SYN; return p < 0 ? p + 1 : p; } // 0 nueva, .5 llena
  function fullMoonsBetween(a, b) {
    var k = Math.ceil((a - NEW0) / SYN - 0.5);           // primera llena después de a
    var n = 0;
    for (var t = NEW0 + (k + 0.5) * SYN; t <= b; t += SYN) if (t >= a) n++;
    return n;
  }
  function drawPhase(svg, p) {
    if (!svg) return;
    var r = 16, c = 20, k = Math.cos(2 * Math.PI * p) * r;   // radio x del terminador
    var waxing = p < 0.5;
    var sweepOuter = waxing ? 1 : 0;
    var sweepInner = (p < 0.25 || p > 0.75) ? (waxing ? 0 : 1) : (waxing ? 1 : 0);
    var lit = "M" + c + " " + (c - r) +
      " A" + r + " " + r + " 0 0 " + sweepOuter + " " + c + " " + (c + r) +
      " A" + Math.abs(k).toFixed(2) + " " + r + " 0 0 " + sweepInner + " " + c + " " + (c - r) + "Z";
    svg.innerHTML = '<circle cx="20" cy="20" r="16" fill="rgba(234,223,200,.12)" stroke="rgba(234,223,200,.35)" stroke-width="1"/>' +
      '<path d="' + lit + '" fill="#EADFC8"/>';
  }
  function renderCountdown() {
    var el = document.getElementById("countdown-text");
    if (!el) return;
    var now = new Date();
    drawPhase(document.getElementById("fase"), phaseAt(now.getTime()));
    var ms = EVENT_DATE - now;
    var nights = Math.ceil(ms / 86400000);
    var lunas = fullMoonsBetween(now.getTime(), EVENT_DATE.getTime());
    if (nights > 1) {
      el.innerHTML = lunas > 1
        ? "Faltan <strong>" + lunas + " lunas llenas</strong> (" + nights + " noches)"
        : lunas === 1 ? "Falta <strong>una luna llena</strong> (" + nights + " noches)"
        : "Faltan <strong>" + nights + " noches</strong>";
    } else if (nights === 1) {
      el.innerHTML = "<strong>Mañana</strong> nos vemos en La Luna";
    } else if (ms > -6 * 3600000) {
      el.innerHTML = "<strong>Es esta noche</strong>";
    } else {
      el.textContent = "Gracias por llegar al centro con nosotros 🖤";
    }
  }
  renderCountdown();

  /* ---------- Playlist: si hay link de embed, se monta el reproductor ---------- */
  var pl = document.getElementById("playlist-player");
  if (pl) {
    var src = (pl.getAttribute("data-embed") || "").trim();
    if (/^https:\/\/open\.spotify\.com\/embed\//.test(src)) {
      pl.innerHTML = '<iframe class="player" title="Playlist de Ollin en Spotify" src="' + src.replace(/"/g, "") +
        '" width="100%" height="352" loading="lazy" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>';
    }
  }

  /* ---------- 2. Cielo ----------
     Estrellas fijas en tres profundidades (parpadean y responden al scroll y al mouse),
     cometas cada pocos segundos y nebulosas con parallax.
     Todo se apaga al llegar a la tierra. */
  var canvas = document.getElementById("sky");
  var cosmos = document.querySelector(".cosmos");
  if (canvas && canvas.getContext) {
    var ctx = canvas.getContext("2d");
    var stars = [], meteors = [];
    var w = 0, h = 0, dpr = 1;
    var bone = "234,223,200", gold = "214,175,99", marigold = "238,123,39", jade = "100,165,142";
    var accent = [gold, gold, marigold, jade];
    var mouseX = 0, mouseY = 0, smX = 0, smY = 0;
    var scrollY0 = window.scrollY || 0;
    var nextMeteor = 1200;
    var last = 0;

    function makeStar() {
      var z = Math.random();                       // 0 = lejos, 1 = cerca
      return {
        x: Math.random() * w,
        y: Math.random() * h,
        z: z,
        r: 0.25 + z * 1.15,
        a: 0.25 + Math.random() * 0.75,
        tw: Math.random() * Math.PI * 2,
        tws: 0.6 + Math.random() * 1.8,             // velocidad de parpadeo
        c: Math.random() < 0.08 ? accent[Math.floor(Math.random() * accent.length)] : bone
      };
    }

    function resize() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = canvas.clientWidth; h = canvas.clientHeight;
      canvas.width = w * dpr; canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var count = Math.round(Math.min(420, (w * h) / 3600));
      stars = [];
      for (var i = 0; i < count; i++) stars.push(makeStar());
    }

    function spawnMeteor() {
      var fromLeft = Math.random() < 0.5;
      var ang = (fromLeft ? 22 : 158) + (Math.random() * 22 - 11); // grados, hacia abajo
      var rad = ang * Math.PI / 180;
      var grande = Math.random() < 0.25;                            // a veces, un cometa lento y largo
      var speed = grande ? 4 + Math.random() * 3 : 9 + Math.random() * 7;
      meteors.push({
        x: fromLeft ? Math.random() * w * 0.6 : w * 0.4 + Math.random() * w * 0.6,
        y: Math.random() * h * 0.5,
        vx: Math.cos(rad) * speed, vy: Math.sin(rad) * speed,
        len: grande ? 260 + Math.random() * 180 : 140 + Math.random() * 160,
        head: grande ? 2.6 : 1.7,
        life: 0, max: grande ? 110 + Math.random() * 50 : 45 + Math.random() * 35,
        c: Math.random() < 0.35 ? marigold : (Math.random() < 0.5 ? gold : bone)
      });
    }

    function wrap(v, max) { return ((v % max) + max) % max; }

    function draw(t) {
      ctx.clearRect(0, 0, w, h);
      var scroll = (window.scrollY || 0) - scrollY0;
      for (var i = 0; i < stars.length; i++) {
        var s = stars[i];
        // parallax: las cercanas se mueven más con el scroll y el mouse
        var px = wrap(s.x + smX * (6 + s.z * 26), w);
        var py = wrap(s.y - scroll * (0.04 + s.z * 0.22) + smY * (4 + s.z * 18), h + 20) - 10;
        var alpha = s.a * (0.55 + 0.45 * Math.sin(t / 1000 * s.tws + s.tw));
        ctx.fillStyle = "rgba(" + s.c + "," + alpha + ")";
        ctx.beginPath(); ctx.arc(px, py, s.r, 0, Math.PI * 2); ctx.fill();
      }
      for (var m = 0; m < meteors.length; m++) {
        var me = meteors[m];
        var k = me.life / me.max;
        var fade = k < 0.2 ? k / 0.2 : 1 - (k - 0.2) / 0.8;
        var sp = Math.sqrt(me.vx * me.vx + me.vy * me.vy);
        var tx = me.x - me.vx / sp * me.len, ty = me.y - me.vy / sp * me.len;
        var mg = ctx.createLinearGradient(tx, ty, me.x, me.y);
        mg.addColorStop(0, "rgba(" + me.c + ",0)");
        mg.addColorStop(1, "rgba(" + me.c + "," + (0.9 * fade) + ")");
        ctx.strokeStyle = mg; ctx.lineWidth = me.head; ctx.lineCap = "round";
        ctx.beginPath(); ctx.moveTo(tx, ty); ctx.lineTo(me.x, me.y); ctx.stroke();
        // cabeza con brillo
        var hg = ctx.createRadialGradient(me.x, me.y, 0, me.x, me.y, me.head * 6);
        hg.addColorStop(0, "rgba(255,244,220," + (0.9 * fade) + ")");
        hg.addColorStop(1, "rgba(" + me.c + ",0)");
        ctx.fillStyle = hg;
        ctx.beginPath(); ctx.arc(me.x, me.y, me.head * 6, 0, Math.PI * 2); ctx.fill();
      }
    }

    function step(t) {
      var dt = Math.min(50, t - (last || t)); last = t;
      var f = dt / 16.7;
      smX += (mouseX - smX) * 0.04; smY += (mouseY - smY) * 0.04;
      nextMeteor -= dt;
      if (nextMeteor <= 0) { spawnMeteor(); nextMeteor = 1800 + Math.random() * 3200; }
      parallaxNebula();
      for (var m = meteors.length - 1; m >= 0; m--) {
        var me = meteors[m];
        me.x += me.vx * f; me.y += me.vy * f; me.life += f;
        if (me.life > me.max) meteors.splice(m, 1);
      }
      draw(t);
      if (running) requestAnimationFrame(step); else last = 0;
    }

    // Nebulosas: cada capa se desplaza a distinta velocidad con el scroll y el mouse
    var layers = cosmos ? Array.prototype.slice.call(cosmos.querySelectorAll(".cosmos__layer")) : [];
    function parallaxNebula() {
      var sc = window.scrollY || 0;
      for (var i = 0; i < layers.length; i++) {
        var d = parseFloat(layers[i].getAttribute("data-depth")) || 0;
        layers[i].style.transform = "translate3d(" + (smX * d * -120).toFixed(1) + "px," + (-sc * d + smY * d * -80).toFixed(1) + "px,0)";
      }
    }

    var running = false;
    var visible = true;
    resize();
    window.addEventListener("resize", function () { resize(); updateFade(); if (!running) draw(0); });
    window.addEventListener("pointermove", function (e) {
      if (e.pointerType !== "mouse") return;
      mouseX = (e.clientX / w - 0.5) * 2; mouseY = (e.clientY / h - 0.5) * 2;
    }, { passive: true });

    // Las estrellas y la nebulosa se apagan conforme bajamos a la tierra
    var horizon = document.querySelector(".horizonte");
    function updateFade() {
      if (!horizon) return;
      var top = horizon.getBoundingClientRect().top;
      var vh = window.innerHeight;
      var start = vh * 1.6, end = vh * 0.1;
      var k = Math.max(0, Math.min(1, (top - end) / (start - end)));
      canvas.style.opacity = k.toFixed(3);
      if (cosmos) cosmos.style.opacity = Math.max(0, Math.min(1, k * 1.3 - 0.1)).toFixed(3);
      var nowVisible = k > 0.01;
      if (nowVisible && !visible && !reduceMotion && !running) { running = true; requestAnimationFrame(step); }
      visible = nowVisible;
      if (!visible) running = false;
      if (reduceMotion) draw(0);
    }
    window.addEventListener("scroll", updateFade, { passive: true });
    updateFade();

    if (reduceMotion) {
      draw(0);
    } else if (visible) {
      running = true;
      requestAnimationFrame(step);
    }
  }

  /* ---------- Lago: oleaje y destellos de la luna ----------
     1) Oleaje: el agua se redibuja en franjas horizontales y cada una se desplaza con una
        onda. Cerca del horizonte las ondas son finas y rápidas; al acercarse, más amplias.
     2) Destellos: brillos breves en la columna de la luna, más anchos al acercarse.
     Corre a ~30 cuadros por segundo y se detiene si el lago no está en pantalla
     o si el usuario pidió "reducir movimiento". */
  (function () {
    var lago = document.querySelector(".lago");
    var cvO = document.getElementById("lago-olas");
    var cvB = document.getElementById("lago-brillos");
    if (!lago || !cvO || !cvB || !cvO.getContext) return;
    var cO = cvO.getContext("2d"), cB = cvB.getContext("2d");
    var narrow = window.matchMedia("(max-width: 700px)");
    var W = 0, H = 0, dpr = 1, glints = [], visible = false, last = 0, acc = 0;
    var img = new Image(), imgOk = false;
    var src = { sx: 0, sy: 0, sw: 0, sh: 0, scale: 1 };

    function fitCover() {                       // igual que background-size: cover; top center
      var iw = img.naturalWidth, ih = img.naturalHeight;
      var s = Math.max((W + 48) / iw, (H + 48) / ih);
      src.scale = s;
      src.sw = (W + 48) / s; src.sh = (H + 48) / s;
      src.sx = (iw - src.sw) / 2; src.sy = 0;
    }
    function makeGlint() {
      var d = Math.pow(Math.random(), 0.8);
      var spread = 30 + d * W * 0.2;
      var g = Math.random() + Math.random() + Math.random() - 1.5;
      return { d: d, x: W / 2 + g * spread, y: 56 + d * (H - 90),
               len: 4 + d * 34 * (0.4 + Math.random()), th: 0.6 + d * 1.6,
               ph: Math.random() * Math.PI * 2, sp: 0.8 + Math.random() * 2.4,
               vx: (Math.random() - 0.5) * (0.04 + d * 0.12) };
    }
    function resize() {
      dpr = Math.min(window.devicePixelRatio || 1, narrow.matches ? 1.5 : 2);
      W = lago.clientWidth; H = lago.clientHeight;
      [cvO, cvB].forEach(function (c) { c.width = W * dpr; c.height = H * dpr; });
      cO.setTransform(dpr, 0, 0, dpr, 0, 0); cB.setTransform(dpr, 0, 0, dpr, 0, 0);
      if (imgOk) fitCover();
      glints = [];
      var n = narrow.matches ? 70 : 170;
      for (var i = 0; i < n; i++) glints.push(makeGlint());
    }

    function drawWater(t) {
      if (!imgOk) return;
      var s = t / 1000, band = narrow.matches ? 3 : 2;
      var top = 0;
      cO.clearRect(0, 0, W, H);
      for (var y = top; y < H; y += band) {
        var d = y / H;                                         // 0 horizonte, 1 cerca
        var k = 0.22 / (0.08 + d);                             // frecuencia: fina lejos, amplia cerca
        var amp = 0.6 + d * 7;                                 // amplitud en px
        var dx = Math.sin(y * k - s * (1.6 - d * 0.6)) * amp
               + Math.sin(y * k * 0.37 + s * 0.9 + 1.7) * amp * 0.55;
        var dy = Math.sin(y * k * 0.5 - s * 1.1) * amp * 0.18;
        var sy = src.sy + (y + 24 + dy) / src.scale;
        cO.drawImage(img, src.sx, sy, src.sw, band / src.scale + 0.5,
                     -24 + dx, y, W + 48, band + 0.5);
      }
      // la orilla de piedra: el agua se oscurece abajo, como en la versión fija
      var g = cO.createLinearGradient(0, H * 0.6, 0, H);
      g.addColorStop(0, "rgba(5,10,11,0)");
      g.addColorStop(1, "#0B0E0B");
      cO.fillStyle = g; cO.fillRect(0, H * 0.6, W, H * 0.4);
      if (narrow.matches) {                                    // en celular, más oscuro para que se lea
        cO.fillStyle = "rgba(5,10,11,.55)"; cO.fillRect(0, 0, W, H);
      }
    }
    function drawGlints(t) {
      cB.clearRect(0, 0, W, H);
      cB.globalCompositeOperation = "lighter";
      for (var i = 0; i < glints.length; i++) {
        var gl = glints[i];
        var a = Math.sin(t / 1000 * gl.sp + gl.ph);
        a = a > 0 ? a * a * a : 0;
        if (a < 0.02) continue;
        var alpha = a * (0.95 - gl.d * 0.35) * (narrow.matches ? 0.5 : 0.85);
        var grd = cB.createLinearGradient(gl.x - gl.len / 2, 0, gl.x + gl.len / 2, 0);
        grd.addColorStop(0, "rgba(255,236,196,0)");
        grd.addColorStop(0.5, "rgba(255,240,210," + alpha.toFixed(3) + ")");
        grd.addColorStop(1, "rgba(255,236,196,0)");
        cB.fillStyle = grd;
        cB.fillRect(gl.x - gl.len / 2, gl.y - gl.th / 2, gl.len, gl.th);
      }
      cB.globalCompositeOperation = "source-over";
    }
    function step(t) {
      var dt = Math.min(100, t - (last || t)); last = t; acc += dt;
      if (acc >= 32) {                                         // ~30 cuadros por segundo
        var f = acc / 16.7; acc = 0;
        for (var i = 0; i < glints.length; i++) {
          var gl = glints[i];
          gl.x += gl.vx * f;
          if (Math.abs(gl.x - W / 2) > 40 + gl.d * W * 0.32) glints[i] = makeGlint();
        }
        drawWater(t); drawGlints(t);
      }
      if (visible) requestAnimationFrame(step); else last = 0;
    }

    resize();
    window.addEventListener("resize", resize);
    if (reduceMotion) { drawGlints(1500); return; }            // agua quieta (la de CSS), sin oleaje
    img.onload = function () {
      imgOk = true; fitCover(); cvO.classList.add("is-on");
    };
    img.src = "img/water.jpg";
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) {
        var v = en[0].isIntersecting;
        if (v && !visible) { visible = true; requestAnimationFrame(step); }
        visible = v;
      }).observe(lago);
    } else { visible = true; requestAnimationFrame(step); }
  })();

  /* ---------- 3. Formulario ---------- */
  var form = document.getElementById("avisame-form");
  if (form) {
    var status = document.getElementById("form-status");
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
          form.reset();
          status.className = "form__status is-ok";
          status.textContent = "Listo. Te avisamos en cuanto salgan los boletos. 🖤";
        })
        .catch(function () {
          status.className = "form__status is-error";
          status.textContent = "No se pudo enviar. Revisa tu conexión e inténtalo otra vez.";
        })
        .then(function () { btn.disabled = false; });
    });
  }
})();
