/**
 * roadmap.js
 * Handles roadmap display, topic expansion, assignment submission
 */

// Sample roadmap data structure (this should come from the backend)
let roadmapData = null;
let currentAssignment = null;
let currentTopics = []; // Store the current topics array for access across functions

// Initialize on page load
// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadUserProgress();
    loadUserCourses();
    loadRoadmapData();
});

/**
 * Load user progress statistics
 */
async function loadUserProgress() {
    try {
        const token = localStorage.getItem('token');

        if (!token) {
            window.location.href = '/login/';
            return;
        }

        const response = await fetch('/api/assignments/progress/', {
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            updateProgressDisplay(data);
        } else {
            console.error('Failed to load progress');
        }
    } catch (error) {
        console.error('Error loading progress:', error);
    }
}

/**
 * Update progress overview display
 */
function updateProgressDisplay(data) {
    document.getElementById('completionPercentage').textContent = `${data.completion_percentage}%`;
    document.getElementById('completedCount').textContent = data.completed;
    document.getElementById('pendingCount').textContent = data.pending;
    document.getElementById('totalScore').textContent = data.total_score;

    // Update time if element exists
    const timeEl = document.getElementById('totalTime');
    if (timeEl && data.total_time_spent !== undefined) {
        timeEl.textContent = formatTime(data.total_time_spent);
    }
}

/**
 * Format minutes into Xh Ym
 */
function formatTime(minutes) {
    if (!minutes) return '0m';
    const h = Math.floor(minutes / 60);
    const m = minutes % 60;
    if (h > 0) return `${h}h ${m}m`;
    return `${m}m`;
}

// Listen for live time updates
window.addEventListener('timeUpdated', (e) => {
    const timeEl = document.getElementById('totalTime');
    if (timeEl && e.detail.totalTime) {
        timeEl.textContent = formatTime(e.detail.totalTime);
    }
});

/**
 * Load roadmap data from generated roadmap
 * This should be called after assessment completion
 */
async function loadRoadmapData() {
    try {
        const token = localStorage.getItem('token');

        if (!token) {
            window.location.href = '/login/';
            return;
        }

        // Try to get roadmap from localStorage
        const storedRoadmap = localStorage.getItem('latestRoadmap');

        console.log('Stored roadmap exists:', !!storedRoadmap);

        if (storedRoadmap) {
            try {
                roadmapData = JSON.parse(storedRoadmap);
                console.log('Parsed roadmap data:', roadmapData);
                displayRoadmap(roadmapData);
            } catch (parseError) {
                console.error('Error parsing roadmap:', parseError);
                showEmptyRoadmapMessage();
            }
        } else {
            console.warn('No roadmap found in localStorage');
            // Show message to generate roadmap first
            showEmptyRoadmapMessage();
        }
    } catch (error) {
        console.error('Error loading roadmap:', error);
        showEmptyRoadmapMessage();
    }
}


/**
 * Load list of user's active courses/roadmaps
 */
async function loadUserCourses() {
    const listContainer = document.getElementById('courseList');
    if (!listContainer) return;

    try {
        const token = localStorage.getItem('token');
        if (!token) return;

        const response = await fetch('/api/roadmaps/user/', {
            headers: { 'Authorization': `Token ${token}` }
        });

        if (response.ok) {
            const courses = await response.json();
            renderCourseList(courses);
        } else {
            console.warn('Failed to load courses, status:', response.status);
            listContainer.innerHTML = '<div class="empty-state-sidebar">Failed to load courses</div>';
        }
    } catch (e) {
        console.error('Error loading courses:', e);
        listContainer.innerHTML = '<div class="empty-state-sidebar">Error loading courses</div>';
    }
}

/**
 * Render the sidebar list of courses
 */
function renderCourseList(courses) {
    const listContainer = document.getElementById('courseList');
    if (!listContainer) return;
    listContainer.innerHTML = '';

    if (courses.length === 0) {
        listContainer.innerHTML = `
            <div class="empty-state-sidebar">
                <p>No active roadmaps found.</p>
                <a href="/courses/" style="font-size:0.9em; color: var(--primary-color);">Start a new course</a>
            </div>
        `;
        showEmptyRoadmapMessage();
        return;
    }

    courses.forEach((course) => {
        const item = document.createElement('div');
        item.className = 'course-item';
        item.dataset.id = course.id;

        item.innerHTML = `
            <div class="course-item-header">
                <span class="course-title">${course.title}</span>
                <span class="course-level" style="text-transform: capitalize;">${course.level}</span>
            </div>
            <span class="course-date">Started ${new Date(course.created_at).toLocaleDateString()}</span>
        `;
        item.onclick = () => loadCourseRoadmap(course.id, item);
        listContainer.appendChild(item);
    });
}

/**
 * Load specific roadmap details when a course is selected
 */
async function loadCourseRoadmap(assessmentId, element) {
    if (!assessmentId) return;

    // Highlight active sidebar item
    document.querySelectorAll('.course-item').forEach(el => el.classList.remove('active'));
    if (element) {
        element.classList.add('active');
    }

    const container = document.getElementById('roadmapTopics');
    container.innerHTML = `
        <div class="loading-state">
            <div class="spinner"></div>
            <p>Loading roadmap...</p>
        </div>
    `;

    try {
        const token = localStorage.getItem('token');
        const url = `/api/roadmaps/${assessmentId}/`;

        const response = await fetch(url, {
            headers: { 'Authorization': `Token ${token}` }
        });

        if (response.ok) {
            const data = await response.json();
            if (data.roadmap) {
                // Save to localStorage for persistence
                localStorage.setItem('latestRoadmap', JSON.stringify(data.roadmap));
                displayRoadmap(data.roadmap);
            } else {
                throw new Error('No roadmap data in response');
            }
        } else {
            throw new Error('Failed to fetch roadmap details');
        }
    } catch (e) {
        console.error('Error loading roadmap:', e);
        showEmptyRoadmapMessage();
    }
}

/**
 * Display the roadmap with topics
 */
function displayRoadmap(data) {
    const container = document.getElementById('roadmapTopics');

    console.log('Displaying roadmap data:', data);
    console.log('Data keys:', Object.keys(data));

    // Handle different roadmap structures
    let topics = [];

    // Try different possible structures
    if (data.learning_path && Array.isArray(data.learning_path) && data.learning_path.length > 0) {
        console.log('Found learning_path');
        topics = data.learning_path;
    } else if (data.weeks && Array.isArray(data.weeks) && data.weeks.length > 0) {
        console.log('Found weeks array');
        // Check if weeks is the topics or contains topics
        if (data.weeks[0].learning_path) {
            // Weeks contain learning_path
            topics = data.weeks.flatMap(week => week.learning_path || []);
        } else {
            // Weeks ARE the topics
            topics = data.weeks;
        }
    } else if (data.roadmap_structure && Array.isArray(data.roadmap_structure) && data.roadmap_structure.length > 0) {
        console.log('Found roadmap_structure');
        topics = data.roadmap_structure;
    } else if (data.topics && Array.isArray(data.topics) && data.topics.length > 0) {
        console.log('Found topics array');
        topics = data.topics;
    } else {
        // Try to find any array property
        console.log('Searching all properties for topics...');
        for (const key in data) {
            if (Array.isArray(data[key]) && data[key].length > 0) {
                console.log(`Found array property: ${key} with ${data[key].length} items`);
                topics = data[key];
                break;
            }
        }
    }

    console.log('Extracted topics:', topics);
    console.log('Topics count:', topics.length);

    if (topics.length === 0) {
        console.warn('No topics found in roadmap data');
        showEmptyRoadmapMessage();
        return;
    }

    // Store topics globally so loadTopicDetails can access them
    currentTopics = topics;
    console.log('Stored currentTopics:', currentTopics);

    // Update page title with course/skill info
    const courseInfo = data.course_name || data.subject || data.topic || '';
    const skillLevel = data.skill_level || data.level || '';

    if (courseInfo) {
        const titleEl = document.getElementById('roadmapTitle');
        const subtitleEl = document.getElementById('roadmapSubtitle');

        if (titleEl) {
            titleEl.textContent = `📚 ${courseInfo} Learning Roadmap`;
        }
        if (subtitleEl && skillLevel) {
            subtitleEl.textContent = `${skillLevel.charAt(0).toUpperCase() + skillLevel.slice(1)} Level - Track your progress and complete assignments`;
        }
    }

    container.innerHTML = '';

    topics.forEach((topic, index) => {
        console.log(`Creating card for topic ${index}:`, topic);
        const topicCard = createTopicCard(topic, index);
        container.appendChild(topicCard);
    });
}

/**
 * Create a topic card element
 */
function createTopicCard(topic, index) {
    const card = document.createElement('div');
    card.className = 'topic-card';

    // Extract topic name from various possible properties
    const topicName = topic.topic || topic.name || topic.title || `Topic ${index + 1}`;
    const weekNumber = topic.week || topic.week_number || (index + 1);
    const duration = topic.duration || topic.estimated_hours || topic.time_estimate || 'Duration varies';

    console.log(`Topic ${index}: name="${topicName}", week=${weekNumber}`);

    card.innerHTML = `
        <div class="topic-header" onclick="toggleTopic(${index})">
            <div class="topic-title">
                <h3>Week ${weekNumber}: ${topicName}</h3>
                <p class="topic-duration">${duration}</p>
            </div>
            <div class="topic-expand-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M6 9l6 6 6-6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
        </div>
        <div class="topic-content" id="topic-content-${index}" style="display: none;">
            <div class="loading-spinner" id="loading-${index}">
                <div class="spinner"></div>
                <p>Loading resources and assignments...</p>
            </div>
            <div class="topic-details" id="details-${index}" style="display: none;"></div>
        </div>
    `;

    return card;
}

/**
 * Toggle topic expansion and load details
 */
async function toggleTopic(index) {
    const content = document.getElementById(`topic-content-${index}`);
    const details = document.getElementById(`details-${index}`);
    const loading = document.getElementById(`loading-${index}`);

    if (content.style.display === 'none') {
        // Expand topic
        content.style.display = 'block';

        // Load topic details if not already loaded
        if (!details.hasChildNodes()) {
            loading.style.display = 'block';
            await loadTopicDetails(index);
        }
    } else {
        // Collapse topic
        content.style.display = 'none';
    }
}

/**
 * Load topic details (resources and assignments) from backend
 */
async function loadTopicDetails(index) {
    try {
        const token = localStorage.getItem('token');

        // Use currentTopics instead of roadmapData.learning_path
        if (!currentTopics || !currentTopics[index]) {
            console.error('Topic not found at index:', index);
            displayTopicDetails(index, null, {});
            return;
        }

        const topic = currentTopics[index];
        const topicName = topic.topic || topic.name || topic.title;

        console.log('Loading details for topic:', topicName);

        const response = await fetch(`/api/roadmap/topic-detail/?topic=${encodeURIComponent(topicName)}`, {
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            displayTopicDetails(index, data, topic);
        } else {
            console.warn('Failed to load topic details from API');
            displayTopicDetails(index, null, topic);
        }
    } catch (error) {
        console.error('Error loading topic details:', error);
        displayTopicDetails(index, null, currentTopics[index] || {});
    }
}

/**
 * Display topic details (resources and assignments)
 */
function displayTopicDetails(index, data, topic) {
    const details = document.getElementById(`details-${index}`);
    const loading = document.getElementById(`loading-${index}`);

    loading.style.display = 'none';
    details.style.display = 'block';

    let html = '';

    console.log('Displaying topic details:', { topic, data });

    // Display subtopics/learning objectives if available
    const learningPoints = topic.subtopics || topic.learning_objectives || topic.objectives || topic.focus_areas || [];
    if (learningPoints.length > 0) {
        html += `
            <div class="subtopics-section">
                <h4>📖 What You'll Learn</h4>
                <ul class="subtopics-list">
                    ${learningPoints.map(item => `<li>${item}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    // Display resources from API or from topic data
    let resources = [];
    if (data && data.resources && data.resources.length > 0) {
        resources = data.resources;
    } else if (topic.resources && topic.resources.length > 0) {
        resources = topic.resources;
    }

    if (resources.length > 0) {
        html += `
            <div class="resources-section">
                <h4>📚 Learning Resources</h4>
                <div class="resources-list">
                    ${resources.map(resource => {
            // Determine resource type and title
            const type = (resource.resource_type || resource.type || '').toLowerCase();
            const title = resource.title || 'Learning Resource';

            // Check if URL is valid (not undefined, null, empty, or 'undefined' string)
            const hasValidUrl = resource.url &&
                resource.url !== 'undefined' &&
                resource.url !== 'null' &&
                resource.url.trim() !== '';

            let destinationUrl = '';
            let linkText = '';
            let linkClass = 'resource-link';

            if (hasValidUrl) {
                destinationUrl = resource.url;
                linkText = 'View Resource';
            } else {
                // Generate dynamic search link based on type
                if (type.includes('video') || type.includes('youtube')) {
                    destinationUrl = `https://www.youtube.com/results?search_query=${encodeURIComponent(title + ' tutorial')}`;
                    linkText = 'Search Video';
                    linkClass += ' youtube-link';
                } else {
                    destinationUrl = `https://www.google.com/search?q=${encodeURIComponent(title + ' tutorial')}`;
                    linkText = 'Search Google';
                    linkClass += ' google-link';
                }
            }

            return `
                        <div class="resource-item">
                            <div class="resource-icon">${getResourceIcon(type)}</div>
                            <div class="resource-details">
                                <h5>${title}</h5>
                                ${resource.description ? `<p>${resource.description}</p>` : ''}
                                ${resource.time_estimate ? `<small>⏱️ ${resource.time_estimate}</small>` : ''}
                            </div>
                            <a href="${destinationUrl}" target="_blank" rel="noopener noreferrer" class="${linkClass}">
                                ${linkText}
                            </a>
                        </div>
                        `;
        }).join('')}
                </div>
            </div>
        `;
    }

    // Display assignments
    if (data && data.assignments && data.assignments.length > 0) {
        html += `
            <div class="assignments-section">
                <h4>✏️ Assignments (${data.assignments.length})</h4>
                <div class="assignments-list">
                    ${data.assignments.map(assignment => `
                        <div class="assignment-item">
                            <div class="assignment-header">
                                <h5>${assignment.title}</h5>
                                <div class="assignment-badges">
                                    <span class="badge difficulty-${assignment.difficulty}">${assignment.difficulty}</span>
                                    <span class="badge points">${assignment.total_points} pts</span>
                                </div>
                            </div>
                            <p>${assignment.description}</p>
                            <div class="assignment-footer">
                                <span class="time-estimate">⏱️ ${assignment.estimated_hours}h</span>
                                ${getAssignmentStatusBadge(assignment)}
                                <button class="btn btn-small btn-primary" onclick='openAssignmentModal(${JSON.stringify(assignment)})'>
                                    ${assignment.user_submission ? 'View Details' : 'Start Assignment'}
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    } else if (data && data.completion_stats && data.completion_stats.total > 0 && data.completion_stats.completed === data.completion_stats.total) {
        html += `
            <div class="all-complete-message">
                <div class="success-icon">✅</div>
                <h4>All Assignments Completed!</h4>
                <p>Great job! You've completed all assignments for this topic.</p>
            </div>
        `;
    }

    // If no content at all, show helpful message
    if (!html || html.trim() === '') {
        html = `
            <div class="no-content-message">
                <p>📚 <strong>Learning resources are being generated for this topic.</strong></p>
                <p>In the meantime, you can:</p>
                <ul style="text-align: left; margin: 20px auto; max-width: 400px;">
                    <li>Search for "${topic.topic || topic.name}" tutorials online</li>
                    <li>Check official documentation</li>
                    <li>Explore video courses on YouTube or Udemy</li>
                </ul>
            </div>
        `;
    }

    details.innerHTML = html;
}

/**
 * Get resource icon based on type
 */
function getResourceIcon(type) {
    const icons = {
        'document': '📄',
        'video': '🎥',
        'article': '📰',
        'link': '🔗'
    };
    return icons[type] || '📁';
}

/**
 * Get assignment status badge
 */
function getAssignmentStatusBadge(assignment) {
    if (!assignment.user_submission) {
        return '<span class="status-badge not-started">⏳ Not Started</span>';
    }

    const status = assignment.user_submission.status;
    const badges = {
        'submitted': '<span class="status-badge submitted">📤 Submitted</span>',
        'graded': '<span class="status-badge graded">📋 Graded</span>',
        'completed': '<span class="status-badge completed">✅ Completed</span>',
        'pending': '<span class="status-badge pending">⏳ Pending</span>'
    };

    return badges[status] || '<span class="status-badge">-</span>';
}

/**
 * Open assignment modal
 */
function openAssignmentModal(assignment) {
    currentAssignment = assignment;

    document.getElementById('modalTitle').textContent = assignment.title;
    document.getElementById('modalDescription').textContent = assignment.description;
    document.getElementById('modalInstructions').innerHTML = assignment.instructions.replace(/\n/g, '<br>');
    document.getElementById('modalDifficulty').textContent = assignment.difficulty;
    document.getElementById('modalDifficulty').className = `badge difficulty-badge difficulty-${assignment.difficulty}`;
    document.getElementById('modalPoints').textContent = `${assignment.total_points} Points`;
    document.getElementById('modalTime').textContent = `${assignment.estimated_hours} Hours`;
    document.getElementById('assignmentId').value = assignment.id;

    // If already submitted, show the submission
    if (assignment.user_submission) {
        // You can pre-fill form or show submission status
        document.getElementById('submissionText').value = assignment.user_submission.submission_text || '';
        document.getElementById('submissionLink').value = assignment.user_submission.submission_link || '';
    } else {
        document.getElementById('submissionText').value = '';
        document.getElementById('submissionLink').value = '';
    }

    document.getElementById('assignmentModal').style.display = 'flex';
}

/**
 * Close assignment modal
 */
function closeAssignmentModal() {
    document.getElementById('assignmentModal').style.display = 'none';
    currentAssignment = null;
}

/**
 * Submit assignment
 */
async function submitAssignment(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const assignmentId = formData.get('assignment_id');
    const submissionText = formData.get('submission_text').trim();
    const submissionLink = formData.get('submission_link').trim();

    if (!submissionText && !submissionLink) {
        alert('Please provide either a text submission or a link.');
        return;
    }

    try {
        const token = localStorage.getItem('token');

        const response = await fetch('/api/assignments/submit/', {
            method: 'POST',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                assignment_id: assignmentId,
                submission_text: submissionText,
                submission_link: submissionLink
            })
        });

        if (response.ok) {
            const result = await response.json();
            alert('✅ Assignment submitted successfully!');
            closeAssignmentModal();

            // Reload roadmap to update assignment status
            loadRoadmapData();
            loadUserProgress();
        } else {
            const error = await response.json();
            alert(`Failed to submit assignment: ${error.error || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error submitting assignment:', error);
        alert('An error occurred while submitting. Please try again.');
    }
}

/**
 * Show empty roadmap message
 */
function showEmptyRoadmapMessage() {
    const container = document.getElementById('roadmapTopics');
    container.innerHTML = `
        <div class="empty-roadmap">
            <div class="empty-icon">📚</div>
            <h3>No Roadmap Available</h3>
            <p>Complete an assessment first to generate your personalized learning roadmap.</p>
            <a href="/courses/" class="btn btn-primary">Take Assessment</a>
        </div>
    `;
}

// Close modal when clicking outside
window.onclick = function (event) {
    const modal = document.getElementById('assignmentModal');
    if (event.target === modal) {
        closeAssignmentModal();
    }
}
