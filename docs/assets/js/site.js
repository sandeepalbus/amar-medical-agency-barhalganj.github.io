(function () {
  "use strict";
  var WA = document.documentElement.getAttribute("data-wa") || "";
  var DAYS = ["रविवार", "सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार"];
  function ist() {
    try { return new Date(new Date().toLocaleString("en-US", { timeZone: "Asia/Kolkata" })); }
    catch (e) { return new Date(); }
  }
  var s = document.querySelector("[data-status]");
  if (s) {
    var n = ist(), m = n.getHours() * 60 + n.getMinutes();
    var open = m >= 450 && m < 1320;
    s.className = "status " + (open ? "open" : "closed");
    s.textContent = open ? "अभी दुकान खुली है" : "अभी दुकान बंद है (सुबह 7:30 बजे खुलेगी)";
  }
  var today = ist().getDay(), tomorrow = (today + 1) % 7;
  var cards = document.querySelectorAll("[data-day]");
  var line = document.querySelector("[data-today-line]");
  var best = null, bestDelta = 99;
  for (var i = 0; i < cards.length; i++) {
    var d = parseInt(cards[i].getAttribute("data-day"), 10);
    var delta = (d - today + 7) % 7;
    if (delta === 0) cards[i].classList.add("is-today");
    var lab = cards[i].querySelector("[data-when]");
    if (lab) lab.textContent = delta === 0 ? "आज" : delta === 1 ? "कल" : DAYS[d];
    if (delta < bestDelta) { bestDelta = delta; best = cards[i]; }
  }
  if (line && best) {
    var who = best.getAttribute("data-name"), t = best.getAttribute("data-time");
    line.textContent = bestDelta === 0 ? "आज OPD: " + who + " (" + t + ")"
      : bestDelta === 1 ? "कल OPD: " + who + " (" + t + ")"
      : "अगली OPD: " + DAYS[parseInt(best.getAttribute("data-day"), 10)] + ", " + who;
  }
  var f = document.getElementById("book-form");
  if (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var name = f.elements.name.value.trim();
      var mob = f.elements.mobile.value.replace(/\D/g, "").slice(-10);
      var sel = f.elements.doctor;
      var doc = sel.options[sel.selectedIndex].text;
      if (!/^[6-9]\d{9}$/.test(mob)) {
        f.elements.mobile.setCustomValidity("कृपया 10 अंकों का सही मोबाइल नंबर लिखें");
        f.elements.mobile.reportValidity();
        return;
      }
      f.elements.mobile.setCustomValidity("");
      var msg = "नमस्ते, मैं " + name + " (मोबाइल: " + mob + ") " + doc +
        " की OPD के बारे में जानना चाहता/चाहती हूँ। कृपया समय और अपॉइंटमेंट की जानकारी दें।";
      window.location.href = "https://wa.me/" + WA + "?text=" + encodeURIComponent(msg);
    });
    f.elements.mobile.addEventListener("input", function () { this.setCustomValidity(""); });
  }
  var q = document.getElementById("q");
  if (q) {
    var items = document.querySelectorAll("[data-q]");
    var groups = document.querySelectorAll("[data-group]");
    var empty = document.getElementById("q-empty");
    q.addEventListener("input", function () {
      var v = q.value.trim().toLowerCase(), shown = 0;
      for (var i = 0; i < items.length; i++) {
        var hit = !v || items[i].getAttribute("data-q").indexOf(v) !== -1;
        items[i].classList.toggle("hide", !hit);
        if (hit) shown++;
      }
      for (var g = 0; g < groups.length; g++) {
        groups[g].classList.toggle("hide", !groups[g].querySelector("[data-q]:not(.hide)"));
      }
      if (empty) empty.classList.toggle("hide", shown > 0);
    });
  }
})();