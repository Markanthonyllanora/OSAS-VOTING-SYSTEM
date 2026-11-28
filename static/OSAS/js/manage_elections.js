document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById("electionModal");
    const openButton = document.getElementById("openElectionModal");
    const closeButton = document.getElementById("closeModal");
    const cancelButton = document.getElementById("cancelModal");
    const form = document.getElementById("electionForm");
    const tableBody = document.getElementById("electionTableBody");
    const saveButton = document.getElementById("saveElection");
    const modalTitle = document.getElementById("modalTitle");
    const modalSubtitle = document.getElementById("modalSubtitle");

    // ELECTION TYPE AND DEPARTMENT
    const titleInput = document.getElementById("electionTitle");
    const descriptionInput = document.getElementById("electionDescription");
    const electionTypeInput = document.getElementById("election_type");
    const departmentGroup = document.getElementById("departmentGroup");
    const departmentInput = document.getElementById("department");

    // DATE AND TIME INPUTS
    const startDateInput = form.elements["start_date"];
    const startTimeInput = form.elements["start_time"];
    const endDateInput = form.elements["end_date"];
    const endTimeInput = form.elements["end_time"];

    // null = creating, otherwise the edit URL of the election being edited
    let editingUrl = null;
    let editingRow = null;

    // ===== MESSAGE POPUP (replaces alert) =====
    function showPopup(message, type, onClose) {
        const overlay = document.getElementById("msgPopup");
        const box = overlay.querySelector(".msg-box");
        const icon = document.getElementById("msgIcon");
        const title = document.getElementById("msgTitle");

        box.classList.remove("is-error", "is-success");

        if (type === "error") {
            box.classList.add("is-error");
            icon.textContent = "!";
            title.textContent = "Error";
        } else if (type === "success") {
            box.classList.add("is-success");
            icon.textContent = "✓";
            title.textContent = "Success";
        } else {
            icon.textContent = "i";
            title.textContent = "Notice";
        }

        document.getElementById("msgText").textContent = message;
        overlay.hidden = false;

        function close() {
            overlay.hidden = true;
            if (typeof onClose === "function") onClose();
        }

        document.getElementById("msgOk").onclick = close;
        document.getElementById("msgClose").onclick = close;
    }

    // ===== FIELD ERRORS =====
    function errorLine(input) {
        return input.closest(".form-group").querySelector(".field-error");
    }

    function setError(input, message) {
        errorLine(input).textContent = message;
        input.closest(".form-group").classList.add("has-error");
    }

    function clearErrors() {
        form.querySelectorAll(".field-error").forEach(function (line) {
            line.textContent = "";
        });
        form.querySelectorAll(".has-error").forEach(function (group) {
            group.classList.remove("has-error");
        });
    }

    // Past start date -> under the date, otherwise under the time
    function showStartError(message) {
        if (startDateInput.value && startDateInput.value < getToday()) {
            setError(startDateInput, message);
        } else {
            setError(startTimeInput, message);
        }
    }

    // End before start date -> under the end date, otherwise under the end time
    function showEndError(message) {
        if (endDateInput.value && startDateInput.value && endDateInput.value < startDateInput.value) {
            setError(endDateInput, message);
        } else {
            setError(endTimeInput, message);
        }
    }

    // GET TODAY'S DATE
    function getToday() {
        const today = new Date();

        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, "0");
        const day = String(today.getDate()).padStart(2, "0");

        return `${year}-${month}-${day}`;
    }

    // GET CURRENT TIME
    function getCurrentTime() {
        const now = new Date();

        const hours = String(now.getHours()).padStart(2, "0");
        const minutes = String(now.getMinutes()).padStart(2, "0");

        return `${hours}:${minutes}`;
    }

    // DATE PICKER RESTRICTIONS
    function updateDateLimits() {

        const today = getToday();
        const currentTime = getCurrentTime();

        startDateInput.min = today;

        if (startDateInput.value === today) {
            startTimeInput.min = currentTime;
        } else {
            startTimeInput.removeAttribute("min");
        }

        const minimumEndDate = startDateInput.value || today;

        endDateInput.min = minimumEndDate;

        if (endDateInput.value && endDateInput.value < minimumEndDate) {
            endDateInput.value = "";
            endTimeInput.value = "";
        }

        if (startDateInput.value && endDateInput.value === startDateInput.value) {
            endTimeInput.min = startTimeInput.value;
        } else {
            endTimeInput.removeAttribute("min");
        }
    }

    startDateInput.addEventListener("change", updateDateLimits);
    startTimeInput.addEventListener("change", updateDateLimits);
    endDateInput.addEventListener("change", updateDateLimits);

    // SHOW DEPARTMENT ONLY FOR DEPARTMENT ELECTIONS
    function updateDepartmentField() {

        if (electionTypeInput.value === "DEPARTMENT") {
            departmentGroup.style.display = "block";
            departmentInput.required = true;
        } else {
            departmentGroup.style.display = "none";
            departmentInput.required = false;
            departmentInput.value = "";
        }
    }

    electionTypeInput.addEventListener("change", updateDepartmentField);

    // ===== MODAL MODES =====
    function setCreateMode() {
        editingUrl = null;
        editingRow = null;
        modalTitle.textContent = "Create New Election";
        modalSubtitle.textContent = "Fill in the details below to create an election.";
        saveButton.textContent = "Save Election";
    }

    function setEditMode(button) {
        editingUrl = button.dataset.editUrl;
        editingRow = button.closest("tr");
        modalTitle.textContent = "Edit Election";
        modalSubtitle.textContent = "Update the details below, then save your changes.";
        saveButton.textContent = "Update Election";
    }

    function closeModal() {
        modal.hidden = true;
        form.reset();
        clearErrors();
        setCreateMode();
        updateDateLimits();
        updateDepartmentField();
    }

    openButton.addEventListener("click", function () {
        form.reset();
        clearErrors();
        setCreateMode();
        updateDepartmentField();
        modal.hidden = false;
        updateDateLimits();
    });

    closeButton.addEventListener("click", closeModal);
    cancelButton.addEventListener("click", closeModal);

    modal.addEventListener("click", function (event) {
        if (event.target === modal) {
            closeModal();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && !modal.hidden) {
            closeModal();
        }
    });

    // OPEN THE POPUP PRE-FILLED FOR EDITING
    function openEdit(button) {
        form.reset();
        clearErrors();
        setEditMode(button);

        titleInput.value = button.dataset.title || "";
        descriptionInput.value = button.dataset.description || "";

        electionTypeInput.value = button.dataset.type || "";
        updateDepartmentField();
        departmentInput.value = button.dataset.department || "";

        startDateInput.value = button.dataset.startDate || "";
        startTimeInput.value = button.dataset.startTime || "";
        endDateInput.value = button.dataset.endDate || "";
        endTimeInput.value = button.dataset.endTime || "";

        updateDateLimits();
        modal.hidden = false;
    }

    // GET CSRF TOKEN
    function getCSRFToken() {
        return form.querySelector('[name="csrfmiddlewaretoken"]').value;
    }

    // ===== TABLE ROWS =====
    function buildRow(election) {

        const row = document.createElement("tr");
        row.id = "election-" + election.id;

        const titleCell = document.createElement("td");
        titleCell.className = "election-title";
        titleCell.textContent = election.title;

        const descriptionCell = document.createElement("td");
        descriptionCell.textContent = election.description || "No description";

        const typeCell = document.createElement("td");
        typeCell.textContent = election.election_type;

        const departmentCell = document.createElement("td");
        departmentCell.textContent = election.department || "—";

        const statusCell = document.createElement("td");
        const status = document.createElement("span");
        status.className = "status " + election.status.toLowerCase();
        status.textContent = election.status;
        statusCell.appendChild(status);

        const startCell = document.createElement("td");
        startCell.textContent = election.start_date;

        const endCell = document.createElement("td");
        endCell.textContent = election.end_date;

        const actionsCell = document.createElement("td");

        // EDIT BUTTON
        const editButton = document.createElement("button");
        editButton.type = "button";
        editButton.className = "edit-election";
        editButton.textContent = "Edit";

        if (election.can_edit) {
            editButton.dataset.editUrl = tableBody.dataset.editUrlTemplate.replace(
                "/0/", "/" + election.id + "/"
            );
            editButton.dataset.title = election.title;
            editButton.dataset.description = election.description || "";
            editButton.dataset.type = election.election_type_value;
            editButton.dataset.department = election.department || "";
            editButton.dataset.startDate = election.start_date_raw;
            editButton.dataset.startTime = election.start_time_raw;
            editButton.dataset.endDate = election.end_date_raw;
            editButton.dataset.endTime = election.end_time_raw;
        } else {
            editButton.disabled = true;
            editButton.title = "Only upcoming elections can be edited";
        }

        // DELETE BUTTON
        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.className = "delete-election";
        deleteButton.textContent = "Delete";
        deleteButton.dataset.deleteUrl = tableBody.dataset.deleteUrlTemplate.replace(
            "/0/", "/" + election.id + "/"
        );

        actionsCell.append(editButton, " ", deleteButton);

        row.append(
            titleCell,
            descriptionCell,
            typeCell,
            departmentCell,
            statusCell,
            startCell,
            endCell,
            actionsCell
        );

        return row;
    }

    function addElection(election) {
        const emptyMessage = document.getElementById("emptyElectionMessage");

        if (emptyMessage) {
            emptyMessage.remove();
        }

        tableBody.appendChild(buildRow(election));
    }

    // ===== VALIDATION (browser side) =====
    function validateForm() {

        clearErrors();
        let valid = true;

        if (!titleInput.value.trim()) {
            setError(titleInput, "Please enter an election title.");
            valid = false;
        }

        if (!electionTypeInput.value) {
            setError(electionTypeInput, "Please select an election type.");
            valid = false;
        }

        if (electionTypeInput.value === "DEPARTMENT" && !departmentInput.value) {
            setError(departmentInput, "Please select a department.");
            valid = false;
        }

        if (!startDateInput.value) { setError(startDateInput, "Please choose a start date."); valid = false; }
        if (!startTimeInput.value) { setError(startTimeInput, "Please choose a start time."); valid = false; }
        if (!endDateInput.value) { setError(endDateInput, "Please choose an end date."); valid = false; }
        if (!endTimeInput.value) { setError(endTimeInput, "Please choose an end time."); valid = false; }

        if (!valid) {
            return false;
        }

        const start = new Date(startDateInput.value + "T" + startTimeInput.value);
        const end = new Date(endDateInput.value + "T" + endTimeInput.value);
        const now = new Date();
        now.setSeconds(0, 0);

        if (start < now) {
            showStartError("Start date and time cannot be in the past.");
            return false;
        }

        if (end <= start) {
            showEndError("End date and time must be later than the start.");
            return false;
        }

        return true;
    }

    // Show an error the server sent, under the right field
    function showServerError(data) {
        clearErrors();

        switch (data.field) {
            case "title": setError(titleInput, data.message); return;
            case "election_type": setError(electionTypeInput, data.message); return;
            case "department": setError(departmentInput, data.message); return;
            case "start": showStartError(data.message); return;
            case "end": showEndError(data.message); return;
        }

        showPopup(data.message || "Unable to save election.", "error");
    }

    // ===== CREATE OR UPDATE =====
    form.addEventListener("submit", async function (event) {

        event.preventDefault();

        updateDateLimits();

        if (!validateForm()) {
            return;
        }

        const isEdit = editingUrl !== null;
        const url = isEdit ? editingUrl : form.action;
        const rowToReplace = editingRow;

        saveButton.disabled = true;

        try {

            const response = await fetch(url, {
                method: "POST",
                body: new FormData(form),
                headers: {
                    "X-CSRFToken": getCSRFToken()
                }
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                showServerError(data);
                return;
            }

            if (isEdit && rowToReplace) {
                rowToReplace.replaceWith(buildRow(data.election));
            } else {
                addElection(data.election);
            }

            closeModal();

            showPopup(data.message, "success");

        } catch (error) {

            console.error("Save error:", error);
            showPopup("Unable to connect to the server.", "error");

        } finally {

            saveButton.disabled = false;

        }
    });

    // ===== EDIT AND DELETE BUTTONS =====
    tableBody.addEventListener("click", async function (event) {

        const editButton = event.target.closest(".edit-election");

        if (editButton) {
            if (!editButton.disabled) {
                openEdit(editButton);
            }
            return;
        }

        const button = event.target.closest(".delete-election");

        if (!button) {
            return;
        }

        if (!confirm("Are you sure you want to delete this election?")) {
            return;
        }

        try {

            const response = await fetch(button.dataset.deleteUrl, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken()
                }
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                showPopup(data.message || "Unable to delete election.", "error");
                return;
            }

            button.closest("tr").remove();

            if (tableBody.querySelectorAll("tr").length === 0) {

                tableBody.innerHTML = `
                    <tr id="emptyElectionMessage">
                        <td colspan="8" class="empty-message">
                            No elections available. Click Create New Election to get started.
                        </td>
                    </tr>
                `;
            }

            showPopup(data.message, "success");

        } catch (error) {

            console.error("Delete error:", error);
            showPopup("Unable to connect to the server.", "error");

        }

    });

    // INITIALIZE DATE RESTRICTIONS
    updateDateLimits();

});