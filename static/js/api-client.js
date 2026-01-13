/**
 * API Client - Centralized API communication with proper error handling
 * @module api-client
 */

const API_BASE = 'http://localhost:8000';

/**
 * Custom error class for API errors
 */
class APIError extends Error {
    constructor(message, status, response) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.response = response;
    }
}

/**
 * Makes an API request with proper error handling
 * @param {string} endpoint - API endpoint path
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} Response data
 * @throws {APIError} If request fails
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;

    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });

        const data = await response.json();

        if (!response.ok) {
            throw new APIError(
                data.detail || `HTTP Error ${response.status}`,
                response.status,
                data
            );
        }

        return data;
    } catch (error) {
        if (error instanceof APIError) {
            throw error;
        }

        // Network or parsing error
        throw new APIError(
            `Network error: ${error.message}`,
            0,
            null
        );
    }
}

/**
 * API methods for different endpoints
 */
const API = {
    /**
     * Upload a markdown file
     * @param {File} file - File to upload
     * @returns {Promise<Object>} Upload result
     */
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE}/api/upload`, {
            method: 'POST',
            body: formData  // Don't set Content-Type for FormData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new APIError(data.detail || 'Upload failed', response.status, data);
        }

        return data;
    },

    /**
     * Get list of uploaded files
     * @returns {Promise<Object>} Files list
     */
    async getFiles() {
        return apiRequest('/api/files');
    },

    /**
     * Get file content by filename
     * @param {string} filename - File name
     * @returns {Promise<Object>} File content
     */
    async getFileContent(filename) {
        return apiRequest(`/api/files/${encodeURIComponent(filename)}`);
    },

    /**
     * Generate exam from file
     * @param {Object} config - Exam configuration
     * @returns {Promise<Object>} Generated exam
     */
    async generateExam(config) {
        return apiRequest('/api/generate', {
            method: 'POST',
            body: JSON.stringify({ config })
        });
    },

    /**
     * Get list of exams with pagination
     * @param {Object} params - Query parameters
     * @returns {Promise<Object>} Exams list
     */
    async getExams(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest(`/api/exams${queryString ? '?' + queryString : ''}`);
    },

    /**
     * Get exam by ID
     * @param {string} examId - Exam ID
     * @returns {Promise<Object>} Exam data
     */
    async getExam(examId) {
        return apiRequest(`/api/exams/${encodeURIComponent(examId)}`);
    },

    /**
     * Grade exam answers
     * @param {string} examId - Exam ID
     * @param {Array} answers - User answers
     * @returns {Promise<Object>} Grading results
     */
    async gradeExam(examId, answers) {
        return apiRequest('/api/grade', {
            method: 'POST',
            body: JSON.stringify({ exam_id: examId, answers })
        });
    },

    /**
     * Import external exam
     * @param {Object} examData - Exam data to import
     * @returns {Promise<Object>} Import result
     */
    async importExam(examData) {
        return apiRequest('/api/import-exam', {
            method: 'POST',
            body: JSON.stringify(examData)
        });
    }
};

// Export for use in other modules
window.API = API;
window.APIError = APIError;
