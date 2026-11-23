document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById("electionModal");
    const openButton = document.getElementById("openElectionModal");
    const closeButton = document.getElementById("closeModal");
    const cancelButton = document.getElementById("cancelModal");
    const form = document.getElementById("electionForm");
    const tableBody = document.getElementById("electionTableBody");
    const saveButton = document.getElementById("saveElection");

    // OPEN MODAL
    openButton.addEventListener("click", function () {
        modal.hidden = false;
    });

    // CLOSE MODAL
    function closeModal() {
        modal.hidden = true;
        form.reset();
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

        const startDate = form.elements["start_date"].value;
        const startTime = form.elements["start_time"].value;

        const endDate = form.elements["end_date"].value;
        const endTime = form.elements["end_time"].value;

        const start = new Date(startDate + "T" + startTime);
        const end = new Date(endDate + "T" + endTime);

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

});
