// SheSecure - Client-side JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Initialize navbar
    initNavbar();
    
    // Initialize theme system
    initTheme();
    
    // Initialize floating chatbot button
    initChatbot();
    
    // Sync contacts for offline mode compatibility
    syncContactsForOfflineMode();
    
    // Initialize emergency actions
    initEmergencyActionButtons();
    
    // Initialize SOS buttons
    initSOSButtons();
});

const DEFAULT_EMERGENCY_NUMBER = '112';
let emergencyActionState = {
    contacts: [],
    location: null,
    emergencyNumber: DEFAULT_EMERGENCY_NUMBER
};
let liveShareState = {
    token: localStorage.getItem('live_share_token') || null,
    shareUrl: localStorage.getItem('live_share_url') || null,
    updateTimer: null
};
let telegramLiveState = {
    sessionId: localStorage.getItem('telegram_live_session_id') || null,
    recipientSignature: localStorage.getItem('telegram_live_signature') || null,
    updateTimer: null
};

// ==================== NAVBAR ====================
function initNavbar() {
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('nav-links');
    
    if (hamburger) {
        hamburger.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }
    
    // Theme selector dropdown
    initThemeSelector();
}

function initThemeSelector() {
    const themeBtn = document.getElementById('theme-btn');
    const themeMenu = document.getElementById('theme-menu');
    const themeOptions = document.querySelectorAll('.theme-option');
    
    if (!themeBtn || !themeMenu) return;
    
    // Toggle menu visibility
    themeBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        themeMenu.classList.toggle('active');
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.theme-selector')) {
            themeMenu.classList.remove('active');
        }
    });
    
    // Handle theme option clicks
    themeOptions.forEach(option => {
        option.addEventListener('click', function() {
            const theme = this.getAttribute('data-theme');
            switchTheme(theme);
            updateThemeMenuUI(theme);
            themeMenu.classList.remove('active');
        });
    });
    
    // Mark active theme on load
    const currentTheme = localStorage.getItem('theme') || 'light';
    updateThemeMenuUI(currentTheme);
}

function updateThemeMenuUI(theme) {
    const themeOptions = document.querySelectorAll('.theme-option');
    themeOptions.forEach(option => {
        if (option.getAttribute('data-theme') === theme) {
            option.classList.add('active');
        } else {
            option.classList.remove('active');
        }
    });
}

// ==================== THEME SYSTEM ====================
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);
    
    // Update menu UI after page load
    setTimeout(() => {
        updateThemeMenuUI(savedTheme);
    }, 100);
}

function applyTheme(theme) {
    // Remove all theme classes
    document.body.classList.remove('theme-light', 'theme-dark', 'theme-high-contrast');
    
    // Add the selected theme class
    document.body.classList.add(`theme-${theme}`);
    
    // Save to localStorage
    localStorage.setItem('theme', theme);
    
    console.log('Theme applied:', theme);
}

function switchTheme(theme) {
    const validThemes = ['light', 'dark', 'high-contrast'];
    if (validThemes.includes(theme)) {
        applyTheme(theme);
    }
}

// ==================== CHATBOT ====================
function initChatbot() {
    const chatBtn = document.getElementById('floating-chatbot-btn');
    if (chatBtn) {
        chatBtn.addEventListener('click', function() {
            window.location.href = '/chatbot';
        });
    }
}

// ==================== STORAGE UTILITIES ====================
function saveToLocalStorage(key, data) {
    localStorage.setItem(key, JSON.stringify(data));
}

function getFromLocalStorage(key) {
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : null;
}

// Sync contacts format for offline safety compatibility
function syncContactsForOfflineMode() {
    const contacts = loadContactsList();
    localStorage.setItem('trusted_contacts', JSON.stringify(contacts));
    localStorage.setItem('contacts_list', JSON.stringify(contacts));
}

// ==================== CONTACTS MANAGEMENT ====================
function loadContactsList() {
    const contacts = getFromLocalStorage('contacts') || [];
    return contacts;
}

function addContact(contact) {
    const contacts = loadContactsList();
    contacts.push(contact);
    saveToLocalStorage('contacts', contacts);
    syncContactsForOfflineMode();
}

function removeContact(index) {
    const contacts = loadContactsList();
    contacts.splice(index, 1);
    saveToLocalStorage('contacts', contacts);
    syncContactsForOfflineMode();
}

