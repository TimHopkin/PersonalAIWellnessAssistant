// Personal AI Wellness Assistant - Main JavaScript

// Global utilities
window.WellnessApp = {
    // Show toast notifications
    showToast: function(message, type = 'info', duration = 5000) {
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'warning' ? 'warning' : type === 'error' ? 'danger' : 'info'} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : type === 'error' ? 'times-circle' : 'info-circle'} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = toastContainer.lastElementChild;
        const toast = new bootstrap.Toast(toastElement, { delay: duration });
        toast.show();
        
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
        
        return toast;
    },
    
    // Loading state management
    setLoading: function(element, loading = true) {
        if (loading) {
            element.disabled = true;
            element.classList.add('loading');
            const originalHTML = element.innerHTML;
            element.dataset.originalHtml = originalHTML;
            
            if (element.tagName === 'BUTTON') {
                element.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
            }
        } else {
            element.disabled = false;
            element.classList.remove('loading');
            if (element.dataset.originalHtml) {
                element.innerHTML = element.dataset.originalHtml;
                delete element.dataset.originalHtml;
            }
        }
    },
    
    // API request wrapper
    apiRequest: async function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        const mergedOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, mergedOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            this.showToast('Network error: ' + error.message, 'error');
            throw error;
        }
    },
    
    // Format date for display
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            weekday: 'short',
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },
    
    // Format time for display
    formatTime: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    },
    
    // Calculate BMI
    calculateBMI: function(weight, height) {
        if (!weight || !height) return null;
        const heightInMeters = height / 100;
        return weight / (heightInMeters * heightInMeters);
    },
    
    // Get BMI category
    getBMICategory: function(bmi) {
        if (bmi < 18.5) return { category: 'Underweight', class: 'text-info' };
        if (bmi < 25) return { category: 'Normal weight', class: 'text-success' };
        if (bmi < 30) return { category: 'Overweight', class: 'text-warning' };
        return { category: 'Obese', class: 'text-danger' };
    },
    
    // Initialize page-specific functionality
    initPage: function() {
        this.initCommonFeatures();
        this.initPageSpecific();
    },
    
    // Common features across all pages
    initCommonFeatures: function() {
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Initialize popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function(popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
        
        // Auto-dismiss alerts after 5 seconds
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(alert => {
            setTimeout(() => {
                if (alert && alert.parentNode) {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }
            }, 5000);
        });
        
        // Add fade-in animation to cards
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('fade-in-up');
        });
    },
    
    // Page-specific initialization
    initPageSpecific: function() {
        const pathname = window.location.pathname;
        
        if (pathname === '/') {
            this.initDashboard();
        } else if (pathname === '/profile') {
            this.initProfile();
        } else if (pathname === '/plan') {
            this.initPlan();
        } else if (pathname === '/schedule') {
            this.initSchedule();
        } else if (pathname === '/progress') {
            this.initProgress();
        } else if (pathname === '/reports') {
            this.initReports();
        }
    },
    
    // Dashboard specific functionality
    initDashboard: function() {
        // Auto-refresh dashboard stats every 5 minutes
        setInterval(() => {
            this.refreshDashboardStats();
        }, 5 * 60 * 1000);
        
        // Initialize quick action buttons
        const quickActions = document.querySelectorAll('.quick-action');
        quickActions.forEach(action => {
            action.addEventListener('click', this.handleQuickAction.bind(this));
        });
    },
    
    // Profile specific functionality
    initProfile: function() {
        const ageInput = document.getElementById('age');
        const weightInput = document.getElementById('weight');
        const heightInput = document.getElementById('height');
        
        if (ageInput && weightInput && heightInput) {
            [ageInput, weightInput, heightInput].forEach(input => {
                input.addEventListener('input', this.updateBMICalculator);
            });
        }
        
        // Initialize form validation
        const profileForm = document.getElementById('profileForm');
        if (profileForm) {
            profileForm.addEventListener('submit', this.handleProfileSubmit.bind(this));
        }
    },
    
    // Plan specific functionality
    initPlan: function() {
        // Initialize plan generation
        const generateForm = document.getElementById('generatePlanForm');
        if (generateForm) {
            generateForm.addEventListener('submit', this.handlePlanGeneration.bind(this));
        }
        
        // Initialize chat functionality
        this.initChatFunctionality();
    },
    
    // Schedule specific functionality
    initSchedule: function() {
        // Initialize calendar functionality
        this.initCalendarView();
    },
    
    // Progress specific functionality
    initProgress: function() {
        // Initialize progress charts
        this.initProgressCharts();
        
        // Initialize activity tracking forms
        const trackingForms = document.querySelectorAll('.tracking-form');
        trackingForms.forEach(form => {
            form.addEventListener('submit', this.handleActivityTracking.bind(this));
        });
    },
    
    // Reports specific functionality
    initReports: function() {
        // Initialize report charts
        this.initReportCharts();
    },
    
    // Utility functions
    refreshDashboardStats: function() {
        this.apiRequest('/api/dashboard-stats')
            .then(data => {
                this.updateDashboardUI(data);
            })
            .catch(error => {
                console.error('Failed to refresh dashboard stats:', error);
            });
    },
    
    updateDashboardUI: function(stats) {
        // Update completion rate
        const completionElement = document.querySelector('.completion-rate');
        if (completionElement) {
            completionElement.textContent = `${(stats.weekly_completion_rate * 100).toFixed(1)}%`;
        }
        
        // Update streak
        const streakElement = document.querySelector('.streak-count');
        if (streakElement) {
            streakElement.textContent = stats.current_streak;
        }
    },
    
    handleQuickAction: function(event) {
        const action = event.currentTarget.dataset.action;
        
        switch (action) {
            case 'complete-activity':
                this.completeActivity(event.currentTarget.dataset.activityId);
                break;
            case 'skip-activity':
                this.skipActivity(event.currentTarget.dataset.activityId);
                break;
            case 'generate-plan':
                window.location.href = '/plan';
                break;
            default:
                console.warn('Unknown quick action:', action);
        }
    },
    
    handleProfileSubmit: function(event) {
        event.preventDefault();
        
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        this.setLoading(submitBtn, true);
        
        // Add any additional validation here
        const isValid = this.validateProfileForm(form);
        
        if (isValid) {
            form.submit();
        } else {
            this.setLoading(submitBtn, false);
        }
    },
    
    validateProfileForm: function(form) {
        const age = parseInt(form.age.value);
        const weight = parseFloat(form.weight.value);
        const height = parseFloat(form.height.value);
        
        if (age < 13 || age > 120) {
            this.showToast('Please enter a valid age between 13 and 120', 'error');
            return false;
        }
        
        if (weight < 30 || weight > 300) {
            this.showToast('Please enter a valid weight between 30 and 300 kg', 'error');
            return false;
        }
        
        if (height < 100 || height > 250) {
            this.showToast('Please enter a valid height between 100 and 250 cm', 'error');
            return false;
        }
        
        return true;
    },
    
    updateBMICalculator: function() {
        const weight = parseFloat(document.getElementById('weight').value);
        const height = parseFloat(document.getElementById('height').value);
        
        const bmiResultDiv = document.getElementById('bmiResult');
        const bmiValueSpan = document.getElementById('bmiValue');
        const bmiCategoryDiv = document.getElementById('bmiCategory');
        
        if (weight && height && bmiResultDiv && bmiValueSpan && bmiCategoryDiv) {
            const bmi = WellnessApp.calculateBMI(weight, height);
            const category = WellnessApp.getBMICategory(bmi);
            
            bmiValueSpan.textContent = bmi.toFixed(1);
            bmiCategoryDiv.textContent = category.category;
            bmiCategoryDiv.className = `mb-0 ${category.class} fw-bold`;
            
            bmiResultDiv.classList.remove('d-none');
        } else if (bmiResultDiv) {
            bmiResultDiv.classList.add('d-none');
        }
    },
    
    // Chart initialization functions
    initProgressCharts: function() {
        // Implementation for progress charts
        const ctx = document.getElementById('progressChart');
        if (ctx) {
            // Chart implementation would go here
            console.log('Initializing progress charts');
        }
    },
    
    initReportCharts: function() {
        // Implementation for report charts
        const reportCharts = document.querySelectorAll('.report-chart');
        reportCharts.forEach(chart => {
            // Chart implementation would go here
            console.log('Initializing report chart:', chart.id);
        });
    },
    
    initCalendarView: function() {
        // Implementation for calendar view
        const calendar = document.getElementById('calendar');
        if (calendar) {
            console.log('Initializing calendar view');
        }
    },
    
    // Chat functionality
    initChatFunctionality: function() {
        try {
            console.log('🔧 Initializing chat functionality...');
            this.currentChatSession = null;
            this.chatConnected = false;
            
            const chatForm = document.getElementById('chatForm');
            const chatInput = document.getElementById('chatInput');
            const chatMessages = document.getElementById('chatMessages');
            const sendBtn = document.getElementById('sendBtn');
            const charCount = document.getElementById('charCount');
            const inputStatus = document.getElementById('inputStatus');
            const connectionStatus = document.getElementById('connectionStatus');
            
            console.log('🔍 Chat elements found:', {
                chatForm: !!chatForm,
                chatInput: !!chatInput,
                chatMessages: !!chatMessages,
                sendBtn: !!sendBtn,
                charCount: !!charCount,
                inputStatus: !!inputStatus,
                connectionStatus: !!connectionStatus
            });
            
            if (chatForm && chatInput && chatMessages && sendBtn) {
                // Initialize UI state
                this.updateConnectionStatus(true);
                this.updateInputStatus('Ready to send');
                
                // Character counter
                if (charCount) {
                    chatInput.addEventListener('input', () => {
                        const length = chatInput.value.length;
                        charCount.textContent = length;
                        
                        if (length > 800) {
                            charCount.className = 'text-warning';
                        } else if (length > 950) {
                            charCount.className = 'text-danger';
                        } else {
                            charCount.className = 'text-muted';
                        }
                        
                        // Enable/disable send button based on input
                        sendBtn.disabled = length === 0 || length > 1000;
                        this.updateInputStatus(length === 0 ? 'Type a message...' : 
                                            length > 1000 ? 'Message too long' : 'Ready to send');
                    });
                }
                
                // Form submission
                chatForm.addEventListener('submit', (e) => {
                    console.log('📝 Chat form submit event triggered');
                    e.preventDefault();
                    e.stopPropagation();
                    
                    try {
                        const message = chatInput.value.trim();
                        console.log('💬 Chat message:', message);
                        
                        if (!message) {
                            console.log('❌ Empty message, skipping');
                            this.updateInputStatus('Type a message...');
                            return;
                        }
                        
                        if (message.length > 1000) {
                            console.log('❌ Message too long');
                            this.updateInputStatus('Message too long');
                            this.showToast('Message must be 1000 characters or less', 'warning');
                            return;
                        }
                        
                        // Prevent multiple submissions
                        if (sendBtn.disabled && sendBtn.innerHTML.includes('spinner')) {
                            console.log('🚫 Already sending message, preventing duplicate submission');
                            return;
                        }
                        
                        // Add user message to chat
                        console.log('➕ Adding user message to chat');
                        this.addUserMessage(message);
                        
                        // Clear input and update UI
                        chatInput.value = '';
                        if (charCount) charCount.textContent = '0';
                        this.setSendingState(true);
                        console.log('🔄 UI updated, sending message to AI...');
                        
                        // Send message to AI
                        this.sendChatMessage(message);
                    } catch (error) {
                        console.error('❌ Error handling chat form submit:', error);
                        this.showToast('Error sending message: ' + error.message, 'error');
                        this.setSendingState(false);
                    }
                });
                
                // Prevent form from closing modal on enter
                chatInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('⌨️ Enter key pressed, triggering form submit');
                        if (!sendBtn.disabled) {
                            chatForm.dispatchEvent(new Event('submit'));
                        }
                    }
                });
                
                // Focus input when modal opens
                const chatModal = document.getElementById('chatModal');
                if (chatModal) {
                    chatModal.addEventListener('shown.bs.modal', () => {
                        chatInput.focus();
                        this.updateConnectionStatus(true);
                    });
                }
                
                console.log('✅ Chat functionality initialized successfully');
            } else {
                console.log('❌ Chat elements not found on this page');
            }
        } catch (error) {
            console.error('❌ Error initializing chat functionality:', error);
            this.showToast('Failed to initialize chat functionality', 'error');
        }
    },
    
    updateConnectionStatus: function(connected) {
        const connectionStatus = document.getElementById('connectionStatus');
        const connectionAlert = document.getElementById('connectionAlert');
        const connectionMessage = document.getElementById('connectionMessage');
        
        this.chatConnected = connected;
        
        if (connectionStatus) {
            if (connected) {
                connectionStatus.textContent = 'Connected';
                connectionStatus.className = 'badge bg-success ms-2';
            } else {
                connectionStatus.textContent = 'Disconnected';
                connectionStatus.className = 'badge bg-danger ms-2';
            }
        }
        
        if (connectionAlert) {
            if (connected) {
                connectionAlert.classList.add('d-none');
            } else {
                connectionAlert.classList.remove('d-none');
                if (connectionMessage) {
                    connectionMessage.textContent = 'Unable to connect to the AI service. Please check your internet connection.';
                }
            }
        }
    },
    
    updateInputStatus: function(status) {
        const inputStatus = document.getElementById('inputStatus');
        if (inputStatus) {
            inputStatus.textContent = status;
        }
    },
    
    setSendingState: function(sending) {
        const sendBtn = document.getElementById('sendBtn');
        const chatInput = document.getElementById('chatInput');
        const closeBtn = document.getElementById('closeBtn');
        
        if (sendBtn) {
            if (sending) {
                sendBtn.disabled = true;
                sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                this.updateInputStatus('Sending message...');
            } else {
                sendBtn.disabled = chatInput && chatInput.value.trim().length === 0;
                sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
                this.updateInputStatus('Ready to send');
            }
        }
        
        if (chatInput) {
            chatInput.disabled = sending;
        }
        
        if (closeBtn) {
            closeBtn.disabled = sending;
        }
    },
    
    retryConnection: function() {
        console.log('🔄 Retrying connection...');
        this.updateConnectionStatus(true);
        this.showToast('Retrying connection...', 'info');
        
        // Try a simple ping to test connectivity
        fetch('/api/chat-sessions', { method: 'GET' })
            .then(response => {
                if (response.ok) {
                    this.updateConnectionStatus(true);
                    this.showToast('Connection restored!', 'success');
                } else {
                    throw new Error('Server responded with error');
                }
            })
            .catch(error => {
                console.error('Connection test failed:', error);
                this.updateConnectionStatus(false);
                this.showToast('Connection test failed. Please try again.', 'error');
            });
    },
    
    addUserMessage: function(message) {
        try {
            const chatMessages = document.getElementById('chatMessages');
            if (!chatMessages) return;
            
            const messageHtml = `
                <div class="message user-message mb-3">
                    <div class="d-flex justify-content-end">
                        <div class="flex-grow-1" style="max-width: 70%;">
                            <div class="bg-primary text-white p-3 rounded shadow-sm">
                                <p class="mb-0">${this.escapeHtml(message)}</p>
                            </div>
                        </div>
                        <div class="flex-shrink-0 ms-3">
                            <div class="bg-secondary rounded-circle d-flex align-items-center justify-content-center" style="width: 35px; height: 35px;">
                                <i class="fas fa-user text-white"></i>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            chatMessages.insertAdjacentHTML('beforeend', messageHtml);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } catch (error) {
            console.error('Error adding user message:', error);
        }
    },
    
    addAIMessage: function(message, isTyping = false) {
        try {
            const chatMessages = document.getElementById('chatMessages');
            if (!chatMessages) return null;
            
            const messageId = 'ai-msg-' + Date.now();
            
            const messageHtml = `
                <div class="message ai-message mb-3" id="${messageId}">
                    <div class="d-flex">
                        <div class="flex-shrink-0 me-3">
                            <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center" style="width: 35px; height: 35px;">
                                <i class="fas fa-robot text-white"></i>
                            </div>
                        </div>
                        <div class="flex-grow-1">
                            <div class="bg-white p-3 rounded shadow-sm">
                                ${isTyping ? '<div class="typing-indicator"><span></span><span></span><span></span></div>' : `<p class="mb-0">${message}</p>`}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            chatMessages.insertAdjacentHTML('beforeend', messageHtml);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            return messageId;
        } catch (error) {
            console.error('Error adding AI message:', error);
            return null;
        }
    },
    
    sendChatMessage: function(message) {
        const self = this;
        
        console.log('🚀 Sending chat message to API:', message);
        
        // Show typing indicator
        const typingId = this.addAIMessage('', true);
        console.log('💭 Added typing indicator with ID:', typingId);
        
        const requestBody = {
            message: message,
            session_id: this.currentChatSession
        };
        console.log('📤 Request payload:', requestBody);
        
        fetch('/api/chat-update-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        })
        .then(response => {
            console.log('📥 API response status:', response.status, response.statusText);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return response.json();
        })
        .then(data => {
            console.log('📊 API response data:', data);
            
            // Remove typing indicator
            const typingElement = document.getElementById(typingId);
            if (typingElement) {
                typingElement.remove();
                console.log('🗑️ Removed typing indicator');
            }
            
            if (data.success) {
                console.log('✅ API request successful');
                
                // Update session ID
                if (data.session_id) {
                    self.currentChatSession = data.session_id;
                    console.log('🔗 Updated session ID:', data.session_id);
                }
                
                // Add AI response
                if (data.response) {
                    self.addAIMessage(data.response);
                    console.log('💬 Added AI response');
                } else {
                    console.warn('⚠️ No AI response in successful response');
                    self.addAIMessage('I received your message but don\'t have a response to show.');
                }
                
                // If there are proposed changes, show them
                if (data.proposed_changes && data.proposed_changes.length > 0) {
                    self.showProposedChanges(data.proposed_changes);
                    console.log('🔧 Showed proposed changes:', data.proposed_changes.length);
                }
            } else {
                console.error('❌ API request failed:', data.error);
                const errorMessage = data.error || 'Unknown error occurred';
                self.addAIMessage('Sorry, I encountered an error: ' + errorMessage);
                self.showToast('Chat error: ' + errorMessage, 'error');
            }
        })
        .catch(error => {
            console.error('❌ Chat request failed:', error);
            
            // Remove typing indicator
            const typingElement = document.getElementById(typingId);
            if (typingElement) {
                typingElement.remove();
                console.log('🗑️ Removed typing indicator after error');
            }
            
            let errorMessage = 'Sorry, I encountered an error processing your request.';
            if (error.message.includes('Failed to fetch')) {
                errorMessage += ' Please check your internet connection.';
                self.updateConnectionStatus(false);
            } else if (error.message.includes('HTTP 5')) {
                errorMessage += ' The server is experiencing issues. Please try again later.';
            } else if (error.message.includes('HTTP 4')) {
                errorMessage += ' There was a problem with your request. Please try rephrasing.';
            } else {
                errorMessage += ' Please try again.';
            }
            
            self.addAIMessage(errorMessage);
            self.showToast('Chat error: ' + error.message, 'error');
        })
        .finally(() => {
            console.log('🔄 Resetting UI state');
            self.setSendingState(false);
        });
    },
    
    showProposedChanges: function(changes) {
        try {
            if (!changes || changes.length === 0) return;
            
            const changesList = changes.map(change => 
                `<li class="mb-1"><i class="fas fa-arrow-right text-primary me-2"></i>${this.escapeHtml(change)}</li>`
            ).join('');
            
            const proposedChangesHtml = `
                <div class="message ai-message mb-3">
                    <div class="d-flex">
                        <div class="flex-shrink-0 me-3">
                            <div class="bg-warning rounded-circle d-flex align-items-center justify-content-center" style="width: 35px; height: 35px;">
                                <i class="fas fa-exclamation text-white"></i>
                            </div>
                        </div>
                        <div class="flex-grow-1">
                            <div class="bg-warning bg-opacity-10 border border-warning p-3 rounded shadow-sm">
                                <h6 class="mb-2 text-warning"><i class="fas fa-check me-1"></i>Changes Applied</h6>
                                <p class="mb-2 small">The following changes have been made to your wellness plan:</p>
                                <ul class="mb-2 small">${changesList}</ul>
                                <p class="mb-0 small text-muted">
                                    <i class="fas fa-info-circle me-1"></i>
                                    Your plan has been automatically saved. Refresh the page to see the updated plan.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            const chatMessages = document.getElementById('chatMessages');
            if (chatMessages) {
                chatMessages.insertAdjacentHTML('beforeend', proposedChangesHtml);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        } catch (error) {
            console.error('Error showing proposed changes:', error);
        }
    },
    
    escapeHtml: function(text) {
        try {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        } catch (error) {
            console.error('Error escaping HTML:', error);
            return String(text).replace(/[&<>"']/g, function(match) {
                const escapeMap = {
                    '&': '&amp;',
                    '<': '&lt;',
                    '>': '&gt;',
                    '"': '&quot;',
                    "'": '&#39;'
                };
                return escapeMap[match];
            });
        }
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    WellnessApp.initPage();
});

// Global error handler
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    WellnessApp.showToast('An unexpected error occurred. Please try again.', 'error');
});

// Service worker disabled for this version
// Can be added later for offline functionality