/**
 * Persistent Back Button Component
 * A fixed back navigation button at top-left for feature screens
 * Follows browser back button standards
 */

class BackButton {
    constructor() {
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.mount());
        } else {
            this.mount();
        }
    }

    mount() {
        // Don't show back button on home/landing pages
        const excludePages = ['/', '/landing', '/login', '/signup'];
        if (excludePages.includes(window.location.pathname)) {
            return;
        }

        // Create back button container
        const backContainer = document.createElement('div');
        backContainer.id = 'back-button-container';
        backContainer.innerHTML = `
            <button 
                id="persistent-back-btn" 
                class="persistent-back-btn"
                aria-label="Go back to previous page"
                title="Go back"
            >
                <span class="back-arrow">←</span>
            </button>
        `;

        // Insert at the beginning of body
        document.body.insertBefore(backContainer, document.body.firstChild);

        // Attach event listener
        this.attachEventListener();
    }

    attachEventListener() {
        const backBtn = document.getElementById('persistent-back-btn');
        
        if (backBtn) {
            backBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.goBack();
            });

            // Keyboard support: Alt+Left arrow (common back shortcut)
            document.addEventListener('keydown', (e) => {
                if ((e.altKey && e.key === 'ArrowLeft') || (e.metaKey && e.key === 'ArrowLeft')) {
                    e.preventDefault();
                    this.goBack();
                }
            });
        }
    }

    goBack() {
        // Try to go back in history
        if (window.history.length > 1) {
            window.history.back();
        } else {
            // Fallback to dashboard if no history
            window.location.href = '/dashboard';
        }
    }
}

// Initialize when script loads
const backButton = new BackButton();
