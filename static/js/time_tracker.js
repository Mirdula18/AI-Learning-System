/**
 * Time Tracker Script
 * Tracks user activity and updates the backend every minute
 */
(function () {
    let activeTime = 0; // ms
    let lastActivity = Date.now();
    let isActive = true;
    const UPDATE_INTERVAL = 60000; // 1 minute
    const INACTIVITY_TIMEOUT = 300000; // 5 minutes

    // Check availability
    if (!localStorage.getItem('token')) {
        console.log('Time Tracker: No user logged in');
        return;
    }

    // Activity listeners
    ['mousedown', 'keydown', 'scroll', 'touchstart'].forEach(event => {
        document.addEventListener(event, () => {
            lastActivity = Date.now();
            isActive = true;
        });
    });

    // Visibility listener
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            isActive = false;
        } else {
            lastActivity = Date.now();
            isActive = true;
        }
    });

    // Heartbeat function
    setInterval(async () => {
        const now = Date.now();

        // Check if user has been inactive or tab is hidden
        if (document.hidden || (now - lastActivity > INACTIVITY_TIMEOUT)) {
            isActive = false;
        } else {
            isActive = true;
        }

        if (isActive) {
            try {
                const token = localStorage.getItem('token');
                if (!token) return;

                const response = await fetch('/api/profile/update-time/', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Token ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ increment: 1 })
                });

                if (response.ok) {
                    const data = await response.json();
                    console.log(`Time Tracker: Logged 1 minute. Total: ${data.total_time_spent}`);

                    // Dispatch event for UI updates
                    window.dispatchEvent(new CustomEvent('timeUpdated', {
                        detail: { totalTime: data.total_time_spent }
                    }));
                }
            } catch (error) {
                console.error('Time Tracker Error:', error);
            }
        }
    }, UPDATE_INTERVAL);
})();
