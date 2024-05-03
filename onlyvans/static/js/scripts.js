document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert); // Initialize Bootstrap alert
            bsAlert.close(); // Close the alert
        }, 5000); // Set timeout for auto-dismissal
    });
});
