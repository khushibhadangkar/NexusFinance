/**
 * Advanced Notification System for Financial Goal Planner
 * Provides toast notifications, alerts, and user feedback
 */

class NotificationManager {
    constructor() {
        this.container = null;
        this.notifications = new Map();
        this.init();
    }

    init() {
        this.createContainer();
        this.setupStyles();
    }

    createContainer() {
        // Create notification container if it doesn't exist
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
            this.container = container;
        } else {
            this.container = document.getElementById('notification-container');
        }
    }

    setupStyles() {
        // Add styles if not already present
        if (!document.getElementById('notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                .notification-container {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 10000;
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                    max-width: 400px;
                    pointer-events: none;
                }

                .notification {
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
                    padding: 16px 20px;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    min-width: 300px;
                    max-width: 400px;
                    transform: translateX(100%);
                    opacity: 0;
                    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
                    pointer-events: auto;
                    position: relative;
                    overflow: hidden;
                }

                .notification.show {
                    transform: translateX(0);
                    opacity: 1;
                }

                .notification.hide {
                    transform: translateX(100%);
                    opacity: 0;
                }

                .notification-icon {
                    width: 24px;
                    height: 24px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                    font-size: 14px;
                    font-weight: bold;
                    color: white;
                }

                .notification-content {
                    flex: 1;
                    min-width: 0;
                }

                .notification-title {
                    font-weight: 600;
                    font-size: 14px;
                    margin-bottom: 4px;
                    color: #1e293b;
                }

                .notification-message {
                    font-size: 13px;
                    color: #64748b;
                    line-height: 1.4;
                }

                .notification-close {
                    position: absolute;
                    top: 8px;
                    right: 8px;
                    background: none;
                    border: none;
                    color: #94a3b8;
                    cursor: pointer;
                    padding: 4px;
                    border-radius: 4px;
                    transition: color 0.2s;
                    font-size: 16px;
                    line-height: 1;
                }

                .notification-close:hover {
                    color: #64748b;
                }

                .notification-progress {
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    height: 3px;
                    background: rgba(0, 0, 0, 0.1);
                    transition: width 0.1s linear;
                }

                /* Notification Types */
                .notification.success {
                    border-left: 4px solid #10b981;
                }

                .notification.success .notification-icon {
                    background: #10b981;
                }

                .notification.error {
                    border-left: 4px solid #ef4444;
                }

                .notification.error .notification-icon {
                    background: #ef4444;
                }

                .notification.warning {
                    border-left: 4px solid #f59e0b;
                }

                .notification.warning .notification-icon {
                    background: #f59e0b;
                }

                .notification.info {
                    border-left: 4px solid #3b82f6;
                }

                .notification.info .notification-icon {
                    background: #3b82f6;
                }

                /* Mobile Responsive */
                @media (max-width: 768px) {
                    .notification-container {
                        top: 10px;
                        right: 10px;
                        left: 10px;
                        max-width: none;
                    }

                    .notification {
                        min-width: auto;
                        max-width: none;
                    }
                }

                /* Animation for progress bar */
                @keyframes progress {
                    from { width: 100%; }
                    to { width: 0%; }
                }
            `;
            document.head.appendChild(style);
        }
    }

    show(message, type = 'info', options = {}) {
        const id = this.generateId();
        const notification = this.createNotification(id, message, type, options);
        
        this.container.appendChild(notification);
        this.notifications.set(id, notification);

        // Trigger animation
        requestAnimationFrame(() => {
            notification.classList.add('show');
        });

        // Auto remove if duration is specified
        if (options.duration !== false) {
            const duration = options.duration || this.getDefaultDuration(type);
            this.scheduleRemoval(id, duration);
        }

        return id;
    }

    createNotification(id, message, type, options) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.dataset.id = id;

        const icon = this.getIcon(type);
        const title = options.title || this.getDefaultTitle(type);

        notification.innerHTML = `
            <div class="notification-icon">${icon}</div>
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" onclick="notificationManager.remove('${id}')">×</button>
            <div class="notification-progress"></div>
        `;

        // Add click to dismiss if specified
        if (options.clickToDismiss !== false) {
            notification.addEventListener('click', () => {
                this.remove(id);
            });
        }

        return notification;
    }

    getIcon(type) {
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        return icons[type] || icons.info;
    }

    getDefaultTitle(type) {
        const titles = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Info'
        };
        return titles[type] || titles.info;
    }

    getDefaultDuration(type) {
        const durations = {
            success: 4000,
            error: 6000,
            warning: 5000,
            info: 4000
        };
        return durations[type] || 4000;
    }

    scheduleRemoval(id, duration) {
        const notification = this.notifications.get(id);
        if (!notification) return;

        const progressBar = notification.querySelector('.notification-progress');
        if (progressBar) {
            progressBar.style.animation = `progress ${duration}ms linear forwards`;
        }

        setTimeout(() => {
            this.remove(id);
        }, duration);
    }

    remove(id) {
        const notification = this.notifications.get(id);
        if (!notification) return;

        notification.classList.add('hide');
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
            this.notifications.delete(id);
        }, 300);
    }

    clear() {
        this.notifications.forEach((notification, id) => {
            this.remove(id);
        });
    }

    generateId() {
        return 'notification_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    // Convenience methods
    success(message, options = {}) {
        return this.show(message, 'success', options);
    }

    error(message, options = {}) {
        return this.show(message, 'error', options);
    }

    warning(message, options = {}) {
        return this.show(message, 'warning', options);
    }

    info(message, options = {}) {
        return this.show(message, 'info', options);
    }
}

// Create global notification manager
window.notificationManager = new NotificationManager();

// Global convenience functions
window.showToast = (message, type = 'info', options = {}) => {
    return notificationManager.show(message, type, options);
};

window.showSuccess = (message, options = {}) => {
    return notificationManager.success(message, options);
};

window.showError = (message, options = {}) => {
    return notificationManager.error(message, options);
};

window.showWarning = (message, options = {}) => {
    return notificationManager.warning(message, options);
};

window.showInfo = (message, options = {}) => {
    return notificationManager.info(message, options);
};