function updateContactCount() {
    const contacts = loadContactsList();
    const countElement = document.getElementById('contacts-count');
    if (countElement) {
        countElement.textContent = contacts.length;
    }
}

// ==================== LOCATION UTILITIES ====================
function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject('Geolocation not supported');
            return;
        }
        
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const { latitude, longitude } = position.coords;
                resolve({ lat: latitude, lon: longitude });
            },
            function(error) {
                reject(error.message);
            }
        );
    });
}

async function getEmergencyLocationOrNull() {
    try {
        return await getCurrentLocation();
    } catch (error) {
        console.warn('Unable to load current location for emergency action:', error);
        return null;
    }
}

function normalizeEmergencyNumber(phone) {
    return String(phone || '').replace(/[^\d+]/g, '');
}

function normalizeWhatsAppNumber(phone) {
    return String(phone || '').replace(/\D/g, '');
}

function getTelegramChatId(contact) {
    return String(contact?.telegram_chat_id || contact?.telegramChatId || '').trim();
}

function getTelegramEligibleContacts(contacts) {
    return (contacts || []).filter(contact => getTelegramChatId(contact));
}

function buildTelegramRecipientSignature(contacts) {
    return getTelegramEligibleContacts(contacts)
        .map(contact => getTelegramChatId(contact))
        .sort()
        .join('|');
}

function resolveEmergencyRecipients(target, explicitNumber) {
    if (explicitNumber) {
        return [{ name: 'Emergency Contact', phone: explicitNumber }];
    }

    if (target === 'trusted-contacts') {
        return loadContactsList();
    }

    return [];
}

function buildEmergencyMessage(location) {
    const shareUrl = arguments.length > 1 ? arguments[1] : null;
    const lines = [
        'This is an emergency alert from SheSecure.',
        'I may need immediate help.'
    ];

    if (shareUrl) {
        lines.push(`Live tracking: ${shareUrl}`);
    } else {
        lines.push('Live tracking link is being prepared.');
    }

    lines.push(`Time: ${new Date().toLocaleString()}`);
    lines.push('Please contact me or emergency services immediately.');

    return lines.join('\n');
}

function buildLiveLocationMessage(location) {
    const shareUrl = arguments.length > 1 ? arguments[1] : null;
    const lines = [
        'Live location update from SheSecure.',
        'Sharing my current location with you for safety.'
    ];

    if (shareUrl) {
        lines.push(`Track me live here: ${shareUrl}`);
    } else {
        lines.push('Live tracking link is being prepared.');
    }

    lines.push(`Time: ${new Date().toLocaleString()}`);
    lines.push('Please keep an eye on this update.');

    return lines.join('\n');
}

async function copyTextToClipboard(text) {
    if (!navigator.clipboard || !text) {
        return false;
    }

    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (error) {
        console.warn('Clipboard copy failed:', error);
        return false;
    }
}

function openEmergencyDialer(number = DEFAULT_EMERGENCY_NUMBER) {
    const normalizedNumber = normalizeEmergencyNumber(number);
    if (!normalizedNumber) {
        alert('No emergency phone number is available.');
        return false;
    }

    window.location.href = `tel:${normalizedNumber}`;
    return true;
}

async function openEmergencySmsComposer(recipients, message) {
    const numbers = (recipients || [])
        .map(contact => normalizeEmergencyNumber(contact.phone || contact))
        .filter(Boolean);

    if (numbers.length === 0) {
        alert('Add at least one trusted contact before sending an emergency message.');
        return false;
    }

    const smsUrl = `sms:${numbers.join(',')}?body=${encodeURIComponent(message || '')}`;

    try {
        window.location.href = smsUrl;
    } catch (error) {
        console.warn('SMS composer could not be opened:', error);
        const copied = await copyTextToClipboard(message || '');
        alert(copied
            ? 'SMS composer could not be opened here, but the emergency message was copied to your clipboard.'
            : 'SMS composer could not be opened on this device.');
        return false;
    }

    return true;
}

