/**
 * File Manager - Handles file upload and management
 * @module file-manager
 */

/**
 * Handles file upload with validation and error handling
 * @param {Event} event - File input change event
 */
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file
    const validation = window.UIUtils.validateFile(file);
    if (!validation.valid) {
        window.UIUtils.showError('uploadResult', validation.error);
        return;
    }

    const resultDiv = 'uploadResult';
    window.UIUtils.showLoading(resultDiv, 'Uploading...');

    const nameInput = document.getElementById('uploadName');
    const desiredName = nameInput ? nameInput.value.trim() : '';

    try {
        const result = await window.API.uploadFile(file, desiredName);
        window.UIUtils.showSuccess(
            resultDiv,
            `${result.message}: ${result.filename} (${window.UIUtils.formatFileSize(result.size)})`
        );

        // Refresh file list
        await loadFileList();

        // Clear file input
        event.target.value = '';
        if (nameInput) {
            nameInput.value = '';
        }
    } catch (error) {
        window.UIUtils.showAPIError(resultDiv, error);
    }
}

/**
 * Loads and displays list of uploaded files
 */
async function loadFileList() {
    try {
        const data = await window.API.getFiles();
        const fileList = document.getElementById('fileList');

        if (!data.files || data.files.length === 0) {
            fileList.innerHTML = '<p style="text-align: center; color: #666;">No files uploaded yet</p>';
            return;
        }

        fileList.innerHTML = data.files.map(file => {
            const isPdf = file.file_type === 'pdf';
            const icon = isPdf ? '📕' : '📄';
            const action = isPdf
                ? `<a class="btn secondary" href="/api/files/${encodeURIComponent(file.filename)}" target="_blank" rel="noopener">Download</a>`
                : `<a class="btn secondary" href="/api/files/${encodeURIComponent(file.filename)}" target="_blank" rel="noopener">View</a>`;

            return `
                <div class="card">
                    <h3>${icon} ${file.filename}</h3>
                    <p>Type: ${file.file_type}</p>
                    <p>Size: ${window.UIUtils.formatFileSize(file.size)}</p>
                    <p>Modified: ${window.UIUtils.formatDate(file.modified)}</p>
                    ${action}
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading files:', error);
        // Don't show error to user - silent failure for background refresh
    }
}

/**
 * Populates file select dropdown
 */
async function populateFileSelect() {
    try {
        const data = await window.API.getFiles();
        const select = document.getElementById('fileSelect');

        const markdownFiles = data.files.filter(file => file.file_type === 'markdown');
        select.innerHTML = '<option value="">Choose a file...</option>' +
            markdownFiles.map(file =>
                `<option value="${file.filename}">${file.filename}</option>`
            ).join('');
    } catch (error) {
        console.error('Error loading files for select:', error);
    }
}

// Export functions
window.FileManager = {
    handleFileUpload,
    loadFileList,
    populateFileSelect
};
