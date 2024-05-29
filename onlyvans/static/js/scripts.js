document.addEventListener('DOMContentLoaded', function () {
    // Automatically close alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Handle the "Is this a free post?" checkbox and its associated tier field
    const isFreePostCheckbox = document.getElementById('id_is_free');
    const tierField = document.getElementById('id_tier');

    if (isFreePostCheckbox && tierField) {
        const tierFieldContainer = tierField.closest('.form-group') || tierField.parentNode;
        const tierLabel = document.querySelector('label[for="id_tier"]');

        function toggleTierField() {
            const isFree = isFreePostCheckbox.checked;
            tierFieldContainer.style.display = isFree ? 'none' : 'block';
            tierLabel.style.display = isFree ? 'none' : 'block';
            tierField.required = !isFree;
            tierField.disabled = isFree;
        }

        isFreePostCheckbox.addEventListener('change', toggleTierField);
        toggleTierField();
    }

    // Logic for purchasing points
    const purchasePointsSelect = document.getElementById('id_points');
    const purchaseAmountDisplay = document.getElementById('amount-to-pay-purchase');

    if (purchasePointsSelect && purchaseAmountDisplay) {
        function updatePurchaseAmount() {
            const points = parseInt(purchasePointsSelect.value, 10);
            const amountInCents = Math.floor(points * dollarsPerPoint * 100);
            const amount = (amountInCents / 100).toFixed(2);
            purchaseAmountDisplay.textContent = amount;
        }

        purchasePointsSelect.addEventListener('change', updatePurchaseAmount);
        updatePurchaseAmount();  // Initialize the amount display on page load
    }

    // Logic for withdrawals
    const withdrawPointsInput = document.getElementById('id_points');
    const withdrawAmountDisplay = document.getElementById('amount-to-pay-withdraw');

    if (withdrawPointsInput && withdrawAmountDisplay) {
        function updateWithdrawAmount() {
            const points = parseInt(withdrawPointsInput.value, 10);
            const amountInCents = Math.floor(points * dollarsPerPoint * 100 * 0.5);  // 50% fee
            const amount = (amountInCents / 100).toFixed(2);
            withdrawAmountDisplay.textContent = amount;
        }

        withdrawPointsInput.addEventListener('input', updateWithdrawAmount);
        updateWithdrawAmount();  // Initialize the amount display on page load
    }

    // Scroll the messages container to the bottom on load
    const container = document.getElementById('messages-container');
    if (container) {
        container.scrollTop = container.scrollHeight;
    }

    // Logic for delete tier modal
    const deleteModal = document.getElementById('deleteModal');
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const tierId = button.getAttribute('data-tier-id');
            const tierName = button.getAttribute('data-tier-name');
            const urlTemplate = button.getAttribute('data-url-template');

            const modalBody = deleteModal.querySelector('.modal-body #tierName');
            const deleteForm = deleteModal.querySelector('#deleteForm');

            modalBody.textContent = tierName;
            deleteForm.action = urlTemplate.replace(0, tierId);
        });
    }
});
