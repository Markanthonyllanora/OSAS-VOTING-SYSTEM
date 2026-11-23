document.addEventListener("DOMContentLoaded", () => {
  const donutEl = document.getElementById("donutChart");
  if (donutEl && window.Chart) {
    new Chart(donutEl, {
      type: "doughnut",
      data: {
        labels: ["President", "Vice President", "Secretary", "Treasurer", "Auditor", "Others"],
        datasets: [{
          data: [45, 42, 38, 36, 30, 27],
          backgroundColor: ["#2563eb", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444", "#94a3b8"],
          borderWidth: 0
        }]
      },
      options: { cutout: "70%", plugins: { legend: { position: "right" } } }
    });
  }

  const turnoutEl = document.getElementById("turnoutDonut");
  if (turnoutEl && window.Chart) {
    const pct = parseFloat(turnoutEl.dataset.turnout || "63.7");
    new Chart(turnoutEl, {
      type: "doughnut",
      data: {
        labels: ["Voted", "Did not vote"],
        datasets: [{
          data: [pct, Math.max(0, 100 - pct)],
          backgroundColor: ["#2563eb", "#e2e8f0"],
          borderWidth: 0
        }]
      },
      options: { cutout: "76%", plugins: { legend: { display: false } } }
    });
  }
});
