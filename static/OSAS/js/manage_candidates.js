// Manage Candidates: Add Candidate popup + photo preview + department field
(function () {
  "use strict";

  var dialog = document.getElementById("candidateDialog");
  if (!dialog) return;

  var openBtn = document.getElementById("openCandidateDialog");
  var fileInput = document.getElementById("id_photo");
  var preview = document.getElementById("photoPreview");
  var placeholder = document.getElementById("photoDefault");
  var electionSelect = document.getElementById("id_election");
  var departmentField = document.getElementById("departmentField");

  // Show the Department dropdown only when the election is "Department"
  function syncDepartment() {
    if (!electionSelect || !departmentField) return;
    departmentField.hidden = electionSelect.value !== "DEPARTMENT";
  }

  function openDialog() {
    if (!dialog.open) dialog.showModal();
    syncDepartment();
  }

  function closeDialog() {
    dialog.close();
  }

  if (openBtn) openBtn.addEventListener("click", openDialog);

  dialog.querySelectorAll("[data-close]").forEach(function (btn) {
    btn.addEventListener("click", closeDialog);
  });

  // Click on the dark backdrop closes the popup
  dialog.addEventListener("click", function (e) {
    if (e.target === dialog) closeDialog();
  });

  if (electionSelect) electionSelect.addEventListener("change", syncDepartment);
  syncDepartment();

  // Reopen automatically when the server found errors in the form
  if (dialog.dataset.open === "true") openDialog();

  // Show a preview of the chosen photo inside the circle
  if (fileInput) {
    fileInput.addEventListener("change", function () {
      var file = fileInput.files && fileInput.files[0];
      if (!file) return;
      preview.src = URL.createObjectURL(file);
      preview.hidden = false;
      placeholder.style.display = "none";
    });
  }
})();