document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

document.addEventListener('DOMContentLoaded', function () {
    let sameEmailCheckbox = document.querySelector('#id_same_email');
    let paypalEmailField = document.querySelector('#id_paypal_email');
    let emailField = document.querySelector('#id_email');
    let paypalEmailFieldContainer = paypalEmailField.parentNode;

    function togglePaypalEmailField() {
        if (sameEmailCheckbox.checked) {
            paypalEmailFieldContainer.style.display = 'none';
            paypalEmailField.disabled = true;
            paypalEmailField.value = emailField.value;
        } else {
            paypalEmailFieldContainer.style.display = '';
            paypalEmailField.disabled = false;
        }
    }

    sameEmailCheckbox.addEventListener('change', togglePaypalEmailField);
    togglePaypalEmailField();

    let form = document.querySelector('form');
    form.addEventListener('submit', function (e) {
        if (sameEmailCheckbox.checked) {
            paypalEmailField.value = emailField.value;
        }
    });
});