function openWhatsAppComposer(recipients, message) {
    const numbers = (recipients || [])
        .map(contact => normalizeWhatsAppNumber(contact.phone || contact))
        .filter(Boolean);

    if (numbers.length === 0) {
        alert('Add at least one trusted contact before sending a WhatsApp alert.');
        return false;
    }

    numbers.forEach((number, index) => {
        const url = `https://wa.me/${number}?text=${encodeURIComponent(message || '')}`;
        if (index === 0) {
            window.open(url, '_blank', 'noopener');
        } else {
            setTimeout(() => {
                window.open(url, '_blank', 'noopener');
            }, index * 300);
        }
    });

    return true;
}

async function sendTrustedContactAlert({ contacts, message, location = null, mode = 'emergency' }) {
    const safeContacts = (contacts || []).filter(contact => normalizeEmergencyNumber(contact.phone || contact));
    const telegramContacts = getTelegramEligibleContacts(safeContacts);

    if (!safeContacts.length) {
        return {
            status: 'error',
            message: 'Add at least one trusted contact before sending an alert.'
        };
    }

    if (telegramContacts.length > 0) {
        const telegramResponse = await fetch('/api/telegram/message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contacts: telegramContacts,
                message,
                location,
                mode,
                timestamp: new Date().toISOString()
            })
        });

        const telegramData = await telegramResponse.json();
        if (telegramResponse.ok && telegramData.status !== 'error') {
            telegramData.message = telegramData.message || `Telegram alerts sent to ${telegramContacts.length} trusted contact(s).`;
            return telegramData;
        }
    }

    const response = await fetch('/emergency/sms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            contacts: safeContacts,
            location,
            message,
            mode,
            timestamp: new Date().toISOString()
        })
    });

    const data = await response.json();
    if (!response.ok || data.status === 'error') {
        throw new Error(data.message || 'Unable to send the trusted contact alert.');
    }

    openWhatsAppComposer(safeContacts, message);
    data.message = `Opened WhatsApp for ${safeContacts.length} trusted contact(s). Add Telegram chat IDs for direct no-click delivery.`;

    return data;
}

async function startTelegramLiveSession(contacts, location, message) {
    const telegramContacts = getTelegramEligibleContacts(contacts);
    const response = await fetch('/api/telegram/live/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            contacts: telegramContacts,
            location,
            message,
            live_period: 3600,
            timestamp: new Date().toISOString()
        })
    });

    const data = await response.json();
    if (!response.ok || data.status === 'error') {
        throw new Error(data.message || 'Unable to start Telegram live location.');
    }

    telegramLiveState.sessionId = data.session_id;
    telegramLiveState.recipientSignature = buildTelegramRecipientSignature(telegramContacts);
    localStorage.setItem('telegram_live_session_id', telegramLiveState.sessionId);
    localStorage.setItem('telegram_live_signature', telegramLiveState.recipientSignature);
    return data;
}

async function updateTelegramLiveSession(location) {
    if (!telegramLiveState.sessionId) {
        throw new Error('Telegram live session is not active.');
    }

    const response = await fetch(`/api/telegram/live/${telegramLiveState.sessionId}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            location,
            timestamp: new Date().toISOString()
        })
    });

    const data = await response.json();
    if (!response.ok || data.status === 'error') {
        throw new Error(data.message || 'Unable to update Telegram live location.');
    }

    return data;
}

function ensureTelegramLiveUpdater(contacts) {
    if (telegramLiveState.updateTimer) {
        return;
    }

    telegramLiveState.updateTimer = window.setInterval(async () => {
        try {
            const location = await getCurrentLocation();
            await updateTelegramLiveSession(location);
            await pushLiveShareUpdate(location);
        } catch (error) {
            console.warn('Telegram live update failed:', error);
        }
    }, 15000);
}

async function ensureTelegramLiveShareSession(contacts, location, introMessage) {
    const telegramContacts = getTelegramEligibleContacts(contacts);
    if (!telegramContacts.length) {
        return { mode: 'fallback' };
    }

    const signature = buildTelegramRecipientSignature(telegramContacts);
    const resolvedLocation = location || await getCurrentLocation();

    if (!telegramLiveState.sessionId || telegramLiveState.recipientSignature !== signature) {
        const data = await startTelegramLiveSession(telegramContacts, resolvedLocation, introMessage);
        ensureTelegramLiveUpdater(telegramContacts);
        return {
            mode: 'telegram',
            sessionId: data.session_id,
            location: resolvedLocation
        };
    }

    await updateTelegramLiveSession(resolvedLocation);
    ensureTelegramLiveUpdater(telegramContacts);
    return {
        mode: 'telegram',
        sessionId: telegramLiveState.sessionId,
        location: resolvedLocation
    };
}

async function createLiveShareSession(location) {
    const response = await fetch('/api/live-share/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            location,
            timestamp: new Date().toISOString()
        })
    });

    const data = await response.json();
    if (!response.ok || data.status !== 'success') {
        throw new Error(data.message || 'Unable to start live sharing.');
    }

    liveShareState.token = data.token;
    liveShareState.shareUrl = data.share_url;
    localStorage.setItem('live_share_token', data.token);
    localStorage.setItem('live_share_url', data.share_url);
    return data;
}

function resetLiveShareSession() {
    liveShareState.token = null;
    liveShareState.shareUrl = null;
    localStorage.removeItem('live_share_token');
    localStorage.removeItem('live_share_url');
}

async function pushLiveShareUpdate(location) {
    if (!liveShareState.token) {
        return createLiveShareSession(location);
    }

    const response = await fetch(`/api/live-share/${liveShareState.token}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            location,
            timestamp: new Date().toISOString()
        })
    });

    const data = await response.json();
    if (response.status === 404 || data.message === 'Live-share session not found.') {
        resetLiveShareSession();
        return createLiveShareSession(location);
    }

    if (!response.ok || data.status !== 'success') {
        throw new Error(data.message || 'Unable to update live location sharing.');
    }

    if (data.share_url) {
        liveShareState.shareUrl = data.share_url;
        localStorage.setItem('live_share_url', data.share_url);
    }

    return {
        token: liveShareState.token,
        share_url: data.share_url || liveShareState.shareUrl,
        location
    };
}

