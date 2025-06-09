/**
 * Smart Hospital Dashboard - Interactive Functionality
 * Handles dynamic data updates, chart animations, and user interactions
 */

class HospitalDashboard {
    constructor() {
        this.updateInterval = 30000; // 30 seconds
        this.charts = {};
        this.metrics = {};
        this.currentSection = 'dashboard'; // Track current section
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.startDataUpdates();
        this.setupNavigation();
        this.createSectionContainers();
    }

    createSectionContainers() {
        // The HTML structure is now pre-built in interface.py
        // We just need to ensure the dashboard section is active by default
        setTimeout(() => {
            this.switchToSection('dashboard');
        }, 100);
    }

    switchToSection(section) {
        console.log('Switching to section:', section);
        
        // Hide all section containers
        const allSections = document.querySelectorAll('.section-container');
        console.log('Found sections:', allSections.length);
        allSections.forEach((sec, index) => {
            console.log(`Section ${index}:`, sec.className);
            sec.classList.remove('active');
            sec.style.display = 'none'; // Force hide with inline style
        });
        
        // Show the selected section
        const targetSection = document.querySelector(`.section-${section}`);
        console.log('Target section:', targetSection);
        if (targetSection) {
            targetSection.classList.add('active');
            targetSection.style.display = 'block'; // Force show with inline style
            console.log('Section switched successfully to:', section);
        } else {
            console.error('Section not found:', section);
            // List all available sections for debugging
            const availableSections = document.querySelectorAll('[class*="section-"]');
            console.log('Available sections:', Array.from(availableSections).map(s => s.className));
        }
        
        // Update current section
        this.currentSection = section;
        
        // Load section-specific data
        this.loadSectionData(section);
    }

    setupEventListeners() {
        // Navigation buttons - Use MutationObserver to handle dynamically created buttons
        const observer = new MutationObserver(() => {
            const navBtns = document.querySelectorAll('.nav-btn');
            navBtns.forEach(btn => {
                if (!btn.hasAttribute('data-listener')) {
                    btn.addEventListener('click', (e) => this.handleNavigation(e));
                    btn.setAttribute('data-listener', 'true');
                }
            });

            // Metric cards hover effects
            const cards = document.querySelectorAll('.metric-card');
            cards.forEach(card => {
                if (!card.hasAttribute('data-listener')) {
                    card.addEventListener('mouseenter', (e) => this.animateCard(e.target, true));
                    card.addEventListener('mouseleave', (e) => this.animateCard(e.target, false));
                    card.setAttribute('data-listener', 'true');
                }
            });

            // Quick action buttons
            const actionBtns = document.querySelectorAll('.quick-action-btn, .header-action-btn');
            actionBtns.forEach(btn => {
                if (!btn.hasAttribute('data-listener')) {
                    btn.addEventListener('click', (e) => this.handleQuickAction(e));
                    btn.setAttribute('data-listener', 'true');
                }
            });

            // Alert action buttons
            const alertBtns = document.querySelectorAll('.alert-btn');
            alertBtns.forEach(btn => {
                if (!btn.hasAttribute('data-listener')) {
                    btn.addEventListener('click', (e) => this.handleAlertAction(e));
                    btn.setAttribute('data-listener', 'true');
                }
            });
        });

        observer.observe(document.body, { childList: true, subtree: true });
    }

    setupNavigation() {
        // Wait for elements to be available
        setTimeout(() => {
            const navBtns = document.querySelectorAll('.nav-btn');
            console.log('Setting up navigation, found buttons:', navBtns.length);
            
            // Set first button as active by default if none are active
            const hasActiveBtn = Array.from(navBtns).some(btn => btn.classList.contains('active'));
            if (navBtns.length > 0 && !hasActiveBtn) {
                navBtns[0].classList.add('active');
                console.log('Set first button as active');
            }
            
            // Ensure dashboard section is shown by default
            this.switchToSection('dashboard');
        }, 500);
    }

    handleNavigation(event) {
        const clickedBtn = event.target;
        const section = clickedBtn.getAttribute('data-section') || clickedBtn.textContent.toLowerCase();

        // Update active state
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        clickedBtn.classList.add('active');

        // Switch to the selected section
        this.switchToSection(section);
        
        // Show notification
        this.showNotification(`📊 Switched to ${clickedBtn.textContent} section`, 'info');
    }

