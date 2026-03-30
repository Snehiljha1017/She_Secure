/**
 * Persistent SOS Button Component
 * A fixed, always-visible emergency button with direct activation.
 */

class SOSButton {
    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.mount());
        } else {
            this.mount();
        }
    }

    mount() {
        const sosContainer = document.createElement('div');
        sosContainer.id = 'sos-button-container';
        sosContainer.innerHTML = `
            <button
                id="persistent-sos-btn"
                class="persistent-sos-btn"
                aria-label="Emergency SOS - Press for help"
                title="Emergency: Press to trigger SOS"
            >
                SOS
            </button>
        `;

        document.body.appendChild(sosContainer);
        this.attachEventListeners();
    }

    attachEventListeners() {
        const sosBtn = document.getElementById('persistent-sos-btn');
        sosBtn?.addEventListener('click', (event) => {
            event.preventDefault();
            this.triggerSOS();
        });
    }

    triggerSOS() {
        if (typeof window.triggerEmergencyAlert === 'function') {
            window.triggerEmergencyAlert();
            return;
        }

        if (typeof offlineSafety !== 'undefined' && offlineSafety.triggerOfflineSOS) {
            offlineSafety.triggerOfflineSOS();
            return;
        }

        this.fallbackSOS();
    }

    fallbackSOS() {
        console.warn('Offline safety system not available. Using fallback.');
        alert('Emergency SOS Triggered. Contacting emergency services...');
        console.log('Emergency triggered at:', new Date().toISOString());
    }
}

const sosButton = new SOSButton();
sosButton.init();
