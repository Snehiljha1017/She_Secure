/**
 * Counselling Portal - Secure & Empathetic Support System
 * Features: AI Chatbot, Live Chat, Appointments, Crisis Support, Resources
 */

class CounsellingPortal {
    constructor() {
        this.currentService = 'mental-health';
        this.chatHistory = [];
        this.sessionID = this.generateSessionID();
        this.privacySettings = this.loadPrivacySettings();
        this.affirmations = [
            "You are brave, resilient, and worthy of support.",
            "Your feelings are valid, and you deserve care.",
            "You are not alone in this journey.",
            "Healing is possible, one step at a time.",
            "You have the strength to overcome challenges.",
            "Your voice matters, and your story is important.",
            "You are deserving of love and compassion.",
            "Every day is a new opportunity for growth.",
            "You are capable of creating positive change.",
            "Your safety and wellbeing are paramount."
        ];
        this.init();
    }

    init() {
        this.setupTabSwitching();
        this.setupAIChat();
        this.setupPrivacyControls();
        this.displayDailyAffirmation();
        this.loadPreviousSessions();
    }

    generateSessionID() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    // ==================== TAB SWITCHING ====================
    setupTabSwitching() {
        const tabs = document.querySelectorAll('.service-tab');
        const contents = document.querySelectorAll('.service-content');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const service = tab.dataset.service;
                
                // Update active tab
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');

                // Update active content
                contents.forEach(c => c.classList.remove('active'));
                const content = document.getElementById(service + '-content');
                if (content) {
                    content.classList.add('active');
                    this.currentService = service;
                }

                // Log selection
                this.logAction('Service selected: ' + service);
            });
        });

        // Set initial active tab
        if (tabs.length > 0) {
            tabs[0].classList.add('active');
        }
    }

    // ==================== AI CHATBOT ====================
    setupAIChat() {
        const input = document.getElementById('ai-message-input');
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendAIMessage();
                }
            });
        }
    }

    sendAIMessage() {
        const input = document.getElementById('ai-message-input');
        if (!input || !input.value.trim()) return;

        const message = input.value.trim();
        const chatBox = document.getElementById('ai-chat-box');

        // Add user message
        this.addChatMessage(message, 'user');
        input.value = '';

        // Store in history
        this.chatHistory.push({
            type: 'user',
            message: message,
            timestamp: new Date().toISOString()
        });

        // Simulate AI response (in production, this would call an API)
        setTimeout(() => {
            const response = this.generateAIResponse(message);
            this.addChatMessage(response, 'bot');

            this.chatHistory.push({
                type: 'bot',
                message: response,
                timestamp: new Date().toISOString()
            });

            this.saveSession();
        }, 500);
    }

    addChatMessage(message, sender) {
        const chatBox = document.getElementById('ai-chat-box');
        if (!chatBox) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}-message`;
        
        const avatar = sender === 'user' ? '👤' : '🤖';
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <p>${this.escapeHTML(message)}</p>
            </div>
        `;

        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    generateAIResponse(userMessage) {
        // Empathetic AI responses based on keywords
        const lower = userMessage.toLowerCase();
        
        const responses = {
            anxiety: "I understand anxiety can feel overwhelming. Have you tried grounding techniques? The 5-4-3-2-1 method (notice 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste) can help bring you back to the present moment.",
            stress: "Stress is a normal response, but we can manage it together. Consider breaking tasks into smaller steps. What's one small thing you could do today to feel less stressed?",
            sad: "Your feelings are valid. It's okay to feel sad sometimes. Would you like to talk about what's making you feel this way? I'm here to listen without judgment.",
            lonely: "Loneliness is a common feeling, but you don't have to face it alone. Consider reaching out to someone you trust, or join support groups. You deserve connection.",
            worry: "Worry often pulls us into 'what-ifs'. Let's focus on what you can control right now. What's one worry you can let go of today?",
            success: "That's wonderful to hear! Celebrating small wins is important. How are you taking care of yourself as you move forward?",
            help: "I'm here to support you. You can share anything, and we can work through it together. What would be most helpful for you right now?"
        };

        for (const [keyword, response] of Object.entries(responses)) {
            if (lower.includes(keyword)) return response;
        }

        // Default empathetic response
        const defaultResponses = [
            "Thank you for sharing that with me. How is that making you feel right now?",
            "I hear you. That sounds challenging. What support would help you most?",
            "Your feelings are important. Tell me more about what you're experiencing.",
            "I'm listening. What matters most to you in this situation?",
            "That's a lot to carry. Let's talk through it together. What's the hardest part?"
        ];

        return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
    }

    // ==================== SESSION MANAGEMENT ====================
    saveSession() {
        const encryptedData = this.encryptData(JSON.stringify(this.chatHistory));
        const sessionData = {
            sessionID: this.sessionID,
            service: this.currentService,
            data: encryptedData,
            timestamp: new Date().toISOString(),
            privacySettings: this.privacySettings
        };

        const sessions = JSON.parse(localStorage.getItem('counselling_sessions') || '[]');
        sessions.push(sessionData);

        // Keep only last 10 sessions to manage storage
        if (sessions.length > 10) {
            sessions.shift();
        }

        localStorage.setItem('counselling_sessions', JSON.stringify(sessions));
    }

    loadPreviousSessions() {
        try {
            const sessions = JSON.parse(localStorage.getItem('counselling_sessions') || '[]');
            console.log(`Loaded ${sessions.length} previous sessions`);
        } catch (e) {
            console.error('Error loading sessions:', e);
        }
    }

    // ==================== PRIVACY & ENCRYPTION ====================
    encryptData(data) {
        // Simple base64 encoding (in production, use proper encryption like TweetNaCl.js)
        return btoa(JSON.stringify(data));
    }

    decryptData(encrypted) {
        try {
            return JSON.parse(atob(encrypted));
        } catch (e) {
            console.error('Decryption failed:', e);
            return null;
        }
    }

    loadPrivacySettings() {
        return {
            autoClearOnLogout: localStorage.getItem('privacy_autoClear') !== 'false',
            encryptStorage: localStorage.getItem('privacy_encrypt') !== 'false',
            shareWithProfessionals: localStorage.getItem('privacy_share') === 'true'
        };
    }

    setupPrivacyControls() {
        const autoClear = document.getElementById('auto-clear-sessions');
        const encrypt = document.getElementById('encrypt-storage');
        const share = document.getElementById('share-with-professionals');

        if (autoClear) {
            autoClear.checked = this.privacySettings.autoClearOnLogout;
            autoClear.addEventListener('change', (e) => {
                localStorage.setItem('privacy_autoClear', e.target.checked);
            });
        }

        if (encrypt) {
            encrypt.checked = this.privacySettings.encryptStorage;
            encrypt.addEventListener('change', (e) => {
                localStorage.setItem('privacy_encrypt', e.target.checked);
            });
        }

        if (share) {
            share.checked = this.privacySettings.shareWithProfessionals;
            share.addEventListener('change', (e) => {
                localStorage.setItem('privacy_share', e.target.checked);
            });
        }
    }

    // ==================== UTILITIES ====================
    escapeHTML(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    logAction(action) {
        const log = {
            action: action,
            timestamp: new Date().toISOString(),
            sessionID: this.sessionID
        };
        console.log('[CounsellingPortal]', log);
    }

    displayDailyAffirmation() {
        const affirmation = document.getElementById('daily-affirmation');
        if (affirmation) {
            const random = this.affirmations[Math.floor(Math.random() * this.affirmations.length)];
            affirmation.textContent = random;
        }
    }
}

