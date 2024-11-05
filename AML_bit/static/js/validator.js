document.addEventListener('DOMContentLoaded', function() {
    // Check Address Form Validation
    const checkAddressForm = document.getElementById('addressForm');
    const checkAddressInput = document.getElementById('check_address');

    if (checkAddressForm) {
        checkAddressForm.addEventListener('submit', function(e) {
            validateAddressForm(e, checkAddressInput);
        });
    }

    // Report Address Form Validation
    const reportForm = document.getElementById('reportForm');
    const reportAddressInput = document.getElementById('report_address');

    if (reportForm) {
        reportForm.addEventListener('submit', function(e) {
            validateAddressForm(e, reportAddressInput);
        });
    }
});

function validateAddressForm(e, addressInput) {
    const address = addressInput.value.trim();
    
    // Basic validation
    if (!address) {
        e.preventDefault();
        alert('Please enter an address');
        return;
    }

    // Bitcoin address format validation
    const btcRegex = /^(1|3|bc1)[a-zA-Z0-9]{25,62}$/;
    if (!btcRegex.test(address)) {
        e.preventDefault();
        alert('Invalid Bitcoin address format');
        return;
    }
}
