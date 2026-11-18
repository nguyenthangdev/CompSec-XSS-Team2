/*
 * demo.js — HARMLESS proof-of-concept payload for the Elgg Stored-XSS lab
 * ----------------------------------------------------------------------
 * PURPOSE
 *   Prove exactly ONE thing: a short <script src=...> reference stored in the
 *   250-character "Brief Description" field causes the browser to fetch and
 *   execute an EXTERNAL JavaScript file in the Elgg page's origin.
 *
 * WHAT IT DOES (all strictly local and visible):
 *   1. Shows a visual banner at the top of the page.
 *   2. Records a local, in-page demonstration event (timestamp + counter in
 *      the banner, a console.log line, and a sessionStorage counter).
 *
 * WHAT IT DELIBERATELY DOES **NOT** DO:
 *   - It does NOT send a friend request.
 *   - It does NOT edit the Brief Description or the About me field.
 *   - It does NOT copy itself into the viewer's profile (no self-propagation).
 *   - It does NOT read cookies, session tokens, or any credentials.
 *   - It makes NO authenticated request to any Elgg action endpoint.
 *
 * The real worm behaviour (add-friend, edit-profile, self-propagation) is
 * analysed in docs/analysis/self-propagation-analysis.md as THEORY ONLY.
 */
(function () {
  "use strict";

  var BANNER_ID = "xss-lab-demo-banner";
  var STORAGE_KEY = "xssLabDemoCount";

  // --- 1. Record a local demonstration event -------------------------------
  var count = 1;
  try {
    count = parseInt(window.sessionStorage.getItem(STORAGE_KEY) || "0", 10) + 1;
    window.sessionStorage.setItem(STORAGE_KEY, String(count));
  } catch (e) {
    // sessionStorage may be unavailable (e.g. file://) — non-fatal.
  }
  var when = new Date().toISOString();
  var where = (window.location && window.location.href) || "(unknown page)";

  // A single console line is enough to show execution in DevTools.
  console.log(
    "[XSS-LAB demo.js] HARMLESS proof-of-concept executed. " +
      "This external script ran inside the Elgg origin. " +
      "No account was modified. event#" +
      count +
      " at " +
      when +
      " on " +
      where
  );

  // --- 2. Show a harmless visual banner ------------------------------------
  function showBanner() {
    var existing = document.getElementById(BANNER_ID);
    var text =
      "✅ Stored-XSS PoC: external demo.js executed (harmless). " +
      "Event #" + count + " · " + when +
      " · No account modified.";

    if (existing) {
      existing.textContent = text;
      return;
    }

    var banner = document.createElement("div");
    banner.id = BANNER_ID;
    banner.textContent = text;
    banner.setAttribute(
      "style",
      [
        "position:fixed",
        "top:0",
        "left:0",
        "right:0",
        "z-index:2147483647",
        "margin:0",
        "padding:10px 14px",
        "font:600 14px/1.4 system-ui,Segoe UI,Roboto,Arial,sans-serif",
        "color:#0b3d0b",
        "background:#c8f7c5",
        "border-bottom:2px solid #2e7d32",
        "text-align:center",
        "box-shadow:0 2px 6px rgba(0,0,0,.2)",
      ].join(";")
    );
    (document.body || document.documentElement).appendChild(banner);
  }

  if (document.body) {
    showBanner();
  } else {
    document.addEventListener("DOMContentLoaded", showBanner);
  }

  // Optional alert() — the canonical "XSS executed" signal. Guarded so that it
  // only fires once per page and never blocks automated screenshotting if the
  // page sets window.XSS_LAB_NO_ALERT = true before the script loads.
  if (!window.XSS_LAB_NO_ALERT) {
    try {
      alert("XSS-LAB: harmless demo.js executed inside the Elgg page. No account was modified.");
    } catch (e) {
      /* alert may be blocked in some automation contexts — banner still shows. */
    }
  }
})();
