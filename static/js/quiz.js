/**
 * Quiz management and interaction
 */

class QuizManager {
    constructor(quizData) {
        this.quizData = quizData;
        this.currentIndex = 0;
        this.userAnswers = {};
        this.startTime = Date.now();
        this.timerInterval = null;
        this.questionStartTimes = {};
    }

    getCurrentQuestion() {
        return this.quizData.questions[this.currentIndex];
    }

    getTotalQuestions() {
        return this.quizData.questions.length;
    }

    selectAnswer(questionId, answer) {
        if (!this.questionStartTimes[questionId]) {
            this.questionStartTimes[questionId] = Date.now();
        }

        this.userAnswers[questionId] = {
            answer: answer,
            timeSpent: Date.now() - this.questionStartTimes[questionId]
        };
    }

    getAnswer(questionId) {
        return this.userAnswers[questionId]?.answer || null;
    }

    hasAnswer(questionId) {
        return !!this.userAnswers[questionId];
    }

    getProgress() {
        return ((this.currentIndex + 1) / this.getTotalQuestions()) * 100;
    }

    getTotalTime() {
        return Math.floor((Date.now() - this.startTime) / 1000);
    }

    getUnansweredCount() {
        let count = 0;
        this.quizData.questions.forEach(q => {
            if (!this.hasAnswer(q.question_id)) {
                count++;
            }
        });
        return count;
    }

    getFormattedAnswers() {
        const formatted = {};
        Object.entries(this.userAnswers).forEach(([qId, data]) => {
            formatted[qId] = {
                answer: data.answer,
                timeSpent: data.timeSpent
            };
        });
        return formatted;
    }

    startTimer(callback) {
        this.timerInterval = setInterval(() => {
            const elapsed = this.getTotalTime();
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            
            if (callback) {
                callback(`${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`);
            }
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }
    }
}

// Utility function to escape HTML
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Utility function to show loading overlay
function showLoadingOverlay(message = 'Loading...') {
    const overlay = document.getElementById('loadingOverlay');
    const text = document.getElementById('loadingText');
    
    if (overlay && text) {
        text.textContent = message;
        overlay.style.display = 'flex';
    }
}

// Utility function to hide loading overlay
function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}