function ensureLiveShareUpdater() {
    if (liveShareState.updateTimer) {
        return;
    }

    liveShareState.updateTimer = window.setInterval(async () => {
        if (!liveShareState.token) {
            return;
        }

        try {
            const location = await getCurrentLocation();
            await pushLiveShareUpdate(location);
        } catch (error) {
            console.warn('Live share update failed:', error);
        }
    }, 15000);
}

async function ensureLiveShareSession(location = null) {
    const resolvedLocation = location || await getCurrentLocation();
    let liveShare;

    if (!liveShareState.token || !liveShareState.shareUrl) {
        liveShare = await createLiveShareSession(resolvedLocation);
    } else {
        liveShare = await pushLiveShareUpdate(resolvedLocation);
    }

    ensureLiveShareUpdater();

    return {
        location: resolvedLocation,
        shareUrl: liveShare.share_url || liveShareState.shareUrl
    };
}

async function sendLocationAndEmergencyAlerts(contacts, location = null) {
    const liveShare = await ensureLiveShareSession(location);
    const resolvedLocation = liveShare.location;
    const shareUrl = liveShare.shareUrl;
    const telegramLive = await ensureTelegramLiveShareSession(
        contacts,
        resolvedLocation,
        buildLiveLocationMessage(resolvedLocation, shareUrl)
    );

    let locationResult;
    if (telegramLive.mode === 'telegram') {
        locationResult = {
            status: 'success',
            delivery: 'telegram',
            message: 'Telegram live location started for trusted contacts.'
        };
    } else {
        locationResult = await sendTrustedContactAlert({
            contacts,
            message: buildLiveLocationMessage(resolvedLocation, shareUrl),
            location: resolvedLocation,
            mode: 'location'
        });
    }

    const emergencyResult = await sendTrustedContactAlert({
        contacts,
        message: buildEmergencyMessage(resolvedLocation, shareUrl),
        location: resolvedLocation,
        mode: 'emergency'
    });

    return {
        locationResult,
        emergencyResult,
        location: resolvedLocation
    };
}