// ==================== GLOBAL FUNCTIONS ====================

// Initialize portal
let counsellingPortal;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        counsellingPortal = new CounsellingPortal();
    });
} else {
    counsellingPortal = new CounsellingPortal();
}

// Live Chat
function startLiveChat() {
    alert('💬 Connecting to a live counsellor...\n\nIn a production app, this would open a secure video/audio call with a licensed counsellor.');
    counsellingPortal.logAction('Live chat initiated');
}

// Legal Chat
function startLegalChat() {
    alert('⚖️ Connecting to a legal advisor...\n\nYour consultation is completely confidential and protected by attorney-client privilege.');
    counsellingPortal.logAction('Legal consultation initiated');
}

// Appointment Booking
function openAppointmentBooking() {
    const date = prompt('Enter preferred date (YYYY-MM-DD):');
    const time = prompt('Enter preferred time (HH:MM):');
    
    if (date && time) {
        alert(`✅ Appointment requested for ${date} at ${time}\n\nYou'll receive a confirmation email with session details and secure link.`);
        counsellingPortal.logAction('Appointment booked: ' + date + ' ' + time);
    }
}

// Crisis Mode
function activateCrisisMode() {
    const confirmed = confirm('🆘 CRISIS SUPPORT MODE\n\nYou will be connected with a crisis counsellor immediately.\n\nIf you are in immediate physical danger, call emergency services (911/112).\n\nContinue?');
    
    if (confirmed) {
        alert('🤝 A crisis counsellor will be with you in moments.\n\nIn the meantime:\n• Practice deep breathing (in for 4, hold for 4, out for 6)\n• Go to a safe place\n• Keep yourself grounded');
        counsellingPortal.logAction('Crisis support activated');
    }
}

