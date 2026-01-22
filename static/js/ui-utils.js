/**
 * UI Utilities - Helper functions for UI feedback and state management
 * @module ui-utils
 */

/**
 * Shows loading spinner in target element
 * @param {string} elementId - Target element ID
 * @param {string} message - Loading message
 */
function showLoading(elementId, message = 'Loading...') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                ${message}
            </div>
        `;
    }
}

/**
 * Shows success message in target element
 * @param {string} elementId - Target element ID
 * @param {string} message - Success message
 * @param {boolean} icon - Show checkmark icon
 */
function showSuccess(elementId, message, icon = true) {
    const element = document.getElementById(elementId);
    if (element) {
        const iconHtml = icon ? '✅ ' : '';
        element.innerHTML = `
            <div class="result success">
                ${iconHtml}${message}
            </div>
        `;
    }
}

/**
 * Shows error message in target element
 * @param {string} elementId - Target element ID
 * @param {string} message - Error message
 * @param {Error} error - Optional error object for logging
 */
function showError(elementId, message, error = null) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="result error">
                ❌ ${message}
            </div>
        `;
    }

    // Log to console for debugging
    if (error) {
        console.error('Error:', message, error);
    }
}

/**
 * Shows user-friendly error message based on error type
 * @param {string} elementId - Target element ID
 * @param {Error} error - Error object
 */
function showAPIError(elementId, error) {
    let message = 'An unexpected error occurred. Please try again.';

    if (window.APIError && error instanceof window.APIError) {
        if (error.status === 0) {
            message = 'Cannot connect to server. Please check your internet connection.';
        } else if (error.status === 400) {
            message = `Invalid input: ${error.message}`;
        } else if (error.status === 404) {
            message = 'Resource not found.';
        } else if (error.status === 413) {
            message = 'File too large. Maximum size is 10MB.';
        } else if (error.status === 422) {
            // Validation error - extract details from FastAPI response
            if (error.response && error.response.detail) {
                if (Array.isArray(error.response.detail)) {
                    // FastAPI validation errors are arrays
                    const errors = error.response.detail.map(err => {
                        const field = err.loc ? err.loc.join('.') : 'unknown';
                        return `${field}: ${err.msg}`;
                    }).join('; ');
                    message = `Validation error: ${errors}`;
                } else if (typeof error.response.detail === 'string') {
                    message = `Validation error: ${error.response.detail}`;
                } else {
                    message = 'Invalid request data. Please check your input.';
                }
            } else {
                message = error.message || 'Invalid request data. Please check your input.';
            }
        } else if (error.status === 429) {
            message = 'Too many requests. Please wait a moment and try again.';
        } else if (error.status >= 500) {
            message = 'Server error. Please try again later.';
        } else {
            message = error.message;
        }
    } else {
        message = error.message || message;
    }

    showError(elementId, message, error);
}

/**
 * Validates file before upload
 * @param {File} file - File to validate
 * @returns {Object} Validation result {valid: boolean, error: string}
 */
function validateFile(file) {
    if (!file) {
        return { valid: false, error: 'No file selected' };
    }

    const lower = file.name.toLowerCase();
    if (!(lower.endsWith('.md') || lower.endsWith('.pdf'))) {
        return { valid: false, error: 'Only .md (Markdown) or .pdf files are allowed' };
    }

    // 10MB limit (matches backend)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        return { valid: false, error: `File too large. Maximum size is ${(maxSize / (1024 * 1024)).toFixed(0)}MB` };
    }

    return { valid: true };
}

/**
 * Validates exam configuration
 * @param {Object} config - Exam config to validate
 * @returns {Object} Validation result {valid: boolean, error: string}
 */
function validateExamConfig(config) {
    const { single_count, multiple_count, open_count } = config;

    const total = (single_count || 0) + (multiple_count || 0) + (open_count || 0);

    if (total === 0) {
        return { valid: false, error: 'Please specify at least one question' };
    }

    if (total > 100) {
        return { valid: false, error: 'Maximum 100 questions allowed' };
    }

    return { valid: true };
}

/**
 * Formats file size for display
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted size (e.g., "1.5 MB")
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Formats date for display
 * @param {number} timestamp - Unix timestamp
 * @returns {string} Formatted date
 */
function formatDate(timestamp) {
    return new Date(timestamp * 1000).toLocaleString();
}

/**
 * Debounces function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in ms
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export utilities
window.UIUtils = {
    showLoading,
    showSuccess,
    showError,
    showAPIError,
    validateFile,
    validateExamConfig,
    formatFileSize,
    formatDate,
    debounce
};
