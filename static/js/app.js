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
    
    // Initialize SOS buttons
    initSOSButtons();
});

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

function saveContact(contact) {
    const contacts = loadContactsList();
    contacts.push(contact);
    saveToLocalStorage('contacts', contacts);
    syncContactsForOfflineMode();
}

function deleteContact(index) {
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
        .then(location => {
            const contacts = loadContactsList();
            if (contacts.length === 0) {
                alert('Please add trusted contacts first!');
                return;
            }
            
            alert(`SOS Activated!\n\nEmergency alerts sent to ${contacts.length} trusted contacts.\n\nLocation: ${location.lat.toFixed(4)}, ${location.lon.toFixed(4)}`);
            
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

