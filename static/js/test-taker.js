/**
 * Test Taker - Handles test taking and grading
 * @module test-taker
 */

let currentExam = null;

/**
 * Loads exam for taking test
 */
async function loadExamForTest() {
    const examId = document.getElementById('examSelect')?.value;
    if (!examId) {
        window.UIUtils.showError('testResult', 'Please select an exam first');
        return;
    }

    const resultDiv = 'testResult';
    window.UIUtils.showLoading(resultDiv, 'Loading exam...');

    try {
        currentExam = await window.API.getExam(examId);

        const testArea = document.getElementById('testArea');
        if (!testArea) return;

        testArea.innerHTML = `
            <h3>Exam: ${currentExam.exam_id}</h3>
            <p style="margin-bottom: 20px;"><strong>Total Questions:</strong> ${currentExam.questions.length}</p>
            <form id="testForm">
                ${currentExam.questions.map((q, i) => {
                    let badge = '';
                    if (q.type === 'single_choice') badge = '<span class="question-type-badge badge-single">Single</span>';
                    if (q.type === 'multiple_choice') badge = '<span class="question-type-badge badge-multiple">Multiple</span>';
                    if (q.type === 'open_ended') badge = '<span class="question-type-badge badge-open">Open-Ended</span>';

                    return `
                        <div class="question ${q.type === 'open_ended' ? 'open-ended' : ''}">
                            <h4>Question ${i + 1} ${badge}</h4>
                            <p><strong>${q.stem}</strong></p>
                            ${q.type === 'open_ended' ? `
                                <textarea
                                    class="text-answer"
                                    id="answer-${i}"
                                    placeholder="Type your answer here (2-4 sentences)..."
                                    required
                                ></textarea>
                            ` : q.options.map((opt, j) => `
                                <label class="option">
                                    <input type="${q.type === 'single_choice' ? 'radio' : 'checkbox'}"
                                           name="q${i}" value="${j}"
                                           onchange="window.TestTaker.updateOptionStyles()">
                                    ${opt}
                                </label>
                            `).join('')}
                        </div>
                    `;
                }).join('')}
                <button type="submit" class="btn" style="width: 100%; padding: 15px; font-size: 18px;">
                    ✅ Submit Answers
                </button>
            </form>
        `;

        document.getElementById('testForm').onsubmit = submitTest;
        document.getElementById(resultDiv).innerHTML = '';
    } catch (error) {
        window.UIUtils.showAPIError(resultDiv, error);
    }
}

/**
 * Updates visual state of selected options
 */
function updateOptionStyles() {
    document.querySelectorAll('.option').forEach(opt => {
        const input = opt.querySelector('input');
        if (input && input.checked) {
            opt.classList.add('selected');
        } else {
            opt.classList.remove('selected');
        }
    });
}

/**
 * Submits test answers for grading
 * @param {Event} event - Form submit event
 */
async function submitTest(event) {
    event.preventDefault();

    if (!currentExam) {
        window.UIUtils.showError('testResult', 'No exam loaded');
        return;
    }

    const answers = [];
    currentExam.questions.forEach((q, i) => {
        if (q.type === 'open_ended') {
            const textarea = document.getElementById(`answer-${i}`);
            if (textarea && textarea.value.trim()) {
                answers.push({
                    question_id: q.id,
                    text_answer: textarea.value.trim()
                });
            }
        } else {
            const inputs = document.querySelectorAll(`input[name="q${i}"]:checked`);
            const choice = Array.from(inputs).map(inp => parseInt(inp.value));

            if (choice.length > 0) {
                answers.push({
                    question_id: q.id,
                    choice: choice
                });
            }
        }
    });

    if (answers.length === 0) {
        window.UIUtils.showError('testResult', 'Please answer at least one question!');
        return;
    }

    const resultDiv = 'testResult';
    window.UIUtils.showLoading(resultDiv, 'Grading your answers with AI...');

    try {
        const result = await window.API.gradeExam(currentExam.exam_id, answers);

        const resultHtml = `
            <div class="result success">
                <h2>🎉 Results</h2>
                <p style="font-size: 24px; margin: 20px 0;">
                    Score: <strong>${result.summary.score_percent.toFixed(1)}%</strong>
                </p>
                <p>Correct: ${result.summary.correct} / ${result.summary.total}</p>

                <div style="margin-top: 30px;">
                    <h3>📊 Detailed Results</h3>
                    ${result.per_question.map((r, i) => {
                        const question = currentExam.questions.find(q => q.id === r.question_id);
                        return `
                            <div class="question ${question.type === 'open_ended' ? 'open-ended' : ''}">
                                <h4>
                                    Question ${i + 1}:
                                    ${r.is_correct ? '✅ Correct' : '❌ Incorrect'}
                                    ${r.partial_credit < 1 && r.partial_credit > 0 ?
                                        `<span style="color: #f39c12;">(${(r.partial_credit * 100).toFixed(0)}% credit)</span>`
                                        : ''}
                                </h4>
                                <p><strong>${question.stem}</strong></p>

                                ${question.type === 'open_ended' ? `
                                    <div class="feedback-box">
                                        <h5>📝 Your Answer:</h5>
                                        <p>${r.given_text || '(No answer provided)'}</p>
                                        <h5 style="margin-top: 15px;">💬 AI Feedback:</h5>
                                        <p>${r.feedback || 'No feedback available'}</p>
                                        <p style="margin-top: 10px;"><strong>Score: ${(r.partial_credit * 100).toFixed(0)}%</strong></p>
                                    </div>
                                ` : `
                                    <p style="margin-top: 10px;">
                                        <strong>Your answer:</strong>
                                        ${r.given.map(idx => question.options[idx]).join(', ') || '(No answer)'}
                                    </p>
                                    <p>
                                        <strong>Correct answer:</strong>
                                        ${r.expected.map(idx => question.options[idx]).join(', ')}
                                    </p>
                                `}
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;

        document.getElementById(resultDiv).innerHTML = resultHtml;
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    } catch (error) {
        window.UIUtils.showAPIError(resultDiv, error);
    }
}

// Export functions
window.TestTaker = {
    loadExamForTest,
    updateOptionStyles,
    submitTest
};
