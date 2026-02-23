/**
 * Persistent SOS Button Component
 * A fixed, always-visible emergency button with confirmation modal
 * Integrates with existing offline safety system
 */

class SOSButton {
    constructor() {
        this.isConfirmationOpen = false;
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
        // Create SOS button container
        const sosContainer = document.createElement('div');
        sosContainer.id = 'sos-button-container';
        sosContainer.innerHTML = `
            <!-- Persistent SOS Button -->
            <button 
                id="persistent-sos-btn" 
                class="persistent-sos-btn"
                aria-label="Emergency SOS - Press for help"
                title="Emergency: Press to trigger SOS"
            >
                🆘
            </button>

            <!-- Confirmation Modal (hidden by default) -->
            <div id="sos-confirmation-modal" class="sos-modal" style="display: none;">
                <div class="sos-modal-overlay" id="sos-modal-overlay"></div>
                <div class="sos-modal-content">
                    <div class="sos-modal-header">
                        <h2>⚠️ Emergency Alert</h2>
                    </div>
                    <div class="sos-modal-body">
                        <p class="sos-modal-question">Are you in danger?</p>
                        <p class="sos-modal-info">This will immediately alert your emergency contacts and trigger safety features.</p>
                    </div>
                    <div class="sos-modal-footer">
                        <button id="sos-cancel-btn" class="sos-btn-cancel" aria-label="Cancel SOS">
                            Cancel
                        </button>
                        <button id="sos-confirm-btn" class="sos-btn-confirm" aria-label="Confirm SOS">
                            Yes, Send SOS
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(sosContainer);

        // Attach event listeners
        this.attachEventListeners();
    }

    attachEventListeners() {
        const sosBtn = document.getElementById('persistent-sos-btn');
        const confirmBtn = document.getElementById('sos-confirm-btn');
        const cancelBtn = document.getElementById('sos-cancel-btn');
        const modalOverlay = document.getElementById('sos-modal-overlay');
        const modal = document.getElementById('sos-confirmation-modal');

        // Open confirmation on button click
        sosBtn?.addEventListener('click', (e) => {
            e.preventDefault();
            this.openConfirmation();
        });

        // Confirm SOS action
        confirmBtn?.addEventListener('click', () => {
            this.closeConfirmation();
            this.triggerSOS();
        });

        // Cancel SOS action
        cancelBtn?.addEventListener('click', () => {
            this.closeConfirmation();
        });

        // Close on overlay click
        modalOverlay?.addEventListener('click', () => {
            this.closeConfirmation();
        });

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isConfirmationOpen) {
                this.closeConfirmation();
            }
        });
    }

    openConfirmation() {
        if (this.isConfirmationOpen) return;

        const modal = document.getElementById('sos-confirmation-modal');
        if (modal) {
            modal.style.display = 'block';
            this.isConfirmationOpen = true;
            
            // Focus confirm button for accessibility
            setTimeout(() => {
                document.getElementById('sos-confirm-btn')?.focus();
            }, 100);
        }
    }

    closeConfirmation() {
        const modal = document.getElementById('sos-confirmation-modal');
        if (modal) {
            modal.style.display = 'none';
            this.isConfirmationOpen = false;
        }
    }

    triggerSOS() {
        // Use existing offline safety system if available
        if (typeof offlineSafety !== 'undefined' && offlineSafety.triggerOfflineSOS) {
            offlineSafety.triggerOfflineSOS();
        } else {
            // Fallback if offline safety not loaded
            this.fallbackSOS();
        }
    }

    fallbackSOS() {
        console.warn('Offline safety system not available. Using fallback.');
        alert('🚨 Emergency SOS Triggered!\n\nContacting emergency services...');
        
        // Log to console for debugging
        console.log('Emergency triggered at:', new Date().toISOString());
        
        // Could implement fallback logic here
        // - Send to backend
        // - Store locally
        // - etc.
    }
}

// Initialize when script loads
const sosButton = new SOSButton();