    async loadSectionData(section) {
        console.log(`Loading ${section} section with simulated data...`);
        
        switch(section) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'alerts':
                this.loadAlertsData();
                break;
            case 'resources':
                this.loadResourcesData();
                break;
            case 'data':
                this.loadDataAnalyticsData();
                break;
        }
    }

    showLoadingState(section) {
        // Add subtle loading animation
        const currentSection = document.querySelector(`.section-${this.currentSection}`);
        if (currentSection) {
            currentSection.style.opacity = '0.7';
            setTimeout(() => {
                currentSection.style.opacity = '1';
            }, 500);
        }
    }

    handleAlertAction(event) {
        const button = event.target;
        const action = button.textContent.toLowerCase();
        const alertItem = button.closest('.alert-item');
        
        const originalText = button.textContent;
        button.style.opacity = '0.7';
        button.textContent = 'Processing...';
        
        setTimeout(() => {
            button.style.opacity = '1';
            button.textContent = originalText;
            
            if (action.includes('acknowledge') || action.includes('dispatch')) {
                // Fade out the alert
                alertItem.style.opacity = '0.5';
                alertItem.style.transform = 'translateX(20px)';
                this.showNotification(`Alert ${action}d successfully`, 'success');
            } else if (action.includes('reorder')) {
                this.showNotification('Reorder request submitted', 'success');
            } else {
                this.showNotification(`${action} action completed`, 'info');
            }
        }, 1000);
    }

    // Load different section data
    loadDashboardData() {
        console.log('Loading dashboard data...');
        this.simulateDataUpdate();
    }

    loadAlertsData() {
        console.log('Loading alerts data...');
        // Update alert counts with random numbers
        const criticalCount = Math.floor(Math.random() * 5) + 1;
        const warningCount = Math.floor(Math.random() * 10) + 3;
        const infoCount = Math.floor(Math.random() * 15) + 8;

        const criticalEl = document.querySelector('.alert-count.critical');
        const warningEl = document.querySelector('.alert-count.warning');
        const infoEl = document.querySelector('.alert-count.info');

        if (criticalEl) criticalEl.textContent = `${criticalCount} Critical`;
        if (warningEl) warningEl.textContent = `${warningCount} Warnings`;
        if (infoEl) infoEl.textContent = `${infoCount} Info`;
    }

    loadResourcesData() {
        console.log('Loading resources data...');
        // Animate inventory bars
        const inventoryFills = document.querySelectorAll('.inventory-fill');
        inventoryFills.forEach((fill, index) => {
            const currentWidth = fill.style.width;
            fill.style.width = '0%';
            setTimeout(() => {
                fill.style.width = currentWidth;
            }, index * 200);
        });
    }

    loadDataAnalyticsData() {
        console.log('Loading data analytics...');
        // Here you could implement data analytics specific updates
        this.showNotification('📈 Analytics data refreshed', 'success');
    }

    initializeCharts() {
        this.initICUOccupancyChart();
        this.initEmergencyLoadChart();
        this.initStaffAvailability();
        this.initToolUsageChart();
    }

    initICUOccupancyChart() {
        const circle = document.querySelector('.progress-circle-fill');
        const text = document.querySelector('.progress-text');
        
        if (circle && text) {
            this.metrics.icuOccupancy = {
                element: circle,
                textElement: text,
                value: 71,
                animate: (newValue) => {
                    const circumference = 2 * Math.PI * 54;
                    const offset = circumference - (newValue / 100) * circumference;
                    circle.style.strokeDashoffset = offset;
                    text.textContent = `${newValue}%`;
                }
            };
        }
    }

    initEmergencyLoadChart() {
        const loadPath = document.querySelector('.load-path');
        if (loadPath) {
            this.metrics.emergencyLoad = {
                element: loadPath,
                data: [70, 50, 45, 40, 35, 30, 25],
                animate: (newData) => {
                    const path = this.generateLoadPath(newData);
                    loadPath.setAttribute('d', path);
                }
            };
        }
    }

    initStaffAvailability() {
        const doctorsProgress = document.querySelector('.doctors-progress');
        const nursesProgress = document.querySelector('.nurses-progress');
        
        if (doctorsProgress && nursesProgress) {
            this.metrics.staffAvailability = {
                doctors: { element: doctorsProgress, value: 75 },
                nurses: { element: nursesProgress, value: 60 },
                animate: (doctorValue, nurseValue) => {
                    doctorsProgress.style.width = `${doctorValue}%`;
                    nursesProgress.style.width = `${nurseValue}%`;
                }
            };
        }
    }

    initToolUsageChart() {
        const bars = document.querySelectorAll('.usage-chart .bar');
        if (bars.length > 0) {
            this.metrics.toolUsage = {
                elements: Array.from(bars),
                values: [60, 40, 70, 35, 85],
                animate: (newValues) => {
                    bars.forEach((bar, index) => {
                        if (newValues[index] !== undefined) {
                            bar.style.height = `${newValues[index]}%`;
                        }
                    });
                }
            };
        }
    }

    generateLoadPath(data) {
        const points = data.map((value, index) => {
            const x = 10 + (index * 30);
            const y = 70 - (value * 0.8);
            return `${x} ${y}`;
        });
        
        return `M ${points[0]} Q ${points[1]} T ${points.slice(2).join(' T ')}`;
    }

    startDataUpdates() {
        // Initial update
        this.updateDashboardData();
        
        // Set up periodic updates
        setInterval(() => {
            this.updateDashboardData();
        }, this.updateInterval);
    }

    async updateDashboardData() {
        // Use simulated data for this demo version
        // In a production environment, this would fetch from a real API
        console.log('Updating dashboard with simulated real-time data...');
        this.simulateDataUpdate();
    }

    simulateDataUpdate() {
        // Simulate ICU occupancy changes
        const currentICU = this.metrics.icuOccupancy?.value || 71;
        const newICU = Math.max(50, Math.min(95, currentICU + (Math.random() - 0.5) * 10));
        this.updateICUOccupancy(Math.round(newICU));

        // Simulate staff availability changes
        const currentDoctors = this.metrics.staffAvailability?.doctors.value || 75;
        const currentNurses = this.metrics.staffAvailability?.nurses.value || 60;
        const newDoctors = Math.max(40, Math.min(90, currentDoctors + (Math.random() - 0.5) * 15));
        const newNurses = Math.max(30, Math.min(85, currentNurses + (Math.random() - 0.5) * 20));
        this.updateStaffAvailability(Math.round(newDoctors), Math.round(newNurses));

        // Simulate tool usage changes
        const newToolUsage = this.metrics.toolUsage?.values.map(val => 
            Math.max(20, Math.min(90, val + (Math.random() - 0.5) * 20))
        ) || [60, 40, 70, 35, 85];
        this.updateToolUsage(newToolUsage.map(val => Math.round(val)));

        // Simulate emergency load changes
        const newEmergencyData = Array.from({length: 7}, () => 
            Math.max(20, Math.min(80, 50 + (Math.random() - 0.5) * 40))
        );
        this.updateEmergencyLoad(newEmergencyData);
    }

    updateMetrics(data) {
        if (data.icuOccupancy !== undefined) {
            this.updateICUOccupancy(data.icuOccupancy);
        }
        if (data.staffAvailability) {
            this.updateStaffAvailability(
                data.staffAvailability.doctors, 
                data.staffAvailability.nurses
            );
        }
        if (data.toolUsage) {
            this.updateToolUsage(data.toolUsage);
        }
        if (data.emergencyLoad) {
            this.updateEmergencyLoad(data.emergencyLoad);
        }
    }

    updateICUOccupancy(value) {
        if (this.metrics.icuOccupancy) {
            this.metrics.icuOccupancy.value = value;
            this.metrics.icuOccupancy.animate(value);
        }
    }

    updateStaffAvailability(doctorValue, nurseValue) {
        if (this.metrics.staffAvailability) {
            this.metrics.staffAvailability.doctors.value = doctorValue;
            this.metrics.staffAvailability.nurses.value = nurseValue;
            this.metrics.staffAvailability.animate(doctorValue, nurseValue);
        }
    }

    updateToolUsage(values) {
        if (this.metrics.toolUsage) {
            this.metrics.toolUsage.values = values;
            this.metrics.toolUsage.animate(values);
        }
    }

    updateEmergencyLoad(data) {
        if (this.metrics.emergencyLoad) {
            this.metrics.emergencyLoad.data = data;
            this.metrics.emergencyLoad.animate(data);
        }
    }

    animateCard(card, isHovering) {
        if (isHovering) {
            card.style.transform = 'translateY(-4px) scale(1.02)';
            card.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.15)';
        } else {
            card.style.transform = 'translateY(0) scale(1)';
            card.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.05)';
        }
    }

    handleQuickAction(event) {
        const button = event.target;
        const action = button.textContent.toLowerCase();
        
        // Add loading state
        const originalText = button.textContent;
        button.style.opacity = '0.7';
        button.textContent = 'Loading...';
        
        // Simulate action processing
        setTimeout(() => {
            button.style.opacity = '1';
            button.textContent = originalText;
            
            // Trigger appropriate action
            if (action.includes('status')) {
                this.refreshAllMetrics();
            }
        }, 1000);
    }

    refreshAllMetrics() {
        this.simulateDataUpdate();
        
        // Show success feedback
        this.showNotification('Dashboard updated successfully', 'success');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : '#3b82f6'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 1000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after delay
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    updateSectionContent(section, data) {
        // Update the dashboard content based on section and data
        console.log(`Updating ${section} with data:`, data);
        
        if (section === 'dashboard') {
            this.updateMetrics(data);
        } else {
            // For other sections, you could update different parts of the UI
            // This is where you'd implement section-specific UI updates
            this.showNotification(`${section.charAt(0).toUpperCase() + section.slice(1)} data updated`, 'info');
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.hospitalDashboard = new HospitalDashboard();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HospitalDashboard;
} 