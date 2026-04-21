/* FarmersConnect - Main JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips and popovers
    initializeBootstrapComponents();
    
    // Setup form validation
    setupFormValidation();
    
    // Auto-dismiss alerts after 5 seconds
    autoDismissAlerts();
});

/**
 * Initialize Bootstrap components (tooltips, popovers)
 */
function initializeBootstrapComponents() {
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Initialize all popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
}

/**
 * Setup form validation with Bootstrap
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

/**
 * Auto-dismiss alerts after 5 seconds
 */
function autoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert:not([data-no-auto-dismiss])');
    
    alerts.forEach(alert => {
        // Only auto-dismiss success alerts
        if (alert.classList.contains('alert-success')) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });
}

/**
 * Show loading spinner during form submission
 */
function showLoadingSpinner(formId, spinnerId = 'loadingSpinner') {
    const form = document.getElementById(formId);
    const spinner = document.getElementById(spinnerId);
    
    if (form) {
        form.addEventListener('submit', function() {
            if (spinner) {
                spinner.style.display = 'block';
            }
        });
    }
}

/**
 * Validate numeric input in real-time
 */
function validateNumericInput(inputId, min, max) {
    const input = document.getElementById(inputId);
    
    if (input) {
        input.addEventListener('change', function() {
            let value = parseFloat(this.value);
            
            if (isNaN(value)) {
                this.classList.add('is-invalid');
                return;
            }
            
            if (value < min || value > max) {
                this.classList.add('is-invalid');
                this.title = `Please enter a value between ${min} and ${max}`;
            } else {
                this.classList.remove('is-invalid');
            }
        });
    }
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Show/hide password toggle
 */
function setupPasswordToggle() {
    const toggleButtons = document.querySelectorAll('[data-toggle="password"]');
    
    toggleButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const input = document.getElementById(targetId);
            
            if (input) {
                const isPassword = input.type === 'password';
                input.type = isPassword ? 'text' : 'password';
                this.classList.toggle('fa-eye');
                this.classList.toggle('fa-eye-slash');
            }
        });
    });
}

/**
 * Handle file input with preview
 */
function setupFileInputPreview(inputId, previewId) {
    const fileInput = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    
    if (fileInput && preview) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
}

/**
 * Debounce function for preventing rapid API calls
 */
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

/**
 * Smooth scroll to element
 */
function smoothScrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text, showNotification = true) {
    navigator.clipboard.writeText(text).then(() => {
        if (showNotification) {
            showToast('Copied to clipboard!', 'success');
        }
    }).catch(err => {
        console.error('Failed to copy:', err);
        if (showNotification) {
            showToast('Failed to copy', 'danger');
        }
    });
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    const toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
    toastContainer.innerHTML = toastHtml;
    document.body.appendChild(toastContainer);
    
    const toast = new bootstrap.Toast(toastContainer.querySelector('.toast'));
    toast.show();
    
    // Remove container after timeout
    setTimeout(() => toastContainer.remove(), 3000);
}

/**
 * Get CSRF token from meta tag
 */
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}

/**
 * Make API call with CSRF token
 */
async function fetchWithCsrf(url, options = {}) {
    const headers = options.headers || {};
    headers['X-CSRFToken'] = getCsrfToken();
    
    return fetch(url, {
        ...options,
        headers
    });
}

/**
 * Check if form is dirty (has unsaved changes)
 */
function setupDirtyFormWarning(formId) {
    const form = document.getElementById(formId);
    let isDirty = false;
    
    if (form) {
        form.addEventListener('change', () => {
            isDirty = true;
        });
        
        form.addEventListener('submit', () => {
            isDirty = false;
        });
        
        window.addEventListener('beforeunload', (e) => {
            if (isDirty) {
                e.preventDefault();
                e.returnValue = '';
            }
        });
    }
}

/**
 * Format date to readable format
 */
function formatDate(dateString) {
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

/**
 * Display loading skeleton
 */
function showSkeleton(elementId, count = 3) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = Array(count).fill(`
            <div class="skeleton d-block h-100 rounded" style="background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%); background-size: 200% 100%; animation: loading 1.5s infinite;"></div>
        `).join('');
    }
}

/**
 * Clear form inputs
 */
function clearFormInputs(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
        form.classList.remove('was-validated');
    }
}

/**
 * Show confirmation dialog
 */
function showConfirmDialog(message, onConfirm, onCancel) {
    const modal = new bootstrap.Modal(document.createElement('div'));
    
    const confirmed = confirm(message);
    if (confirmed && onConfirm) {
        onConfirm();
    } else if (!confirmed && onCancel) {
        onCancel();
    }
}

/**
 * Disable form submission button to prevent double submission
 */
function preventDoubleSubmit(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processing...';
                
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || 'Submit';
                }, 3000);
            }
        });
    }
}

/**
 * Export to CSV
 */
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const rows = [];
    const cells = table.querySelectorAll('tr');
    
    cells.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const csvCols = Array.from(cols).map(col => col.textContent);
        rows.push(csvCols.join(','));
    });
    
    const csvContent = 'data:text/csv;charset=utf-8,' + rows.join('\n');
    const link = document.createElement('a');
    link.setAttribute('href', encodeURI(csvContent));
    link.setAttribute('download', filename);
    link.click();
}

/**
 * Animate counting up to a number
 */
function animateCountUp(elementId, targetNumber, duration = 2000) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const start = 0;
    const increment = targetNumber / (duration / 10);
    let current = start;
    
    const interval = setInterval(() => {
        current += increment;
        if (current >= targetNumber) {
            element.textContent = formatNumber(Math.floor(targetNumber));
            clearInterval(interval);
        } else {
            element.textContent = formatNumber(Math.floor(current));
        }
    }, 10);
}

// Export functions for use in other scripts
window.FarmersConnect = {
    showToast,
    copyToClipboard,
    formatDate,
    clearFormInputs,
    validateNumericInput,
    preventDoubleSubmit,
    exportTableToCSV,
    animateCountUp,
    fetchWithCsrf
};