// Mindfulness
function startMindfulness() {
    alert('🧘 Starting Guided Mindfulness Exercise\n\nClosing your eyes and focusing on your breath...\n\n1. Inhale for 4 counts\n2. Hold for 4 counts\n3. Exhale for 6 counts\n\nRepeat 10 times. You are safe.');
    counsellingPortal.logAction('Mindfulness exercise started');
}

// Crisis Hotlines
function viewCrisisHotlines() {
    const hotlines = `
    📞 CRISIS HOTLINES

    🌍 International:
    • International Association for Suicide Prevention
    • Find your country: https://www.iasp.info/resources/Crisis_Centres/

    🇮🇳 India:
    • AASRA: 9820466726
    • iCall: 9152987821
    • Vandrevala Foundation: 9999 77 6666

    🇺🇸 United States:
    • 988 Suicide & Crisis Lifeline
    • Crisis Text Line: Text HOME to 741741

    All hotlines are FREE, 24/7, and ANONYMOUS
    `;
    console.log(hotlines);
    alert(hotlines);
    counsellingPortal.logAction('Crisis hotlines viewed');
}

// View Resources
function viewResources(category) {
    const resources = {
        'mental-health': {
            title: '📖 Mental Health Resources',
            content: `
Anxiety Management:
• Progressive Muscle Relaxation
• Box Breathing Technique
• Cognitive Behavioral Therapy (CBT) Basics

Depression Support:
• Daily Routine Building
• Behavioral Activation
• Thought Challenging Exercises

Stress Relief:
• Journaling Prompts
• Meditation Guides
• Physical Activity Ideas
            `
        },
        'legal': {
            title: '⚖️ Legal Resources',
            content: `
Know Your Rights:
• Domestic Violence Protection Act
• Workplace Harassment Laws
• Sexual Harassment Redressal
• Property Rights
• Custody Laws

What to Do:
• Document incidents
• File FIR (First Information Report)
• Obtain Protection Orders
• Legal Aid Services
• Evidence Collection Guide
            `
        }
    };

    const resource = resources[category] || resources['mental-health'];
    alert(resource.title + '\n\n' + resource.content);
    counsellingPortal.logAction('Resources viewed: ' + category);
}

// View Directory
function viewDirectory() {
    alert(`
📍 NEARBY SUPPORT ORGANIZATIONS

Legal Support:
• Women's Rights Organizations
• Free Legal Aid Clinics
• Bar Association Referrals

Health Services:
• Trauma-Informed Therapists
• Psychiatrists
• Counselling Centers

Shelters & Safe Houses:
• Women's Shelters
• Emergency Accommodation
• Transitional Housing

This feature will show local resources based on your location in production.
    `);
    counsellingPortal.logAction('Directory viewed');
}

// Build Action Plan
function buildActionPlan() {
    const plan = prompt('Enter your personal crisis action plan:\n\nInclude:\n1. Warning signs\n2. Internal coping strategies\n3. People to contact\n4. Professional support\n5. Ways to make environment safer');
    
    if (plan) {
        const actionPlanData = {
            plan: plan,
            createdAt: new Date().toISOString()
        };
        localStorage.setItem('crisis_action_plan', JSON.stringify(actionPlanData));
        alert('✅ Your Crisis Action Plan has been saved!\n\nYou can access it anytime from the Resources section.');
        counsellingPortal.logAction('Action plan created');
    }
}

// View Educational Content
function viewEducationalContent() {
    alert(`
📚 EDUCATIONAL MATERIALS

Understanding Mental Health:
• What is Depression?
• What is Anxiety?
• PTSD and Trauma Recovery
• Relationship Patterns
• Grief and Loss

Recovery & Healing:
• Neuroplasticity & Change
• Building Resilience
• Healthy Boundaries
• Self-Compassion
• Growth After Adversity

Expert Articles:
• Latest research
• Recovery stories
• Expert interviews
    `);
    counsellingPortal.logAction('Educational content viewed');
}

