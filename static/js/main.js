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
            this.currentChatSession = null;
            
            const chatForm = document.getElementById('chatForm');
            const chatInput = document.getElementById('chatInput');
            const chatMessages = document.getElementById('chatMessages');
            const sendBtn = document.getElementById('sendBtn');
            
            if (chatForm && chatInput && chatMessages && sendBtn) {
                chatForm.addEventListener('submit', (e) => {
                    e.preventDefault();
                    
                    try {
                        const message = chatInput.value.trim();
                        if (!message) return;
                        
                        // Add user message to chat
                        this.addUserMessage(message);
                        
                        // Clear input and disable send button
                        chatInput.value = '';
                        sendBtn.disabled = true;
                        sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                        
                        // Send message to AI
                        this.sendChatMessage(message);
                    } catch (error) {
                        console.error('Error handling chat form submit:', error);
                        this.showToast('Error sending message. Please try again.', 'error');
                    }
                });
                
                console.log('Chat functionality initialized');
            } else {
                console.log('Chat elements not found on this page');
            }
        } catch (error) {
            console.error('Error initializing chat functionality:', error);
        }
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
        
        // Show typing indicator
        const typingId = this.addAIMessage('', true);
        
        fetch('/api/chat-update-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                session_id: this.currentChatSession
            })
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            const typingElement = document.getElementById(typingId);
            if (typingElement) {
                typingElement.remove();
            }
            
            if (data.success) {
                // Update session ID
                if (data.session_id) {
                    self.currentChatSession = data.session_id;
                }
                
                // Add AI response
                self.addAIMessage(data.response);
                
                // If there are proposed changes, show them
                if (data.proposed_changes && data.proposed_changes.length > 0) {
                    self.showProposedChanges(data.proposed_changes);
                }
            } else {
                self.addAIMessage('Sorry, I encountered an error: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            // Remove typing indicator
            const typingElement = document.getElementById(typingId);
            if (typingElement) {
                typingElement.remove();
            }
            
            self.addAIMessage('Sorry, I encountered an error processing your request. Please try again.');
            console.error('Chat error:', error);
        })
        .finally(() => {
            // Re-enable send button
            const sendBtn = document.getElementById('sendBtn');
            if (sendBtn) {
                sendBtn.disabled = false;
                sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
            }
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

// Service worker registration for offline capability (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed');
            });
    });
}