// OSAS Voting System - navigation behavior (sidebar + account dropdown)
(function () {
  "use strict";

  var sidebar = document.getElementById("appSidebar");
  if (!sidebar) return; // no navigation on this page

  var overlay = document.getElementById("sidebarOverlay");
  var toggle = document.getElementById("sidebarToggle");
  var accountBtn = document.getElementById("accountBtn");
  var accountMenu = document.getElementById("accountMenu");
  var accountWrap = document.getElementById("accountMenuWrap");

  // ----- Mobile sidebar -----
  function openSidebar() {
    sidebar.classList.add("is-open");
    overlay.hidden = false;
    toggle.setAttribute("aria-expanded", "true");
  }

  function closeSidebar() {
    sidebar.classList.remove("is-open");
    overlay.hidden = true;
    toggle.setAttribute("aria-expanded", "false");
  }

  if (toggle) {
    toggle.addEventListener("click", function () {
      sidebar.classList.contains("is-open") ? closeSidebar() : openSidebar();
    });
  }
  if (overlay) overlay.addEventListener("click", closeSidebar);

  sidebar.querySelectorAll(".nav-link").forEach(function (link) {
    link.addEventListener("click", closeSidebar);
  });

  window.addEventListener("resize", function () {
    if (window.innerWidth >= 768) closeSidebar();
  });

  // ----- Account dropdown -----
  function setAccountMenu(open) {
    accountMenu.hidden = !open;
    accountBtn.setAttribute("aria-expanded", open ? "true" : "false");
  }

  accountBtn.addEventListener("click", function () {
    setAccountMenu(accountMenu.hidden);
  });

  document.addEventListener("click", function (e) {
    if (!accountWrap.contains(e.target)) setAccountMenu(false);
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      setAccountMenu(false);
      closeSidebar();
    }
  });
})();