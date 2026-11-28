
document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById("electionModal");
    const openButton = document.getElementById("openElectionModal");
    const closeButton = document.getElementById("closeModal");
    const cancelButton = document.getElementById("cancelModal");
    const form = document.getElementById("electionForm");
    const tableBody = document.getElementById("electionTableBody");
    const saveButton = document.getElementById("saveElection");
    // ELECTION TYPE AND DEPARTMENT
    const electionTypeInput = document.getElementById("election_type");
    const departmentGroup = document.getElementById("departmentGroup");
    const departmentInput = document.getElementById("department");

    // DATE AND TIME INPUTS
    const startDateInput = form.elements["start_date"];
    const startTimeInput = form.elements["start_time"];
    const endDateInput = form.elements["end_date"];
    const endTimeInput = form.elements["end_time"];

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

        // START DATE: DISABLE PAST DATES
        startDateInput.min = today;

        // START TIME: IF TODAY IS SELECTED
        if (startDateInput.value === today) {
            startTimeInput.min = currentTime;
        } else {
            startTimeInput.removeAttribute("min");
        }

        // END DATE: CANNOT BE BEFORE START DATE
        const minimumEndDate = startDateInput.value || today;

        endDateInput.min = minimumEndDate;

        // CLEAR INVALID END DATE
        if (
            endDateInput.value &&
            endDateInput.value < minimumEndDate
        ) {
            endDateInput.value = "";
            endTimeInput.value = "";
        }

        // END TIME: MUST BE LATER IF SAME DATE
        if (
            startDateInput.value &&
            endDateInput.value === startDateInput.value
        ) {
            endTimeInput.min = startTimeInput.value;
        } else {
            endTimeInput.removeAttribute("min");
        }
    }

    

    // UPDATE RESTRICTIONS WHEN INPUT CHANGES
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

    // OPEN MODAL
    openButton.addEventListener("click", function () {
        modal.hidden = false;
        updateDateLimits();
    });

    // CLOSE MODAL
    function closeModal() {
        modal.hidden = true;
        form.reset();
        updateDateLimits();
        updateDepartmentField();
    }

    closeButton.addEventListener("click", closeModal);
    cancelButton.addEventListener("click", closeModal);

    // CLICK OUTSIDE TO CLOSE
    modal.addEventListener("click", function (event) {
        if (event.target === modal) {
            closeModal();
        }
    });

    // ESCAPE KEY TO CLOSE
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && !modal.hidden) {
            closeModal();
        }
    });

    // GET CSRF TOKEN
    function getCSRFToken() {
        return form.querySelector('[name="csrfmiddlewaretoken"]').value;
    }

    // ADD ELECTION TO TABLE
    function addElection(election) {

        const emptyMessage = document.getElementById("emptyElectionMessage");

        if (emptyMessage) {
            emptyMessage.remove();
        }

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
        const deleteButton = document.createElement("button");

        deleteButton.type = "button";
        deleteButton.className = "delete-election";
        deleteButton.textContent = "Delete";

        const urlTemplate = tableBody.dataset.deleteUrlTemplate;

        deleteButton.dataset.deleteUrl = urlTemplate.replace(
            "/0/",
            "/" + election.id + "/"
        );

        actionsCell.appendChild(deleteButton);

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

        tableBody.appendChild(row);
    }

    // CREATE ELECTION
    form.addEventListener("submit", async function (event) {

        event.preventDefault();

        updateDateLimits();

        const startDate = startDateInput.value;
        const startTime = startTimeInput.value;

        const endDate = endDateInput.value;
        const endTime = endTimeInput.value;

        if (!startDate || !startTime || !endDate || !endTime) {
            alert("Please complete all date and time fields.");
            return;
        }

        const start = new Date(startDate + "T" + startTime);
        const end = new Date(endDate + "T" + endTime);
        const now = new Date();

        // CHECK PAST START DATE
        if (start < now) {
            alert("Start date and time cannot be in the past.");
            return;
        }

        // CHECK END DATE
        if (end <= start) {
            alert("End date and time must be later than the start date and time.");
            return;
        }

        saveButton.disabled = true;

        try {

            const response = await fetch(form.action, {
                method: "POST",
                body: new FormData(form),
                headers: {
                    "X-CSRFToken": getCSRFToken()
                }
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                alert(data.message || "Unable to save election.");
                return;
            }

            addElection(data.election);

            closeModal();

            alert(data.message);

        } catch (error) {

            console.error("Create error:", error);
            alert("Unable to connect to the server.");

        } finally {

            saveButton.disabled = false;

        }
    });

    // DELETE ELECTION
    tableBody.addEventListener("click", async function (event) {

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
                alert(data.message || "Unable to delete election.");
                return;
            }

            button.closest("tr").remove();

            if (tableBody.querySelectorAll("tr").length === 0) {

                tableBody.innerHTML = `
                    <tr id="emptyElectionMessage">
                        <td colspan="6" class="empty-message">
                            No elections available. Click Create New Election to get started.
                        </td>
                    </tr>
                `;
            }

            alert(data.message);

        } catch (error) {

            console.error("Delete error:", error);
            alert("Unable to connect to the server.");

        }

    });

    // INITIALIZE DATE RESTRICTIONS
    updateDateLimits();

});
