/**
 * Exam Manager - Handles exam generation and management
 * @module exam-manager
 */

// Exam pagination state
let examSort = 'created';
let examOrder = 'desc';
let examPage = 1;
let examPageSize = 10;
let examMeta = { total_pages: 1 };

/**
 * Updates total questions counter
 */
function updateQuestionTotal() {
    const single = parseInt(document.getElementById('singleCount')?.value) || 0;
    const multiple = parseInt(document.getElementById('multipleCount')?.value) || 0;
    const open = parseInt(document.getElementById('openCount')?.value) || 0;

    const total = single + multiple + open;
    const display = document.getElementById('totalQuestionsDisplay');
    if (display) {
        display.textContent = total;
    }
}

/**
 * Generates exam from selected file
 */
async function generateExam() {
    const filename = document.getElementById('fileSelect')?.value;
    if (!filename) {
        window.UIUtils.showError('generateResult', 'Please select a file first');
        return;
    }

    const resultDiv = 'generateResult';
    window.UIUtils.showLoading(resultDiv, 'Generating exam with AI...');

    try {
        // Get file content
        const fileData = await window.API.getFileContent(filename);

        // Get configuration
        const singleCount = parseInt(document.getElementById('singleCount')?.value) || 0;
        const multipleCount = parseInt(document.getElementById('multipleCount')?.value) || 0;
        const openCount = parseInt(document.getElementById('openCount')?.value) || 0;
        const difficulty = document.getElementById('difficulty')?.value || 'mixed';
        const language = document.getElementById('language')?.value || 'en';
        const provider = document.getElementById('provider')?.value || 'openai';
        const modelName = document.getElementById('modelName')?.value?.trim() || null;

        // Validate config
        const validation = window.UIUtils.validateExamConfig({
            single_count: singleCount,
            multiple_count: multipleCount,
            open_count: openCount
        });

        if (!validation.valid) {
            window.UIUtils.showError(resultDiv, validation.error);
            return;
        }

        // Build request payload matching API schema
        const requestPayload = {
            markdown_content: fileData.content,
            config: {
                single_choice_count: singleCount,
                multiple_choice_count: multipleCount,
                open_ended_count: openCount,
                difficulty,
                language,
                provider
            }
        };

        // Add optional model name if provided
        if (modelName) {
            requestPayload.config.model_name = modelName;
        }

        // Generate exam
        const exam = await window.API.generateExam(requestPayload);

        window.UIUtils.showSuccess(
            resultDiv,
            `Exam generated successfully! ID: ${exam.exam_id} (${exam.questions.length} questions)`
        );

        // Refresh exam list
        await loadExamList();
    } catch (error) {
        window.UIUtils.showAPIError(resultDiv, error);
    }
}

/**
 * Loads and displays list of exams
 */
async function loadExamList() {
    try {
        const params = {
            sort_by: examSort,
            order: examOrder,
            page: examPage,
            page_size: examPageSize
        };

        const data = await window.API.getExams(params);
        examMeta = {
            total_pages: data.total_pages || 1,
            total: data.total || 0,
            page: data.page || 1
        };

        const examList = document.getElementById('examList');
        const examPageInfo = document.getElementById('examPageInfo');

        if (!data.exams || data.exams.length === 0) {
            examList.innerHTML = '<p style="text-align: center; color: #666;">No exams generated yet</p>';
            if (examPageInfo) examPageInfo.innerHTML = '';
            return;
        }

        // Update pagination info
        if (examPageInfo) {
            examPageInfo.innerHTML = `
                Page ${examMeta.page} of ${examMeta.total_pages} (${examMeta.total} total exams)
            `;
        }

        examList.innerHTML = `
            <table class="exam-table">
                <thead>
                    <tr>
                        <th>Exam ID</th>
                        <th>Questions</th>
                        <th>Created</th>
                        <th>Size</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.exams.map(exam => `
                        <tr>
                            <td><strong>${exam.exam_id}</strong></td>
                            <td>-</td>
                            <td>${window.UIUtils.formatDate(exam.created)}</td>
                            <td>${window.UIUtils.formatFileSize(exam.size)}</td>
                            <td>
                                <button class="btn secondary" onclick="window.ExamManager.viewExam('${exam.exam_id}')">
                                    👁️ View
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        console.error('Error loading exams:', error);
    }
}

