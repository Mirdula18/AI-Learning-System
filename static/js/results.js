/**
 * Results visualization and management
 */

class ResultsManager {
    constructor(data) {
        this.data = data;
        this.profile = data.learner_profile;
        this.evalResults = data.evaluation_results;
    }

    animateScore(targetScore, correct, total, duration = 2000) {
        return new Promise((resolve) => {
            let current = 0;
            const increment = targetScore / (duration / 20);
            const interval = setInterval(() => {
                current += increment;
                
                if (current >= targetScore) {
                    current = targetScore;
                    clearInterval(interval);
                    resolve();
                }

                // Update display
                const scoreDisplay = document.getElementById('scoreDisplay');
                if (scoreDisplay) {
                    scoreDisplay.textContent = `${Math.round(current)}%`;
                }

                // Update circle
                const scoreCircle = document.getElementById('scoreCircle');
                if (scoreCircle) {
                    const circumference = 2 * Math.PI * 90;
                    const offset = circumference - (current / 100) * circumference;
                    scoreCircle.style.strokeDashoffset = offset;
                    scoreCircle.style.transition = 'stroke-dashoffset 0.02s linear';
                }
            }, 20);
        });
    }

    renderSkillBadge() {
        const skillBadge = document.getElementById('skillBadge');
        if (!skillBadge) return;

        const icons = {
            'absolute_beginner': '🌱',
            'beginner': '🎓',
            'intermediate': '⚡',
            'advanced': '🚀'
        };

        const skillLevel = this.profile.skill_level;
        const icon = icons[skillLevel] || '🎯';
        const text = skillLevel.replace(/_/g, ' ').toUpperCase();

        skillBadge.innerHTML = `
            <span class="level-icon">${icon}</span>
            <span class="level-text">${text}</span>
        `;
        skillBadge.className = `skill-level-badge ${skillLevel}`;
    }

    renderPersonalMessage() {
        const messageEl = document.getElementById('personalMessage');
        if (messageEl) {
            messageEl.textContent = this.profile.personalized_message;
        }
    }

    renderDifficultyBreakdown() {
        const breakdown = this.evalResults.score_by_difficulty;

        ['beginner', 'intermediate', 'advanced'].forEach(level => {
            const data = breakdown[level];
            const percent = (data.correct / data.total) * 100;

            const scoreEl = document.getElementById(`${level}Score`);
            const progressEl = document.getElementById(`${level}Progress`);

            if (scoreEl) {
                scoreEl.textContent = `${data.correct}/${data.total}`;
            }
            if (progressEl) {
                progressEl.style.width = `${percent}%`;
            }
        });
    }

    renderStrengths() {
        const strengthsList = document.getElementById('strengthsList');
        if (!strengthsList) return;

        const html = this.profile.strengths.map(s => `
            <div class="strength-item">
                <div class="strength-header">
                    <span class="strength-topic">${s.topic}</span>
                    <span class="strength-percent">${s.proficiency_percent}%</span>
                </div>
                <div class="progress-bar small">
                    <div class="progress-fill" style="width: ${s.proficiency_percent}%"></div>
                </div>
                <p class="strength-note">${s.note}</p>
            </div>
        `).join('');

        strengthsList.innerHTML = html;
    }

    renderWeaknesses() {
        const weaknessesList = document.getElementById('weaknessesList');
        if (!weaknessesList) return;

        const html = this.profile.weaknesses.map(w => `
            <div class="weakness-item priority-${w.priority}">
                <div class="weakness-header">
                    <span class="weakness-topic">${w.topic}</span>
                    <span class="priority-badge">${w.priority} priority</span>
                </div>
                <div class="progress-bar small">
                    <div class="progress-fill warning" style="width: ${w.proficiency_percent}%"></div>
                </div>
                <p class="weakness-note">${w.note}</p>
            </div>
        `).join('');

        weaknessesList.innerHTML = html;
    }

    renderStats() {
        const weeksEl = document.getElementById('estimatedWeeks');
        if (weeksEl) {
            weeksEl.textContent = this.profile.estimated_weeks_to_proficiency;
        }
    }

    async render() {
        // Hide loading
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }

        // Show all sections
        const sections = [
            'scoreHero',
            'performanceSection',
            'insightsGrid',
            'nextStepsSection'
        ];

        sections.forEach(section => {
            const el = document.getElementById(section);
            if (el) el.style.display = 'block';
        });

        // Render components
        this.renderSkillBadge();
        this.renderPersonalMessage();
        this.renderDifficultyBreakdown();
        this.renderStrengths();
        this.renderWeaknesses();
        this.renderStats();

        // Update score display
        const scoreFraction = document.getElementById('scoreFraction');
        if (scoreFraction) {
            scoreFraction.textContent = 
                `${this.evalResults.total_correct}/${this.evalResults.total_questions} Correct`;
        }

        // Animate score
        await this.animateScore(
            this.evalResults.overall_score,
            this.evalResults.total_correct,
            this.evalResults.total_questions
        );
    }
}

// Global function for roadmap generation
function generateRoadmap() {
    alert('Roadmap generation feature will be implemented in the next phase!');
}
