
document.addEventListener("DOMContentLoaded", function () {

    // Get modal elements
    const voterDialog = document.getElementById("voterDialog");
    const openVoterDialog = document.getElementById("openVoterDialog");
    const closeButtons = document.querySelectorAll("#voterDialog [data-close]");

    // Open Add Voter Modal
    if (openVoterDialog && voterDialog) {
        openVoterDialog.addEventListener("click", function () {
            voterDialog.showModal();
        });
    }

    // Close Modal Buttons
    closeButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            voterDialog.close();
        });
    });

    // Close when clicking outside the modal
    if (voterDialog) {
        voterDialog.addEventListener("click", function (event) {
            if (event.target === voterDialog) {
                voterDialog.close();
            }
        });

        // Automatically open modal if there are form errors
        if (voterDialog.dataset.open === "true") {
            voterDialog.showModal();
        }
    }

});
