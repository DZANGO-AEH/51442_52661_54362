document.addEventListener('DOMContentLoaded', function () {
    // Automatically close alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Handle the "same email as PayPal" checkbox
    let sameEmailCheckbox = document.querySelector('#id_same_email');
    let paypalEmailField = document.querySelector('#id_paypal_email');
    let emailField = document.querySelector('#id_email');

    if (sameEmailCheckbox && paypalEmailField && emailField) {
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
        form.addEventListener('submit', function () {
            if (sameEmailCheckbox.checked) {
                paypalEmailField.value = emailField.value;
            }
        });
    }

    // Handle the "Is this a free post?" checkbox and its associated tier field
    let isFreePostCheckbox = document.getElementById('id_is_free');
    let tierField = document.getElementById('id_tier');

    if (isFreePostCheckbox && tierField) {
        let tierFieldContainer = tierField.closest('.form-group') || tierField.parentNode;
        let tierLabel = document.querySelector('label[for="id_tier"]');

        function toggleTierField() {
            let isFree = isFreePostCheckbox.checked;
            tierFieldContainer.style.display = isFree ? 'none' : 'block';
            tierLabel.style.display = isFree ? 'none' : 'block';
            tierField.required = !isFree;
            tierField.disabled = isFree;
        }

        isFreePostCheckbox.addEventListener('change', toggleTierField);
        toggleTierField();
    }
});

window.onload = function() {
    let container = document.getElementById('messages-container');
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}