/**
 * Views exam details
 * @param {string} examId - Exam ID to view
 */
async function viewExam(examId) {
    try {
        const exam = await window.API.getExam(examId);

        const modalContent = `
            <h2>Exam: ${exam.exam_id}</h2>
            <p><strong>Total Questions:</strong> ${exam.questions.length}</p>
            <div style="max-height: 400px; overflow-y: auto;">
                ${exam.questions.map((q, i) => `
                    <div class="question ${q.type === 'open_ended' ? 'open-ended' : ''}">
                        <h4>Question ${i + 1}: ${q.type}</h4>
                        <p><strong>${q.stem}</strong></p>
                        ${q.type !== 'open_ended' ?
                            q.options.map((opt, j) => `
                                <p>${j + 1}. ${opt} ${q.correct.includes(j) ? '✓' : ''}</p>
                            `).join('') :
                            `<p><em>Open-ended question</em></p>`
                        }
                    </div>
                `).join('')}
            </div>
        `;

        // Show in result div (simple approach)
        const resultDiv = document.getElementById('examViewResult');
        if (resultDiv) {
            resultDiv.innerHTML = modalContent;
            resultDiv.scrollIntoView({ behavior: 'smooth' });
        }
    } catch (error) {
        window.UIUtils.showAPIError('examViewResult', error);
    }
}

/**
 * Changes exam sort/filter
 */
function changeExamSort() {
    examSort = document.getElementById('examSort')?.value || 'created';
    examOrder = document.getElementById('examOrder')?.value || 'desc';
    examPageSize = parseInt(document.getElementById('examPageSize')?.value) || 10;
    examPage = 1;
    loadExamList();
}

/**
 * Goes to next exam page
 */
function nextExamPage() {
    if (examPage < examMeta.total_pages) {
        examPage += 1;
        loadExamList();
    }
}

/**
 * Goes to previous exam page
 */
function prevExamPage() {
    if (examPage > 1) {
        examPage -= 1;
        loadExamList();
    }
}

/**
 * Populates exam select for test taking
 */
async function populateExamSelect() {
    try {
        const data = await window.API.getExams({ page_size: 100 });
        const select = document.getElementById('examSelect');

        if (select) {
            select.innerHTML = '<option value="">Choose an exam...</option>' +
                data.exams.map(exam =>
                    `<option value="${exam.exam_id}">${exam.exam_id} (${window.UIUtils.formatDate(exam.created)})</option>`
                ).join('');
        }
    } catch (error) {
        console.error('Error loading exams for select:', error);
    }
}

/**
 * Imports exam from JSON
 */
async function importExam() {
    const importText = document.getElementById('importText')?.value.trim();
    if (!importText) {
        window.UIUtils.showError('importResult', 'Please paste exam JSON');
        return;
    }

    const resultDiv = 'importResult';
    window.UIUtils.showLoading(resultDiv, 'Importing exam...');

    try {
        const examData = JSON.parse(importText);
        await window.API.importExam(examData);

        window.UIUtils.showSuccess(resultDiv, `Exam ${examData.exam_id} imported successfully!`);

        // Clear input and refresh list
        document.getElementById('importText').value = '';
        await loadExamList();
    } catch (error) {
        if (error instanceof SyntaxError) {
            window.UIUtils.showError(resultDiv, 'Invalid JSON format');
        } else {
            window.UIUtils.showAPIError(resultDiv, error);
        }
    }
}

// Export functions
window.ExamManager = {
    updateQuestionTotal,
    generateExam,
    loadExamList,
    viewExam,
    changeExamSort,
    nextExamPage,
    prevExamPage,
    populateExamSelect,
    importExam
};
