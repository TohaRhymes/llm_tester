/**
 * Main Application - Entry point and initialization
 * @module main
 */

/**
 * Switches between tabs
 * @param {string} tabName - Tab name to switch to
 */
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));

    // Activate selected tab
    const clickedTab = event.target.closest('.tab');
    if (clickedTab) clickedTab.classList.add('active');

    const tabContent = document.getElementById(`${tabName}-tab`);
    if (tabContent) tabContent.classList.add('active');

    // Load data for specific tabs
    if (tabName === 'upload') {
        window.FileManager.loadFileList();
    }
    if (tabName === 'generate') {
        window.FileManager.loadFileList();
        window.FileManager.populateFileSelect();
    }
    if (tabName === 'exams') {
        window.ExamManager.loadExamList();
    }
    if (tabName === 'take') {
        window.ExamManager.loadExamList();
        window.ExamManager.populateExamSelect();
    }
}

/**
 * Initialize application on page load
 */
function initializeApp() {
    console.log('🎓 LLM Test Generator initialized');

    // Load initial data
    window.FileManager.loadFileList();

    // Set up event listeners for question count inputs
    const inputs = ['singleCount', 'multipleCount', 'openCount'];
    inputs.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('input', window.ExamManager.updateQuestionTotal);
        }
    });

    // Initialize total display
    window.ExamManager.updateQuestionTotal();

    console.log('✅ Application ready');
}

// Wait for DOM to be ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// Export for global access
window.switchTab = switchTab;