// Calming Tools
function openCalmingTools() {
    alert(`
🎵 CALMING TOOLS & EXERCISES

Meditation:
• 5-minute guided meditation
• 10-minute body scan
• 20-minute deep relaxation

Breathing Exercises:
• Box Breathing (4-4-4-4)
• 4-7-8 Technique
• Belly Breathing

Grounding Techniques:
• 5 Senses Exercise
• Progressive Muscle Relaxation
• Cold Water Immersion

Mindful Activities:
• Guided Journaling
• Coloring Exercises
• Gentle Yoga Sequences

Starting a 5-minute meditation...
    `);
    counsellingPortal.logAction('Calming tools opened');
}

// View Session History
function viewSessionHistory() {
    try {
        const sessions = JSON.parse(localStorage.getItem('counselling_sessions') || '[]');
        
        if (sessions.length === 0) {
            alert('No session history yet. Start a conversation to create history.');
        } else {
            let historyText = `📋 SESSION HISTORY (${sessions.length} sessions)\n\n`;
            sessions.slice(-5).reverse().forEach((session, idx) => {
                const date = new Date(session.timestamp).toLocaleDateString();
                historyText += `${idx + 1}. ${session.service} - ${date}\n`;
            });
            alert(historyText);
        }
    } catch (e) {
        alert('Error loading history: ' + e.message);
    }
    counsellingPortal.logAction('Session history viewed');
}

// Export Sessions
function exportSessions() {
    try {
        const sessions = JSON.parse(localStorage.getItem('counselling_sessions') || '[]');
        const dataStr = JSON.stringify(sessions, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `counselling_sessions_${Date.now()}.json`;
        link.click();
        alert('✅ Sessions exported successfully!');
        counsellingPortal.logAction('Sessions exported');
    } catch (e) {
        alert('Error exporting sessions: ' + e.message);
    }
}

// Clear Chat History
function clearChatHistory() {
    if (confirm('Clear all chat messages? This cannot be undone.')) {
        counsellingPortal.chatHistory = [];
        const chatBox = document.getElementById('ai-chat-box');
        if (chatBox) {
            chatBox.innerHTML = `
                <div class="chat-message bot-message">
                    <div class="message-avatar">🤖</div>
                    <div class="message-content">
                        <p>Hi! I'm here to listen and support you. How are you feeling today?</p>
                    </div>
                </div>
            `;
        }
        alert('✅ Chat history cleared.');
        counsellingPortal.logAction('Chat history cleared');
    }
}

// Download Session
function downloadSession() {
    const history = counsellingPortal.chatHistory;
    if (history.length === 0) {
        alert('No messages to download yet.');
        return;
    }

    let transcript = `COUNSELLING SESSION TRANSCRIPT\nSession ID: ${counsellingPortal.sessionID}\nDate: ${new Date().toLocaleString()}\n\n`;
    
    history.forEach(msg => {
        const time = new Date(msg.timestamp).toLocaleTimeString();
        transcript += `[${time}] ${msg.type.toUpperCase()}: ${msg.message}\n\n`;
    });

    const blob = new Blob([transcript], {type: 'text/plain'});
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `session_${counsellingPortal.sessionID}.txt`;
    link.click();
    alert('✅ Session downloaded!');
    counsellingPortal.logAction('Session downloaded');
}

// Delete All Data
function deleteAllData() {
    if (confirm('⚠️ This will permanently delete ALL session data, chat history, and settings.\n\nThis cannot be undone. Are you sure?')) {
        if (confirm('Confirm deletion of all counselling data?')) {
            localStorage.removeItem('counselling_sessions');
            localStorage.removeItem('crisis_action_plan');
            localStorage.removeItem('privacy_autoClear');
            localStorage.removeItem('privacy_encrypt');
            localStorage.removeItem('privacy_share');
            counsellingPortal.chatHistory = [];
            alert('✅ All data has been permanently deleted.');
            counsellingPortal.logAction('All data deleted');
        }
    }
}

// Get New Affirmation
function getNewAffirmation() {
    counsellingPortal.displayDailyAffirmation();
}

// AI Chat topic shortcuts
function askAIAbout(topic) {
    const prompts = {
        anxiety: "I'm feeling anxious right now. Can you help me?",
        stress: "I'm stressed about everything. Where do I start?",
        relationships: "I'm struggling with my relationships.",
        confidence: "I'm lacking confidence in myself."
    };

    const input = document.getElementById('ai-message-input');
    if (input) {
        input.value = prompts[topic] || "Tell me more.";
        counsellingPortal.sendAIMessage();
    }
}
