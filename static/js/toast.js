// Toast Notification System

class Toast {
    constructor(message, type = 'info', duration = 4000) {
        this.message = message;
        this.type = type; // 'success', 'error', 'info', 'warning'
        this.duration = duration;
        this.element = null;
        this.create();
    }

    create() {
        try {
            // Create toast container if it doesn't exist
            let container = document.getElementById('toast-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'toast-container';
                container.className = 'toast-container';
                // Apply inline styles to ensure positioning works even if CSS doesn't load
                container.style.position = 'fixed';
                container.style.top = '20px';
                container.style.right = '20px';
                container.style.zIndex = '10000';
                container.style.display = 'flex';
                container.style.flexDirection = 'column';
                container.style.gap = '10px';
                container.style.pointerEvents = 'none';
                document.body.appendChild(container);
            }

            // Create toast element
            this.element = document.createElement('div');
            this.element.className = `toast toast-${this.type}`;
            
            // Apply initial inline styles to ensure visibility
            this.element.style.opacity = '0';
            this.element.style.transform = 'translateX(400px)';
            this.element.style.transition = 'all 0.3s ease';
            this.element.style.pointerEvents = 'auto';
            
            // Create icon based on type
            const icon = this.getIcon();
            
            // Create content
            this.element.innerHTML = `
                <div class="toast-content">
                    <span class="toast-icon">${icon}</span>
                    <span class="toast-message">${this.message}</span>
                </div>
                <button class="toast-close" onclick="this.parentElement.remove()">×</button>
            `;

            // Add to container
            container.appendChild(this.element);

            // Trigger animation - use requestAnimationFrame for better timing
            requestAnimationFrame(() => {
                setTimeout(() => {
                    if (this.element) {
                        this.element.classList.add('show');
                        // Also set inline styles to ensure it works
                        this.element.style.opacity = '1';
                        this.element.style.transform = 'translateX(0)';
                    }
                }, 50);
            });

            // Auto remove after duration
            if (this.duration > 0) {
                setTimeout(() => {
                    this.remove();
                }, this.duration);
            }
        } catch (error) {
            console.error('Error creating toast:', error);
        }
    }

    getIcon() {
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        return icons[this.type] || icons.info;
    }

    remove() {
        if (this.element) {
            this.element.classList.remove('show');
            setTimeout(() => {
                if (this.element && this.element.parentNode) {
                    this.element.parentNode.removeChild(this.element);
                }
            }, 300);
        }
    }
}

// Helper functions
function showToast(message, type = 'info', duration = 4000) {
    return new Toast(message, type, duration);
}

function showSuccess(message, duration = 4000) {
    return new Toast(message, 'success', duration);
}

function showError(message, duration = 5000) {
    return new Toast(message, 'error', duration);
}

function showWarning(message, duration = 4000) {
    return new Toast(message, 'warning', duration);
}

function showInfo(message, duration = 4000) {
    return new Toast(message, 'info', duration);
}

// Function to convert Django messages to Toast notifications
function convertDjangoMessages() {
    try {
        // Find all Django message elements - try multiple selectors
        // Only get elements that haven't been converted yet
        const messageElements = document.querySelectorAll('.messages li:not([data-toast-converted]), ul.messages li:not([data-toast-converted]), .msg:not([data-toast-converted]), .error:not([data-toast-converted])');
        
        messageElements.forEach(function(element) {
            // Mark as converted immediately to prevent duplicate processing
            element.setAttribute('data-toast-converted', 'true');
            
            let message = element.textContent.trim();
            let type = 'info';
            
            // Determine type from class - check all possible class names
            const classes = element.className.toLowerCase();
            if (classes.includes('success') || classes.includes('msg')) {
                type = 'success';
            } else if (classes.includes('error')) {
                type = 'error';
            } else if (classes.includes('warning')) {
                type = 'warning';
            } else if (classes.includes('info') || classes.includes('debug')) {
                type = 'info';
            }
            
            // Show toast only if message exists and hasn't been shown
            if (message && message.length > 0) {
                showToast(message, type);
            }
            
            // Hide original message element
            element.style.display = 'none';
        });
        
        // Also check for messages in ul.messages and hide the container
        const messageLists = document.querySelectorAll('ul.messages, .messages');
        messageLists.forEach(function(list) {
            // Only hide if it's empty or all children are hidden
            const visibleChildren = Array.from(list.children).filter(child => 
                child.style.display !== 'none' && window.getComputedStyle(child).display !== 'none'
            );
            if (visibleChildren.length === 0) {
                list.style.display = 'none';
            }
        });
        
        // Also check for standalone message divs (only unconverted ones)
        const messageDivs = document.querySelectorAll('.msg:not([data-toast-converted]), .error:not([data-toast-converted]), .success:not([data-toast-converted]), .warning:not([data-toast-converted]), .info:not([data-toast-converted])');
        messageDivs.forEach(function(div) {
            // Mark as converted immediately
            div.setAttribute('data-toast-converted', 'true');
            
            if (div.textContent.trim()) {
                let type = 'info';
                const classes = div.className.toLowerCase();
                if (classes.includes('success') || classes.includes('msg')) {
                    type = 'success';
                } else if (classes.includes('error')) {
                    type = 'error';
                } else if (classes.includes('warning')) {
                    type = 'warning';
                }
                showToast(div.textContent.trim(), type);
                div.style.display = 'none';
            }
        });
    } catch (error) {
        console.error('Error converting Django messages:', error);
    }
}

// Track if we've already initialized to prevent multiple calls
let toastSystemInitialized = false;

// Run on DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    if (!toastSystemInitialized) {
        toastSystemInitialized = true;
        convertDjangoMessages();
    }
});

// Also run on window load as a fallback (but only if not already done)
window.addEventListener('load', function() {
    if (!toastSystemInitialized) {
        toastSystemInitialized = true;
        // Small delay to ensure everything is rendered
        setTimeout(convertDjangoMessages, 100);
    }
});

// Watch for new messages being added to the DOM (for dynamic content)
// Only convert new messages that haven't been processed
if (typeof MutationObserver !== 'undefined') {
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                // Check if any added nodes are message elements
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        // Check if it's a message element or contains message elements
                        const isMessageElement = node.classList && (
                            node.classList.contains('messages') || 
                            node.classList.contains('msg') || 
                            node.classList.contains('error')
                        );
                        
                        const hasMessageChildren = node.querySelector && node.querySelector(':not([data-toast-converted]) .messages, :not([data-toast-converted]) .msg, :not([data-toast-converted]) .error');
                        
                        if (isMessageElement || hasMessageChildren) {
                            // Only convert new, unconverted messages
                            setTimeout(function() {
                                const newMessages = node.querySelectorAll ? 
                                    node.querySelectorAll('.messages li:not([data-toast-converted]), .msg:not([data-toast-converted]), .error:not([data-toast-converted])') :
                                    [];
                                
                                if (newMessages.length > 0 || (node.matches && node.matches(':not([data-toast-converted]) .msg, :not([data-toast-converted]) .error'))) {
                                    convertDjangoMessages();
                                }
                            }, 50);
                        }
                    }
                });
            }
        });
    });
    
    // Start observing when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
}

// Make functions globally available
window.showToast = showToast;
window.showSuccess = showSuccess;
window.showError = showError;
window.showWarning = showWarning;
window.showInfo = showInfo;

// Test function - call window.testToast() in console to test
window.testToast = function() {
    showSuccess('Test success message!');
    setTimeout(() => showError('Test error message!'), 500);
    setTimeout(() => showWarning('Test warning message!'), 1000);
    setTimeout(() => showInfo('Test info message!'), 1500);
};