function ensureEmergencyActionModal() {
    if (document.getElementById('emergency-action-modal')) {
        return;
    }

    const modal = document.createElement('div');
    modal.id = 'emergency-action-modal';
    modal.className = 'emergency-action-modal';
    modal.innerHTML = `
        <div class="emergency-action-backdrop" data-emergency-close="true"></div>
        <div class="emergency-action-panel" role="dialog" aria-modal="true" aria-labelledby="emergency-action-title">
            <button type="button" class="emergency-action-close" data-emergency-close="true" aria-label="Close emergency actions">Close</button>
            <p class="emergency-action-kicker">Emergency actions ready</p>
            <h2 id="emergency-action-title">Choose how to respond right now</h2>
            <p class="emergency-action-summary" id="emergency-action-summary">
                Call emergency services or send a prepared message to your trusted contacts.
            </p>
            <div class="emergency-action-buttons">
                <button type="button" class="btn btn-primary" id="emergency-call-action">Call 112</button>
                <button type="button" class="btn btn-secondary" id="emergency-message-action">Message Contacts</button>
                <button type="button" class="btn btn-secondary" id="emergency-copy-action">Copy Alert</button>
            </div>
        </div>
    `;

    const styles = document.createElement('style');
    styles.textContent = `
        .emergency-action-modal {
            position: fixed;
            inset: 0;
            z-index: 1200;
            display: none;
        }
        .emergency-action-modal.active {
            display: block;
        }
        .emergency-action-backdrop {
            position: absolute;
            inset: 0;
            background: rgba(15, 23, 42, 0.65);
        }
        .emergency-action-panel {
            position: relative;
            width: min(92vw, 520px);
            margin: 12vh auto 0;
            background: #ffffff;
            color: #111827;
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.28);
        }
        .emergency-action-close {
            border: 0;
            background: transparent;
            color: #475569;
            cursor: pointer;
            float: right;
            font-size: 14px;
        }
        .emergency-action-kicker {
            margin: 0 0 8px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 12px;
            color: #b91c1c;
            font-weight: 700;
        }
        .emergency-action-panel h2 {
            margin: 0 0 10px;
            font-size: 28px;
            line-height: 1.2;
        }
        .emergency-action-summary {
            margin: 0 0 20px;
            color: #475569;
        }
        .emergency-action-buttons {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
        }
        @media (max-width: 640px) {
            .emergency-action-panel {
                margin-top: 8vh;
                padding: 20px;
            }
            .emergency-action-buttons {
                grid-template-columns: 1fr;
            }
        }
    `;

    document.head.appendChild(styles);
    document.body.appendChild(modal);

    modal.addEventListener('click', async function(event) {
        const closeTarget = event.target.closest('[data-emergency-close="true"]');
        if (closeTarget) {
            hideEmergencyActionModal();
            return;
        }

        if (event.target.id === 'emergency-call-action') {
            openEmergencyDialer(emergencyActionState.emergencyNumber);
            return;
        }

        if (event.target.id === 'emergency-message-action') {
            const message = buildEmergencyMessage(emergencyActionState.location);
            await sendTrustedContactAlert({
                contacts: emergencyActionState.contacts,
                message,
                location: emergencyActionState.location,
                mode: 'emergency'
            });
            return;
        }

        if (event.target.id === 'emergency-copy-action') {
            const copied = await copyTextToClipboard(buildEmergencyMessage(emergencyActionState.location));
            alert(copied ? 'Emergency message copied to clipboard.' : 'Clipboard access is not available on this device.');
        }
    });
}

function showEmergencyActionModal({ contacts = [], location = null, emergencyNumber = DEFAULT_EMERGENCY_NUMBER } = {}) {
    ensureEmergencyActionModal();

    emergencyActionState = {
        contacts,
        location,
        emergencyNumber
    };

    const modal = document.getElementById('emergency-action-modal');
    const summary = document.getElementById('emergency-action-summary');
    const callButton = document.getElementById('emergency-call-action');
    const messageButton = document.getElementById('emergency-message-action');

    if (!modal || !summary || !callButton || !messageButton) {
        return;
    }

    const recipientCount = contacts.length;
    const locationText = location && Number.isFinite(location.lat) && Number.isFinite(location.lon)
        ? `Location ready: ${location.lat.toFixed(4)}, ${location.lon.toFixed(4)}.`
        : 'Location will be omitted if it is unavailable.';

    summary.textContent = `${locationText} Call ${emergencyNumber} now or open a prepared SMS for ${recipientCount} trusted contact${recipientCount === 1 ? '' : 's'}.`;
    callButton.textContent = `Call ${emergencyNumber}`;
    messageButton.disabled = recipientCount === 0;
    messageButton.textContent = recipientCount === 0 ? 'No Contacts Saved' : 'Message Contacts';
    modal.classList.add('active');
}

function hideEmergencyActionModal() {
    const modal = document.getElementById('emergency-action-modal');
    if (modal) {
        modal.classList.remove('active');
    }
}

