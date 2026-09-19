// Web-edition enhancements for the OpenStax book HTML.
//
// The left (book) sidebar is injected at build time by build_nav.py (robust under
// file://). This script adds the parts that must run in the browser:
//   * the right "On this page" sidebar, built from the page's own heading anchors;
//   * a scrollspy that highlights the current section as you scroll;
//   * the mobile hamburger toggle for the left sidebar.
// No dependencies. Degrades gracefully: with JS off, both sidebars still render
// (the right one just stays empty) and all links/anchors work.
(function () {
  "use strict";

  // right sidebar: "On this page" from the section headings (they carry ids)
  function buildPageToc() {
    var host = document.getElementById("page-toc");
    if (!host) return null;
    var content = document.querySelector("main.content") || document.body;
    var heads = content.querySelectorAll("h2[id], h3[id], h4[id]");
    if (heads.length < 2) { host.hidden = true; return null; }
    var title = document.createElement("div");
    title.className = "page-toc-title";
    title.textContent = "On this page";
    var ul = document.createElement("ul");
    heads.forEach(function (h) {
      var li = document.createElement("li");
      li.className = "lvl-" + h.tagName.toLowerCase();
      var a = document.createElement("a");
      a.href = "#" + h.id;
      a.textContent = (h.textContent || "").trim();
      a.dataset.target = h.id;
      li.appendChild(a);
      ul.appendChild(li);
    });
    host.appendChild(title);
    host.appendChild(ul);
    // Mobile: the static right sidebar is CSS-hidden below 1180px; expose the same
    // #page-toc as an off-canvas RIGHT drawer (mirror of the left ☰ Chapters
    // drawer). Create an upper-right toggle button + a scrim (CSS turns #page-toc
    // into the drawer on narrow screens). Only built here — i.e. only when the page
    // actually has an on-this-page (>=2 sub-headings) — so no orphan button.
    var btn = document.createElement("button");
    btn.id = "page-toc-toggle";
    btn.className = "page-toc-toggle";
    btn.setAttribute("aria-label", "Toggle on this page");
    btn.textContent = "On this page";
    var scrim = document.createElement("div");
    scrim.id = "toc-scrim";
    document.body.appendChild(btn);
    document.body.appendChild(scrim);
    function closeToc() { document.body.classList.remove("toc-open"); }
    btn.addEventListener("click", function () { document.body.classList.toggle("toc-open"); });
    scrim.addEventListener("click", closeToc);       // tap outside -> close
    host.querySelectorAll("a").forEach(function (a) { a.addEventListener("click", closeToc); });
    return heads;
  }

  // scrollspy: highlight the page-toc entry for the section currently in view
  function scrollSpy(heads) {
    if (!heads || !("IntersectionObserver" in window)) return;
    var links = {};
    document.querySelectorAll("#page-toc a").forEach(function (a) {
      links[a.dataset.target] = a;
    });
    var current = null;
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var a = links[e.target.id];
        if (!a) return;
        if (current) current.classList.remove("active");
        a.classList.add("active");
        current = a;
      });
    }, { rootMargin: "0px 0px -75% 0px", threshold: 0 });
    heads.forEach(function (h) { obs.observe(h); });
  }

  // left sidebar: expand/collapse a chapter's subtree when its caret is clicked
  function treeToggle() {
    document.querySelectorAll("#book-toc .toc-toggle").forEach(function (btn) {
      btn.addEventListener("click", function (ev) {
        ev.preventDefault();
        var li = btn.closest("li");
        if (li) li.classList.toggle("open");
      });
    });
  }

  // mobile: toggle the left (book) sidebar drawer
  function mobileToggle() {
    var btn = document.getElementById("nav-toggle");
    if (!btn) return;
    function close() { document.body.classList.remove("nav-open"); }
    btn.addEventListener("click", function () {
      document.body.classList.toggle("nav-open");
    });
    // tapping a chapter link closes the drawer (then navigates)
    document.querySelectorAll("#book-toc a").forEach(function (a) {
      a.addEventListener("click", close);
    });
    // tapping the page (the dimming scrim over the content, shown while the drawer
    // is open) closes it too — the expected "tap outside to dismiss" behaviour.
    var scrim = document.getElementById("nav-scrim");
    if (scrim) scrim.addEventListener("click", close);
  }

  // bring the active book-toc entry into view within the sticky sidebar
  function revealActive() {
    var a = document.querySelector("#book-toc a.active");
    if (!a || !a.scrollIntoView) return;
    try { a.scrollIntoView({ block: "center" }); } catch (e) { a.scrollIntoView(); }
  }

  function init() {
    var heads = buildPageToc();
    scrollSpy(heads);
    treeToggle();
    mobileToggle();
    revealActive();
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
