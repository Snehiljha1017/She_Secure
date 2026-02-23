// ==================== OFFLINE SAFETY MODE ====================
// Comprehensive offline safety features for emergency situations

class OfflineSafetyMode {
    constructor() {
        this.isOnline = navigator.onLine;
        this.emergencyQueue = this.loadQueue();
        this.lastKnownLocation = this.loadLastLocation();
        this.audioRecorder = null;
        this.videoRecorder = null;
        this.alarmAudio = null;
        
        this.init();
    }
    
    init() {
        this.setupOnlineDetection();
        this.setupOfflineIndicator();
        this.setupAlarmAudio();
        this.startLocationTracking();
        this.checkAndProcessQueue();
    }
    
    // ==================== ONLINE/OFFLINE DETECTION ====================
    setupOnlineDetection() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.updateOfflineIndicator(false);
            this.processQueuedEmergencies();
            this.showNotification('✅ Back Online', 'Emergency queue is being processed', 'success');
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.updateOfflineIndicator(true);
            this.showNotification('⚠️ Offline Mode', 'Emergency features available without internet', 'warning');
        });
    }
    
    setupOfflineIndicator() {
        // Create offline status indicator - Premium design
        const indicator = document.createElement('div');
        indicator.id = 'offline-indicator';
        indicator.className = 'offline-indicator';
        indicator.innerHTML = `
            <div class="offline-indicator-accent"></div>
            <div class="offline-indicator-main">
                <div class="offline-indicator-header">
                    <div class="offline-indicator-status">
                        <span class="offline-pulsing-dot"></span>
                        <span class="offline-title">Safety Shield Active</span>
                    </div>
                    <span class="offline-icon">🛡️</span>
                </div>
                <p class="offline-indicator-subtitle">All emergency features ready</p>
                <div class="offline-feature-chips">
                    <span class="feature-chip" data-feature="location">
                        <span class="chip-icon">📍</span> Location
                    </span>
                    <span class="feature-chip" data-feature="recording">
                        <span class="chip-icon">📹</span> Recording
                    </span>
                    <span class="feature-chip" data-feature="contacts">
                        <span class="chip-icon">👥</span> Contacts
                    </span>
                    <span class="feature-chip" data-feature="alarm">
                        <span class="chip-icon">🔔</span> Alarm
                    </span>
                </div>
                <div class="offline-indicator-actions">
                    <button id="offline-mode-toggle" class="offline-action-btn" title="Disable Offline Safety Mode">
                        Disable
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(indicator);

        // Attach toggle event listener
        const toggleBtn = document.getElementById('offline-mode-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.disableOfflineMode();
            });
        }
        
        this.updateOfflineIndicator(!this.isOnline);
    }
    
    updateOfflineIndicator(isOffline) {
        const indicator = document.getElementById('offline-indicator');
        if (!indicator) return;
        
        if (isOffline) {
            indicator.classList.add('active');
            indicator.querySelector('.offline-title').textContent = 'Safety Shield Active';
            indicator.querySelector('.offline-icon').textContent = '🛡️';
        } else {
            indicator.classList.remove('active');
            indicator.querySelector('.offline-title').textContent = 'Online Protection Ready';
            indicator.querySelector('.offline-icon').textContent = '✅';
        }
    }
    
    disableOfflineMode() {
        // Hide the offline indicator bar
        const indicator = document.getElementById('offline-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
        
        // Clear emergency data and stop tracking
        this.stopAllMonitoring();
        
        // Show notification
        this.showNotification(
            '🔓 Offline Safety Disabled',
            'All emergency features have been disabled. Enable it again from Dashboard.',
            'info'
        );
    }
    
    stopAllMonitoring() {
        // Stop alarm if playing
        if (this.alarmAudio) {
            this.stopAlarm();
        }
        
        // Stop recording if active
        if (this.videoRecorder || this.audioRecorder) {
            this.stopRecordingEvidence();
        }
        
        // Clear location tracking interval
        if (this.locationInterval) {
            clearInterval(this.locationInterval);
        }
    }
    
    reEnableOfflineMode() {
        const indicator = document.getElementById('offline-indicator');
        if (indicator) {
            indicator.style.display = 'flex';
            this.updateOfflineIndicator(!this.isOnline);
        }
        
        this.showNotification(
            '🛡️ Offline Safety Re-enabled',
            'Emergency features are now active again.',
            'success'
        );
    }
    
    // ==================== LOCATION TRACKING ====================
    startLocationTracking() {
        // Update location every 30 seconds
        this.updateLocation();
        this.locationInterval = setInterval(() => this.updateLocation(), 30000);
    }
    
    updateLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.lastKnownLocation = {
                        lat: position.coords.latitude,
                        lon: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: new Date().toISOString()
                    };
                    this.saveLastLocation();
                },
                (error) => {
                    console.warn('Location update failed:', error);
                }
            );
        }
    }
    
    // ==================== OFFLINE SOS (ONE-TAP) ====================
    triggerOfflineSOS() {
        const timestamp = new Date().toISOString();
        const contacts = this.loadContacts();
        
        if (contacts.length === 0) {
            alert('⚠️ No emergency contacts found!\n\nPlease add trusted contacts in the Helplines section.');
            return;
        }
        
        // Get current or last known location
        this.getCurrentOrLastLocation().then(location => {
            const emergencyData = {
                timestamp: timestamp,
                location: location,
                contacts: contacts,
                type: 'offline_sos',
                status: 'pending'
            };
            
            // Queue for sending when online
            this.queueEmergency(emergencyData);
            
            // Attempt SMS if possible (requires device SMS capability)
            this.attemptEmergencySMS(contacts, location);
            
            // Trigger alarm
            this.triggerAlarm();
            
            // Start recording evidence
            this.startRecordingEvidence();
            
            // Show confirmation
            this.showOfflineSOSConfirmation(contacts.length, location);
            
            // Try to process immediately if online
            if (this.isOnline) {
                this.processQueuedEmergencies();
            }
        });
    }
    
    getCurrentOrLastLocation() {
        return new Promise((resolve) => {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const location = {
                            lat: position.coords.latitude,
                            lon: position.coords.longitude,
                            accuracy: position.coords.accuracy,
                            timestamp: new Date().toISOString(),
                            type: 'current'
                        };
                        this.lastKnownLocation = location;
                        this.saveLastLocation();
                        resolve(location);
                    },
                    () => {
                        // Use last known location as fallback
                        resolve({
                            ...this.lastKnownLocation,
                            type: 'last_known'
                        });
                    }
                );
            } else {
                resolve({
                    ...this.lastKnownLocation,
                    type: 'last_known'
                });
            }
        });
    }
    
    // ==================== SMS EMERGENCY ====================
    attemptEmergencySMS(contacts, location) {
        // This requires SMS gateway integration or device SMS capability
        // For web apps, queue for server-side processing
        
        const message = `🚨 EMERGENCY ALERT from SheSecure App!\n\n` +
                       `Location: https://maps.google.com/?q=${location.lat},${location.lon}\n` +
                       `Time: ${new Date().toLocaleString()}\n` +
                       `Accuracy: ${location.accuracy}m\n\n` +
                       `This is an automated emergency alert. Please respond immediately.`;
        
        // If online, send via server
        if (this.isOnline) {
            fetch('/emergency/sms', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    contacts: contacts,
                    location: location,
                    message: message,
                    timestamp: new Date().toISOString()
                })
            }).then(response => response.json())
              .then(data => console.log('SMS queued:', data))
              .catch(error => console.error('SMS queue failed:', error));
        }
        
        console.log('Emergency SMS prepared for:', contacts.length, 'contacts');
    }
    
    // ==================== ALARM SYSTEM ====================
    setupAlarmAudio() {
        // Create audio element for alarm
        this.alarmAudio = new Audio();
        // Using a loud beep sound (data URI for offline availability)
        this.alarmAudio.src = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBiuBzvLZiTYIGGS57OihUBELTKXh8bllHghAkNXwz38pBSZ7y/HeijgJF2O06+yhTxALSKDf7rdmHgYufsvy2og1CAdcsuXqnE4PC0qh3+22YxwGKXzL89uJNQcIXLLl6ppODwtKoN/ttmlCByl8y/PajDUHCFyx5OmZTQ0KSZ/e7bJiGwYpe8zy2Yk1BwhbsuXqmU0NCkif3u2yYhsGKXvM8tmJNQcIW7Lk6ZlNDQpIn97tsmIbBil7zPLZiTUHCFuy5OmZTQ0KSJ/e7bJiGwYpe8zy2Yk1BwhbsuTpmU0NCkif3u2yYhsGKXvM8tmJNQcIW7Lk6ZlNDQpHn97tsmIbBil7y/LZiTYHCFqy5emZTQ0KSJ/e7rJiGwYpe8zy2Yk1BwhbsuTpmU0NCkif3u2yYhsGKXvM8tmJNQcIW7Lk6ZlNDQpIn97tsmIbBil7zPLZiTUHCFuy5OmZTQ0KSJ/e7bJiGwYpe8zy2Yk1BwhbsuTpmU0NCkif3u2yYhsGKXvM8tmJNQcIW7Lk6ZlNDQpIn97tsmIbBil7y/LZiTYHCFuy5OmZTQ0KR5/e7bJiGwYpe8zy2Yk1BwhbsuTpmU0NCkif3u2yYhsGKXvM8tmJNQcIW7Lk6ZlNDQpIn97tsmIbBil7zPLZiTUHCFuy5OmZTQ0KSJ/e7bJiGwYpe8zy2Yk1BwhbsuTpmU0NCkif3u2yYhsGKXvM8tmJNQcIW7Lk6ZlNDQpIn97ts2IbBil7y/LZiTYHCFuy5OmZTQ0KSJ/e7bJiGwYpe8zy2Yk1BwhbsuTpmU0NCkif3u2yYhsGKXvM8tmJNQcIW7Lk6ZlNDQpIn97tsmIbBil7zPLZiTUHCFuy5OmZTQ0KSJ/e7bJiGwYpe8zy2Yk1BwhbsuTpmU0NCkif3u2yYhsGKXvM8tmJNQcIW7Lk6ZlNDQpIn97tsmIbBil7zPLZiTUICFux5OqZTQ0KSJ/e7bJiGwYoe8zy2Yk1BwhbsuTpmU0NCkif3u2yYhsGKXvM8tmJNQcIW7Lk6ZlNDQpIn97tsmIbBil7zPLZiTUHCFuy5OmZTQ0KSJ/e7bJiGwYpe8zy2Yk1BwhbsuTpmU0NCkif3u2yYhsGKXvM8tmJNQcIW7Lk6ZlNDQpIn97tsmIbBil7zPLZiTUHCFuy5OmZTQ0KSJ/e7bJiGwYpe8zy2Yk1BwhbsuTpmU0NCkif3u2yYhsGKXvM8tmJNQcIW7Lk6ZlNDQpIn97tsmIbBil7zPLZiTUHCFuy5OmZTQ0KSJ/e7bJiGwYpe8vy2Yk2BwhbsuTpmU0NCkif3u2yYhsGKXvM8tmJNQcIW7Lk6ZlNDQpIn97tsmIbBil7zPLZiTUHCFuy5OmZTQ0KSJ/e7bJiGwYpe8zy2Yk1BwhbsuTpmU0NCkif3u2yYhsGKXvM8tmJNQcIW7Lk6ZlNDQpIn97tsmIbBil7zPLZiTUHCFuy5OmZTQ0KSJ/e7bJiGwYpe8zy2Yk1BwhbsuTpmU0NCkif3u2yYhsGKXvM8tmJNQcIW7Lk6ZlNDQpIn97tsmIbBil7zPLZiTUHCFuy5OmZTQ0KSJ/e7bJiGwYpe8zy2Yk1BwhbsuTpmU0NCkif3u2yYhsGKXvM8tmJNQcIW7Lk6ZlNDQpIn97tsmIbBil7zPLZiTUHCFuy5OmZTQ0KSJ/e7bJiGwYpe8zy2Yk1BwhbsuTpmU0NCkif3u2yYhsGKXvM8tmJNQcIW7Lk6ZlNDQpIn97tsmIbBil7zPLZiTUHCFuy5OmaTQ0KSJ/e7bJiGwYpe8zy2Yk1BwhbsuXqmlANCkif3O6zYhsGKXvM8tmJNQcIW7Lk6ZpNDQpIn97tsmIbBil7zPLZiTUHCFuy5OmaTQ4JR5/e7rJiGwYpe8zy2Yk1BwhbsuTqmU0NCkef3u2yYhsGKXvM8tmJNQcIW7Lk6plNDQpIn97tsmIbBil7zPLZiTUHCFux5eqaTQ0KSJ/e7bJiGwYpe8zy2Yk1BwhbsuTpmk0NCkif3u2yYhsGKXvM8tmJNQcIW7Lk6ppNDgpHn97usmIbBil7zPLZiTUHCFuy5OqZTQ0KSJ/e7bJiGwYpe8zy2Yk1BwhbsuTpmU0NCkif3u2yYhsGKXvM';
        this.alarmAudio.loop = true;
    }
    
    triggerAlarm() {
        if (this.alarmAudio) {
            this.alarmAudio.play().catch(error => {
                console.warn('Alarm audio failed:', error);
                // Fallback: vibration
                this.triggerVibration();
            });
            
            // Auto-stop after 30 seconds
            setTimeout(() => this.stopAlarm(), 30000);
        }
        
        // Also trigger vibration
        this.triggerVibration();
    }
    
    stopAlarm() {
        if (this.alarmAudio) {
            this.alarmAudio.pause();
            this.alarmAudio.currentTime = 0;
        }
    }
    
    triggerVibration() {
        if ('vibrate' in navigator) {
            // Vibrate in SOS pattern: long, short, long
            navigator.vibrate([1000, 500, 1000, 500, 1000]);
        }
    }
    
    // ==================== EVIDENCE RECORDING ====================
    async startRecordingEvidence() {
        try {
            // Request audio recording
            const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.startAudioRecording(audioStream);
            
            // Request video recording (if camera available)
            try {
                const videoStream = await navigator.mediaDevices.getUserMedia({ 
                    video: { facingMode: 'environment' }, 
                    audio: false 
                });
                this.startVideoRecording(videoStream);
            } catch (videoError) {
                console.warn('Video recording not available:', videoError);
            }
        } catch (error) {
            console.warn('Media recording failed:', error);
            this.showNotification('Recording', 'Could not start evidence recording', 'warning');
        }
    }
    
    startAudioRecording(stream) {
        try {
            this.audioRecorder = new MediaRecorder(stream);
            const audioChunks = [];
            
            this.audioRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };
            
            this.audioRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                this.saveEvidence('audio', audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };
            
            this.audioRecorder.start();
            
            // Stop after 2 minutes
            setTimeout(() => {
                if (this.audioRecorder && this.audioRecorder.state === 'recording') {
                    this.audioRecorder.stop();
                }
            }, 120000);
        } catch (error) {
            console.error('Audio recording failed:', error);
        }
    }
    
    startVideoRecording(stream) {
        try {
            this.videoRecorder = new MediaRecorder(stream);
            const videoChunks = [];
            
            this.videoRecorder.ondataavailable = (event) => {
                videoChunks.push(event.data);
            };
            
            this.videoRecorder.onstop = () => {
                const videoBlob = new Blob(videoChunks, { type: 'video/webm' });
                this.saveEvidence('video', videoBlob);
                stream.getTracks().forEach(track => track.stop());
            };
            
            this.videoRecorder.start();
            
            // Stop after 1 minute (video files can be large)
            setTimeout(() => {
                if (this.videoRecorder && this.videoRecorder.state === 'recording') {
                    this.videoRecorder.stop();
                }
            }, 60000);
        } catch (error) {
            console.error('Video recording failed:', error);
        }
    }
    
    saveEvidence(type, blob) {
        const reader = new FileReader();
        reader.onloadend = () => {
            const base64data = reader.result;
            const evidence = {
                type: type,
                data: base64data,
                timestamp: new Date().toISOString(),
                size: blob.size
            };
            
            // Save to localStorage
            const evidenceList = this.loadEvidence();
            evidenceList.push(evidence);
            
            // Keep only last 5 evidence items (storage limit)
            if (evidenceList.length > 5) {
                evidenceList.shift();
            }
            
            localStorage.setItem('emergency_evidence', JSON.stringify(evidenceList));
            console.log(`${type} evidence saved (${blob.size} bytes)`);
        };
        reader.readAsDataURL(blob);
    }
    
    loadEvidence() {
        const stored = localStorage.getItem('emergency_evidence');
        return stored ? JSON.parse(stored) : [];
    }
    
    // ==================== QUEUE MANAGEMENT ====================
    queueEmergency(emergencyData) {
        this.emergencyQueue.push(emergencyData);
        this.saveQueue();
        console.log('Emergency queued:', emergencyData);
    }
    
    async processQueuedEmergencies() {
        if (this.emergencyQueue.length === 0) {
            return;
        }
        
        console.log(`Processing ${this.emergencyQueue.length} queued emergencies...`);
        
        try {
            const response = await fetch('/emergency/process-queue', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    queue: this.emergencyQueue
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('Queue processed:', data);
                
                // Clear processed items
                this.emergencyQueue = this.emergencyQueue.filter(item => item.status === 'pending');
                this.saveQueue();
                
                this.showNotification('✅ Emergencies Sent', `${data.processed} alerts delivered`, 'success');
            }
        } catch (error) {
            console.error('Failed to process queue:', error);
        }
    }
    
    checkAndProcessQueue() {
        // Check every 30 seconds if online
        setInterval(() => {
            if (this.isOnline && this.emergencyQueue.length > 0) {
                this.processQueuedEmergencies();
            }
        }, 30000);
    }
    
    // ==================== LOCAL STORAGE ====================
    saveQueue() {
        localStorage.setItem('emergency_queue', JSON.stringify(this.emergencyQueue));
    }
    
    loadQueue() {
        const stored = localStorage.getItem('emergency_queue');
        return stored ? JSON.parse(stored) : [];
    }
    
    saveLastLocation() {
        localStorage.setItem('last_known_location', JSON.stringify(this.lastKnownLocation));
    }
    
    loadLastLocation() {
        const stored = localStorage.getItem('last_known_location');
        return stored ? JSON.parse(stored) : { lat: 0, lon: 0, timestamp: null };
    }
    
    loadContacts() {
        // Load from localStorage or default contacts
        const stored = localStorage.getItem('trusted_contacts');
        if (stored) {
            return JSON.parse(stored);
        }
        
        // Fallback to contacts.json data if available
        try {
            const contactsData = localStorage.getItem('contacts_list');
            return contactsData ? JSON.parse(contactsData) : [];
        } catch {
            return [];
        }
    }
    
    // ==================== UI HELPERS ====================
    showOfflineSOSConfirmation(contactCount, location) {
        const locationType = location.type === 'current' ? 'Current' : 'Last Known';
        const accuracy = location.accuracy ? Math.round(location.accuracy) + 'm' : 'Unknown';
        
        const message = `🚨 OFFLINE SOS ACTIVATED!\n\n` +
                       `✅ Queued for ${contactCount} contacts\n` +
                       `📍 ${locationType} Location (±${accuracy})\n` +
                       `🔊 Alarm triggered\n` +
                       `📹 Evidence recording started\n\n` +
                       `Alerts will be sent when connectivity is restored.\n\n` +
                       `💡 Queue Status: Check dashboard for details`;
        
        alert(message);
        
        // Also show persistent notification
        this.showNotification(
            '🚨 SOS Active', 
            `Emergency queued for ${contactCount} contacts. View status on dashboard.`,
            'emergency',
            0 // Don't auto-dismiss
        );
        
        // Update queue badge
        this.updateQueueBadge();
    }
    
    showNotification(title, message, type = 'info', duration = 5000) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `safety-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <strong>${title}</strong>
                <p>${message}</p>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">×</button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after duration (unless duration is 0)
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, duration);
        }
    }
    
    updateQueueBadge() {
        const badge = document.getElementById('emergency-queue-badge');
        const pendingCount = this.emergencyQueue.filter(item => item.status === 'pending').length;
        
        if (!badge && pendingCount > 0) {
            // Create badge if it doesn't exist
            const newBadge = document.createElement('div');
            newBadge.id = 'emergency-queue-badge';
            newBadge.className = 'emergency-queue-badge has-items';
            newBadge.innerHTML = `
                ⏳ <span class="queue-count">${pendingCount}</span> alerts pending
            `;
            newBadge.onclick = () => {
                if (typeof viewQueueStatus === 'function') {
                    viewQueueStatus();
                }
            };
            document.body.appendChild(newBadge);
        } else if (badge) {
            if (pendingCount > 0) {
                badge.classList.add('has-items');
                badge.querySelector('.queue-count').textContent = pendingCount;
            } else {
                badge.classList.remove('has-items');
            }
        }
    }
}

// ==================== INITIALIZATION ====================
// Initialize offline safety mode when DOM is ready
let offlineSafety;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        offlineSafety = new OfflineSafetyMode();
    });
} else {
    offlineSafety = new OfflineSafetyMode();
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OfflineSafetyMode;
}