function initEmergencyActionButtons() {
    ensureEmergencyActionModal();

    const buttons = document.querySelectorAll('[data-emergency-action]');
    buttons.forEach(button => {
        if (button.dataset.emergencyBound === 'true') {
            return;
        }

        button.dataset.emergencyBound = 'true';
        button.addEventListener('click', async function(event) {
            event.preventDefault();

            const action = this.dataset.emergencyAction;
            const emergencyNumber = this.dataset.emergencyNumber || DEFAULT_EMERGENCY_NUMBER;
            const location = await getEmergencyLocationOrNull();
            const contacts = resolveEmergencyRecipients(this.dataset.emergencyTarget, this.dataset.emergencyContact);

            if (action === 'call') {
                openEmergencyDialer(emergencyNumber);
                return;
            }

            if (action === 'message') {
                await sendTrustedContactAlert({
                    contacts,
                    message: buildEmergencyMessage(location),
                    location,
                    mode: 'emergency'
                });
                return;
            }

            if (action === 'panel') {
                showEmergencyActionModal({
                    contacts: contacts.length > 0 ? contacts : loadContactsList(),
                    location,
                    emergencyNumber
                });
            }
        });
    });
}

// ==================== EMERGENCY ALERT ====================
function initSOSButtons() {
    // Find all SOS buttons and attach event listeners
    const sosButtons = document.querySelectorAll('#sos-btn, .sos-btn, .btn-sos');
    sosButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            triggerSOS();
        });
    });
}

function triggerSOS() {
    // Use offline safety mode if available
    if (typeof offlineSafety !== 'undefined' && offlineSafety) {
        offlineSafety.triggerOfflineSOS();
        return;
    }
    
    // Fallback to basic SOS
    getCurrentLocation()
        .then(async location => {
            const contacts = loadContactsList();
            if (contacts.length === 0) {
                alert('Please add trusted contacts first!');
                return;
            }

            await sendLocationAndEmergencyAlerts(contacts, location);
            alert(`SOS Activated!\n\nLive location and emergency alerts were triggered for ${contacts.length} trusted contacts.\n\nLocation: ${location.lat.toFixed(4)}, ${location.lon.toFixed(4)}`);
            showEmergencyActionModal({
                contacts,
                location,
                emergencyNumber: DEFAULT_EMERGENCY_NUMBER
            });
            
            // Log SOS event
            console.log('SOS triggered at:', location);
        })
        .catch(error => {
            alert('Unable to get location for SOS: ' + error);
        });
}

// ==================== FORM UTILITIES ====================
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^\d{10,}$/;
    return re.test(phone.replace(/\D/g, ''));
}

// ==================== LEGACY SUPPORT ====================
// Legacy functions for backward compatibility

function loadContacts() {
    return loadContactsList();
}

function saveContacts(contacts) {
    saveToLocalStorage('contacts', contacts);
    syncContactsForOfflineMode();
}

function fetchLocation() {
    getCurrentLocation().then(location => {
        const latElem = document.getElementById('lat');
        const lonElem = document.getElementById('lon');
        if (latElem) latElem.textContent = location.lat.toFixed(6);
        if (lonElem) lonElem.textContent = location.lon.toFixed(6);
    });
}

function computeSafetyLevel(lat, lon) {
    // Mock safety calculation based on coordinates
    const riskScore = Math.random() * 100;
    return riskScore > 70 ? 'HIGH RISK ⚠️' : 'LOW RISK ✅';
}

function triggerEmergencyAlert() {
    triggerSOS();
}

window.buildEmergencyMessage = buildEmergencyMessage;
window.buildLiveLocationMessage = buildLiveLocationMessage;
window.ensureLiveShareSession = ensureLiveShareSession;
window.ensureTelegramLiveShareSession = ensureTelegramLiveShareSession;
window.loadContactsList = loadContactsList;
window.openEmergencyDialer = openEmergencyDialer;
window.openEmergencySmsComposer = openEmergencySmsComposer;
window.openWhatsAppComposer = openWhatsAppComposer;
window.getTelegramEligibleContacts = getTelegramEligibleContacts;
window.sendLocationAndEmergencyAlerts = sendLocationAndEmergencyAlerts;
window.sendTrustedContactAlert = sendTrustedContactAlert;
window.showEmergencyActionModal = showEmergencyActionModal;

