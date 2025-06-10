class HospitalDashboard {
    constructor() {
        this.updateInterval = 30000; // 30 seconds
        this.metrics = {};
        this.currentSection = 'dashboard'; // Track current section
        this.init();
    }

    init() {
        // Wait for page to load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        this.setupEventListeners();
        this.initializeCharts();
        this.startDataUpdates();
        this.setupNavigation();
        this.createSectionContainers();
        this.initializeInteractiveChart();
        this.showWelcomeMessage();
    }

    createSectionContainers() {
        // The HTML structure uses a single analysis-section for all content
        // We just need to ensure the dashboard section is active by default
        setTimeout(() => {
            // Make sure the analysis section is visible
            const analysisSection = document.querySelector('.analysis-section');
            const mainContentArea = document.querySelector('.main-content-area');
            
            if (analysisSection) {
                analysisSection.style.display = 'block';
                analysisSection.style.opacity = '1';
            }
            
            if (mainContentArea) {
                mainContentArea.style.display = 'block';
                mainContentArea.style.opacity = '1';
            }
            
            // Initialize with dashboard section
            this.switchToSection('dashboard');
            console.log('Section containers initialized with analysis-section approach');
        }, 100);
    }

    initializeInteractiveChart() {
        // Initialize chart with default line chart
        setTimeout(() => {
            this.updateChart('line');
            
            // Ensure chart buttons are properly connected
            const chartButtons = document.querySelectorAll('.chart-btn');
            chartButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.handleChartTypeChange(e);
                });
            });
            
            console.log('Interactive chart initialized with', chartButtons.length, 'buttons');
        }, 1000);
    }

    setupEventListeners() {
        // Navigation buttons
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

             // Chart button interactions
             const chartBtns = document.querySelectorAll('.chart-btn');
             chartBtns.forEach(btn => {
                 if (!btn.hasAttribute('data-listener')) {
                     btn.addEventListener('click', (e) => this.handleChartTypeChange(e));
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

     switchToSection(section) {
         console.log('Switching to section:', section);
         
         // Update current section
         this.currentSection = section;
         
         const analysisSection = document.querySelector('.analysis-section');
         const analysisTitle = document.querySelector('.analysis-title');
         const chartControls = document.querySelector('.chart-controls');
         const chartContainer = document.querySelector('.chart-container');
         
         if (analysisSection && analysisTitle) {
             console.log('Found analysis section, updating content for:', section);
             
             // Add a subtle animation to indicate section change
             analysisSection.style.opacity = '0.7';
             
             setTimeout(() => {
                 if (section === 'dashboard') {
                     // Show full dashboard with charts
                     
                     querySelector("#for-data").style.display = 'none';
                     querySelector("#for-dashboard").style.display = 'flex';
                     analysisTitle.textContent = 'Dashboard Analytics';
                     if (chartControls) chartControls.style.display = 'block';
                     if (chartContainer) chartContainer.style.display = 'block';
                 } else {
                     // Show only title for other sections
                     switch(section) {
                         case 'data':
                             querySelector("#for-data").style.display = 'flex';
                             querySelector("#for-dashboard").style.display = 'none';
                             break;
                         default:
                             analysisTitle.textContent = 'Dashboard Analytics';
                     }
                     // Hide chart controls and container for non-dashboard sections
                     if (chartControls) chartControls.style.display = 'none';
                     if (chartContainer) chartContainer.style.display = 'none';
                 }
                 
                 analysisSection.style.opacity = '1';
             }, 200);
             
             console.log('Section switched successfully to:', section);
         } else {
             console.log('Analysis section not found, section switching disabled');
         }
         
         // Load section-specific data
         this.loadSectionData(section);
     }

     async loadSectionData(section) {
         console.log(`Loading ${section} section with simulated data...`);
         
         switch(section) {
             case 'dashboard':
                 this.loadDashboardData();
                 this.updateChartForSection('dashboard');
                 this.showNotification('📊 Dashboard refreshed', 'success');
                 break;
            
             case 'data':
                 this.loadDataAnalyticsData();
                 this.showNotification('📈 Data analytics updated', 'info');
                 break;
             default:
                 this.loadDashboardData();
                 this.updateChartForSection('dashboard');
                 this.showNotification('📊 Dashboard refreshed', 'success');
                 break;
         }
     }

     updateChartForSection(section) {
         // Update chart data and legend based on the selected section
         let sectionData;
         
         switch(section) {
             case 'dashboard':
                 sectionData = [
                     { month: 'Jan', patients: 65, revenue: 45, satisfaction: 50 },
                     { month: 'Feb', patients: 58, revenue: 52, satisfaction: 45 },
                     { month: 'Mar', patients: 52, revenue: 58, satisfaction: 40 },
                     { month: 'Apr', patients: 45, revenue: 62, satisfaction: 35 },
                     { month: 'May', patients: 38, revenue: 68, satisfaction: 30 },
                     { month: 'Jun', patients: 45, revenue: 55, satisfaction: 25 },
                     { month: 'Jul', patients: 35, revenue: 48, satisfaction: 20 }
                 ];
                 this.updateLegendForSection(['Patient Count', 'Revenue Data', 'Satisfaction']);
                 break;
             case 'alerts':
                 sectionData = [
                     { month: 'Jan', critical: 3, warning: 7, info: 12 },
                     { month: 'Feb', critical: 5, warning: 9, info: 15 },
                     { month: 'Mar', critical: 2, warning: 6, info: 10 },
                     { month: 'Apr', critical: 4, warning: 8, info: 14 },
                     { month: 'May', critical: 1, warning: 4, info: 8 },
                     { month: 'Jun', critical: 3, warning: 7, info: 11 },
                     { month: 'Jul', critical: 2, warning: 5, info: 9 }
                 ];
                 this.updateLegendForSection(['Critical Alerts', 'Warning Alerts', 'Info Alerts']);
                 break;
             case 'resources':
                 sectionData = [
                     { month: 'Jan', beds: 85, staff: 67, equipment: 92 },
                     { month: 'Feb', beds: 78, staff: 72, equipment: 89 },
                     { month: 'Mar', beds: 82, staff: 65, equipment: 94 },
                     { month: 'Apr', beds: 88, staff: 70, equipment: 87 },
                     { month: 'May', beds: 75, staff: 68, equipment: 91 },
                     { month: 'Jun', beds: 80, staff: 73, equipment: 93 },
                     { month: 'Jul', beds: 83, staff: 69, equipment: 88 }
                 ];
                 this.updateLegendForSection(['Bed Occupancy %', 'Staff Availability %', 'Equipment Status %']);
                 break;
             case 'data':
                 sectionData = [
                     { month: 'Jan', admissions: 120, avgStay: 4.2, revenue: 280 },
                     { month: 'Feb', admissions: 135, avgStay: 3.8, revenue: 310 },
                     { month: 'Mar', admissions: 115, avgStay: 4.5, revenue: 265 },
                     { month: 'Apr', admissions: 142, avgStay: 3.9, revenue: 325 },
                     { month: 'May', admissions: 128, avgStay: 4.1, revenue: 295 },
                     { month: 'Jun', admissions: 138, avgStay: 3.7, revenue: 315 },
                     { month: 'Jul', admissions: 125, avgStay: 4.3, revenue: 285 }
                 ];
                 this.updateLegendForSection(['Admissions', 'Avg Stay (days)', 'Revenue ($K)']);
                 break;
             default:
                 return;
         }
         
         // Update the chart with new data
         if (this.setChartData) {
             this.setChartData(sectionData);
         }
     }

     updateLegendForSection(labels) {
         const legendContainer = document.querySelector('.chart-legend');
         if (!legendContainer || !labels) return;

         const colors = ['#3b82f6', '#22d3ee', '#10b981'];
         
         const legendHTML = labels.map((label, i) => `
             <span class="legend-item">
                 <span class="legend-color" style="background: ${colors[i % colors.length]};"></span>
                 ${label}
             </span>
         `).join('');
         
         legendContainer.innerHTML = legendHTML;
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
         this.refreshAllMetrics();
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
         
         // Also animate metrics container if available
         const metricsContainer = document.querySelector('.metrics-container');
         if (metricsContainer) {
             metricsContainer.style.opacity = '0.7';
             setTimeout(() => {
                 metricsContainer.style.opacity = '1';
             }, 500);
         }
     }

    initializeCharts() {
        this.initICUOccupancyChart();
        this.initEmergencyLoadChart();
        this.initStaffAvailability();
        this.initToolUsageChart();
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
                    circle.style.strokeDashoffset = offset + 'px';
                    text.textContent = newValue + '%';
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
                    doctorsProgress.style.width = doctorValue + '%';
                    nursesProgress.style.width = nurseValue + '%';
                    
                    // Update percentage displays
                    const doctorPercentage = document.querySelector('.staff-item:first-child .staff-percentage');
                    const nursePercentage = document.querySelector('.staff-item:last-child .staff-percentage');
                    if (doctorPercentage) doctorPercentage.textContent = doctorValue + '%';
                    if (nursePercentage) nursePercentage.textContent = nurseValue + '%';
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
                            bar.style.height = newValues[index] + '%';
                        }
                    });
                }
            };
        }
    }

    startDataUpdates() {
        this.updateDashboardData();
        setInterval(() => {
            this.updateDashboardData();
        }, this.updateInterval);
    }

    updateDashboardData() {
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
         
         const originalText = button.textContent;
         button.style.opacity = '0.7';
         button.textContent = 'Loading...';
         
         setTimeout(() => {
             button.style.opacity = '1';
             button.textContent = originalText;
             
             if (action.includes('status')) {
                 this.refreshAllMetrics();
             }
         }, 1000);
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

     handleChartTypeChange(event) {
         console.log('handleChartTypeChange called', event);
         const clickedBtn = event.target;
         const chartType = clickedBtn.getAttribute('data-chart') || clickedBtn.textContent.toLowerCase();
         
         console.log('Chart type detected:', chartType, 'from button:', clickedBtn.textContent);
         
         // Update active state
         document.querySelectorAll('.chart-btn').forEach(btn => {
             btn.classList.remove('active');
         });
         clickedBtn.classList.add('active');
         
         // Show notification
         this.showNotification(`📊 Switched to ${clickedBtn.textContent} view`, 'info');
         
         // Update chart content
         this.updateChart(chartType);
         
         console.log(`Chart type changed to: ${chartType}`);
     }

     updateChart(chartType, data = null) {
         console.log('updateChart called with type:', chartType);
         const chartContainer = document.querySelector('.line-chart');
         if (!chartContainer) {
             console.error('Chart container not found!');
             return;
         }

         console.log('Chart container found, updating to', chartType);

         // Use provided data or get current data
         const chartData = data || this.getChartData();
         console.log('Using chart data:', chartData);

         // Add transition effect
         chartContainer.style.opacity = '0.3';
         chartContainer.style.transform = 'scale(0.95)';
         
         setTimeout(() => {
             // Generate chart based on type with dynamic data
             switch(chartType) {
                 case 'line':
                     console.log('Generating dynamic line chart');
                     chartContainer.innerHTML = this.generateDynamicLineChart(chartData);
                     break;
                 case 'bar':
                     console.log('Generating dynamic bar chart');
                     chartContainer.innerHTML = this.generateDynamicBarChart(chartData);
                     break;
                 case 'pie':
                     console.log('Generating dynamic pie chart');
                     chartContainer.innerHTML = this.generateDynamicPieChart(chartData);
                     break;
                 case 'scatter':
                     console.log('Generating dynamic scatter chart');
                     chartContainer.innerHTML = this.generateDynamicScatterChart(chartData);
                     break;
                 default:
                     console.log('Default: generating dynamic line chart');
                     chartContainer.innerHTML = this.generateDynamicLineChart(chartData);
             }
             
             // Update legend dynamically
             this.updateDynamicLegend(chartData, chartType);
             
             // Restore chart appearance
             chartContainer.style.opacity = '1';
             chartContainer.style.transform = 'scale(1)';
             console.log('Chart updated successfully to', chartType);
         }, 150);
     }

     getCurrentChartData() {
         // Default sample data that can be easily replaced
         return [
             { month: 'Jan', patients: 65, revenue: 45, paties: 50 },
             { month: 'Feb', patients: 58, revenue: 52, paties: 45 },
             { month: 'Mar', patients: 52, revenue: 58, paties: 40 },
             { month: 'Apr', patients: 45, revenue: 62, paties: 35 },
             { month: 'May', patients: 38, revenue: 68, paties: 30 },
             { month: 'Jun', patients: 45, revenue: 55, paties: 25 },
             { month: 'Jul', patients: 35, revenue: 48, paties: 20 }
         ];
     }

     analyzeDataStructure(data) {
         if (!data || data.length === 0) return { xField: null, yFields: [], colors: [] };
         
         const firstItem = data[0];
         const fields = Object.keys(firstItem);
         
         // Detect x-axis field (typically string/category field)
         const xField = fields.find(field => 
             typeof firstItem[field] === 'string' || 
             field.toLowerCase().includes('time') ||
             field.toLowerCase().includes('date') ||
             field.toLowerCase().includes('month') ||
             field.toLowerCase().includes('category') ||
             field.toLowerCase().includes('label')
         ) || fields[0];
         
         // Detect y-axis fields (numeric fields excluding x-axis)
         const yFields = fields.filter(field => 
             field !== xField && 
             typeof firstItem[field] === 'number'
         );
         
         // Generate colors dynamically
         const colorPalette = [
             '#3b82f6', '#22d3ee', '#10b981', '#f59e0b', 
             '#ef4444', '#8b5cf6', '#06b6d4', '#84cc16', 
             '#f97316', '#ec4899', '#6366f1', '#14b8a6'
         ];
         
         const colors = yFields.map((field, index) => 
             colorPalette[index % colorPalette.length]
         );
         
         return { xField, yFields, colors };
     }

     generateDynamicLineChart(data) {
         const { xField, yFields, colors } = this.analyzeDataStructure(data);
         console.log('Line chart structure:', { xField, yFields, colors });
         
         if (!xField || yFields.length === 0) {
             return '<div style="padding: 20px; text-align: center; color: #64748b;">No valid data structure for line chart</div>';
         }

         // Calculate scales
         const allValues = data.flatMap(d => yFields.map(field => d[field] || 0));
         const minValue = Math.min(...allValues);
         const maxValue = Math.max(...allValues);
         const valueRange = maxValue - minValue || 1;
         
         // Scale functions
         const scaleY = (value) => 250 - ((value - minValue) / valueRange) * 180;
         const scaleX = (index) => 80 + index * (440 / (data.length - 1));

         return `
             <svg width="100%" height="400" viewBox="0 0 600 320">
                 <!-- Grid lines -->
                 <defs>
                     <pattern id="grid" width="50" height="25" patternUnits="userSpaceOnUse">
                         <path d="M 50 0 L 0 0 0 25" fill="none" stroke="#f1f5f9" stroke-width="1"/>
                     </pattern>
                 </defs>
                 <rect width="100%" height="100%" fill="url(#grid)" />
                 
                 <!-- Y-axis labels -->
                 ${Array.from({length: 6}, (_, i) => {
                     const value = Math.round(maxValue - (i * valueRange / 5));
                     const y = 50 + i * 40;
                     return `<text x="30" y="${y}" fill="#64748b" font-size="12" text-anchor="end">${value}</text>`;
                 }).join('')}
                 
                 <!-- X-axis labels -->
                 ${data.map((d, i) => `<text x="${scaleX(i)}" y="280" fill="#64748b" font-size="12" text-anchor="middle">${d[xField]}</text>`).join('')}
                 
                 <!-- Dynamic lines for each field -->
                 ${yFields.map((field, fieldIndex) => {
                     const lineColor = colors[fieldIndex];
                     const pathData = data.map((d, i) => `${scaleX(i)} ${scaleY(d[field] || 0)}`).join(' L ');
                     return `
                         <!-- ${field} line -->
                         <path d="M ${pathData}" 
                               stroke="${lineColor}" stroke-width="3" fill="none" stroke-linecap="round"/>
                         
                         <!-- Data points for ${field} -->
                         ${data.map((d, i) => `<circle cx="${scaleX(i)}" cy="${scaleY(d[field] || 0)}" r="4" fill="${lineColor}"/>`).join('')}
                     `;
                 }).join('')}
             </svg>
         `;
     }

     // Keep old function for backwards compatibility
     generateLineChart() {
         return this.generateDynamicLineChart(this.getCurrentChartData());
     }

     generateDynamicBarChart(data) {
         const { xField, yFields, colors } = this.analyzeDataStructure(data);
         console.log('Bar chart structure:', { xField, yFields, colors });
         
         if (!xField || yFields.length === 0) {
             return '<div style="padding: 20px; text-align: center; color: #64748b;">No valid data structure for bar chart</div>';
         }

         // Calculate scales
         const allValues = data.flatMap(d => yFields.map(field => d[field] || 0));
         const minValue = Math.max(0, Math.min(...allValues)); // Start from 0 for bars
         const maxValue = Math.max(...allValues);
         const valueRange = maxValue - minValue || 1;
         
         // Scale functions
         const scaleY = (value) => 250 - ((value - minValue) / valueRange) * 180;
         const scaleHeight = (value) => ((value - minValue) / valueRange) * 180;
         const categoryWidth = 440 / data.length;
         const barWidth = Math.min(15, (categoryWidth - 10) / yFields.length);

         return `
             <svg width="100%" height="400" viewBox="0 0 600 320">
                 <!-- Grid lines -->
                 <defs>
                     <pattern id="grid" width="50" height="25" patternUnits="userSpaceOnUse">
                         <path d="M 50 0 L 0 0 0 25" fill="none" stroke="#f1f5f9" stroke-width="1"/>
                     </pattern>
                 </defs>
                 <rect width="100%" height="100%" fill="url(#grid)" />
                 
                 <!-- Y-axis labels -->
                 ${Array.from({length: 6}, (_, i) => {
                     const value = Math.round(maxValue - (i * valueRange / 5));
                     const y = 50 + i * 40;
                     return `<text x="30" y="${y}" fill="#64748b" font-size="12" text-anchor="end">${value}</text>`;
                 }).join('')}
                 
                 <!-- X-axis labels -->
                 ${data.map((d, i) => {
                     const centerX = 80 + i * categoryWidth + categoryWidth / 2;
                     return `<text x="${centerX}" y="280" fill="#64748b" font-size="12" text-anchor="middle">${d[xField]}</text>`;
                 }).join('')}
                 
                 <!-- Dynamic bars for each field -->
                 ${data.map((d, dataIndex) => {
                     const baseX = 80 + dataIndex * categoryWidth;
                     const startX = baseX + (categoryWidth - (yFields.length * barWidth + (yFields.length - 1) * 2)) / 2;
                     
                     return yFields.map((field, fieldIndex) => {
                         const barColor = colors[fieldIndex];
                         const value = d[field] || 0;
                         const barHeight = scaleHeight(value);
                         const barY = scaleY(value);
                         const barX = startX + fieldIndex * (barWidth + 2);
                         
                         return `
                             <!-- ${field} bar for ${d[xField]} -->
                             <rect x="${barX}" y="${barY}" width="${barWidth}" height="${barHeight}" 
                                   fill="${barColor}" rx="2" opacity="0.9"/>
                             <text x="${barX + barWidth/2}" y="${barY - 5}" fill="#64748b" 
                                   font-size="10" text-anchor="middle">${value}</text>
                         `;
                     }).join('');
                 }).join('')}
             </svg>
         `;
     }

     // Keep old function for backwards compatibility
     generateBarChart() {
         return this.generateDynamicBarChart(this.getCurrentChartData());
     }

     generateDynamicPieChart(data) {
         console.log('Generating dynamic pie chart with data:', data);
         
         if (!data || data.length === 0) {
             return '<div style="padding: 20px; text-align: center; color: #64748b;">No data available for pie chart</div>';
         }

         // For pie charts, we can use different approaches:
         // 1. If data has explicit value and label fields
         // 2. If data needs to be aggregated from multiple series
         // 3. Use the first numeric field for values
         
         const { xField, yFields, colors } = this.analyzeDataStructure(data);
         
         let pieData = [];
         
         // Check if we have explicit value/label structure
         if (data[0].hasOwnProperty('value') && data[0].hasOwnProperty('label')) {
             pieData = data.map((d, i) => ({
                 label: d.label,
                 value: d.value,
                 color: d.color || colors[i % colors.length]
             }));
         } else if (yFields.length === 1) {
             // Single numeric field - use each data point as a slice
             pieData = data.map((d, i) => ({
                 label: d[xField] || `Item ${i + 1}`,
                 value: d[yFields[0]] || 0,
                 color: colors[i % colors.length]
             }));
         } else if (yFields.length > 1) {
             // Multiple numeric fields - use field names as labels, sum values
             pieData = yFields.map((field, i) => ({
                 label: field.charAt(0).toUpperCase() + field.slice(1),
                 value: data.reduce((sum, d) => sum + (d[field] || 0), 0),
                 color: colors[i % colors.length]
             }));
         } else {
             return '<div style="padding: 20px; text-align: center; color: #64748b;">No valid numeric data for pie chart</div>';
         }

         const total = pieData.reduce((sum, d) => sum + d.value, 0);
         if (total === 0) {
             return '<div style="padding: 20px; text-align: center; color: #64748b;">All values are zero</div>';
         }

         let currentAngle = 0;
         const radius = 80;
         const centerX = 300;
         const centerY = 130;

         const slices = pieData.map(d => {
             const startAngle = currentAngle;
             const endAngle = currentAngle + (d.value / total) * 2 * Math.PI;
             currentAngle = endAngle;

             const x1 = centerX + radius * Math.cos(startAngle);
             const y1 = centerY + radius * Math.sin(startAngle);
             const x2 = centerX + radius * Math.cos(endAngle);
             const y2 = centerY + radius * Math.sin(endAngle);

             const largeArcFlag = endAngle - startAngle <= Math.PI ? "0" : "1";
             const percentage = Math.round((d.value / total) * 100);

             return {
                 ...d,
                 percentage,
                 path: `M ${centerX} ${centerY} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2} Z`,
                 labelX: centerX + (radius * 0.7) * Math.cos((startAngle + endAngle) / 2),
                 labelY: centerY + (radius * 0.7) * Math.sin((startAngle + endAngle) / 2)
             };
         });

         return `
             <svg width="100%" height="400" viewBox="0 0 600 300">
                 <!-- Pie slices -->
                 ${slices.map(slice => `
                     <path d="${slice.path}" fill="${slice.color}" stroke="white" stroke-width="2"/>
                     ${slice.percentage > 5 ? `<text x="${slice.labelX}" y="${slice.labelY}" fill="white" font-size="12" text-anchor="middle" font-weight="600">${slice.percentage}%</text>` : ''}
                 `).join('')}
                 
                 <!-- Legend -->
                 ${pieData.map((d, i) => `
                     <rect x="450" y="${50 + i * 20}" width="12" height="12" fill="${d.color}" rx="2"/>
                     <text x="470" y="${60 + i * 20}" fill="#64748b" font-size="11">${d.label} (${Math.round((d.value / total) * 100)}%)</text>
                 `).join('')}
                 
                 <!-- Title -->
                 <text x="300" y="30" fill="#1e293b" font-size="16" text-anchor="middle" font-weight="600">Data Distribution</text>
             </svg>
         `;
     }

     // Keep old function for backwards compatibility
     generatePieChart() {
         // Convert current data format to pie chart format for demo
         const currentData = this.getCurrentChartData();
         const { yFields, colors } = this.analyzeDataStructure(currentData);
         
         // Use field totals for pie chart
         const pieData = yFields.map((field, i) => ({
             label: field.charAt(0).toUpperCase() + field.slice(1),
             value: currentData.reduce((sum, d) => sum + (d[field] || 0), 0),
             color: colors[i % colors.length]
         }));
         
         return this.generateDynamicPieChart(pieData);
     }

     generateDynamicScatterChart(data) {
         console.log('Generating dynamic scatter chart with data:', data);
         
         if (!data || data.length === 0) {
             return '<div style="padding: 20px; text-align: center; color: #64748b;">No data available for scatter chart</div>';
         }

         const { xField, yFields, colors } = this.analyzeDataStructure(data);
         
         if (yFields.length < 2) {
             return '<div style="padding: 20px; text-align: center; color: #64748b;">Scatter chart requires at least 2 numeric fields</div>';
         }

         // Use first two numeric fields for X and Y axes
         const xAxisField = yFields[0];
         const yAxisField = yFields[1];
         const sizeField = yFields[2] || null; // Optional third field for bubble size
         const labelField = xField; // Use the category field for labels
         
         // Calculate scales
         const xValues = data.map(d => d[xAxisField] || 0);
         const yValues = data.map(d => d[yAxisField] || 0);
         const sizeValues = sizeField ? data.map(d => d[sizeField] || 0) : [];
         
         const xMin = Math.min(...xValues);
         const xMax = Math.max(...xValues);
         const yMin = Math.min(...yValues);
         const yMax = Math.max(...yValues);
         const sizeMin = sizeValues.length ? Math.min(...sizeValues) : 5;
         const sizeMax = sizeValues.length ? Math.max(...sizeValues) : 10;
         
         const xRange = xMax - xMin || 1;
         const yRange = yMax - yMin || 1;
         const sizeRange = sizeMax - sizeMin || 1;
         
         // Scale functions
         const scaleX = (value) => 50 + ((value - xMin) / xRange) * 500;
         const scaleY = (value) => 250 - ((value - yMin) / yRange) * 200;
         const scaleSize = (value) => sizeField ? 
             5 + ((value - sizeMin) / sizeRange) * 10 : 
             8; // Default size if no size field

         return `
             <svg width="100%" height="400" viewBox="0 0 600 300">
                 <!-- Grid lines -->
                 <defs>
                     <pattern id="grid" width="50" height="25" patternUnits="userSpaceOnUse">
                         <path d="M 50 0 L 0 0 0 25" fill="none" stroke="#f1f5f9" stroke-width="1"/>
                     </pattern>
                 </defs>
                 <rect width="100%" height="100%" fill="url(#grid)" />
                 
                 <!-- X-axis -->
                 <line x1="50" y1="250" x2="550" y2="250" stroke="#e2e8f0" stroke-width="2"/>
                 <text x="300" y="290" fill="#64748b" font-size="12" text-anchor="middle">${xAxisField.charAt(0).toUpperCase() + xAxisField.slice(1)}</text>
                 
                 <!-- Y-axis -->
                 <line x1="50" y1="50" x2="50" y2="250" stroke="#e2e8f0" stroke-width="2"/>
                 <text x="25" y="150" fill="#64748b" font-size="12" text-anchor="middle" transform="rotate(-90 25 150)">${yAxisField.charAt(0).toUpperCase() + yAxisField.slice(1)}</text>
                 
                 <!-- X-axis labels -->
                 ${Array.from({length: 6}, (_, i) => {
                     const value = Math.round(xMin + (i * xRange / 5));
                     const x = 50 + i * 100;
                     return `<text x="${x}" y="265" fill="#64748b" font-size="10" text-anchor="middle">${value}</text>`;
                 }).join('')}
                 
                 <!-- Y-axis labels -->
                 ${Array.from({length: 6}, (_, i) => {
                     const value = Math.round(yMax - (i * yRange / 5));
                     const y = 50 + i * 40;
                     return `<text x="35" y="${y}" fill="#64748b" font-size="10" text-anchor="end">${value}</text>`;
                 }).join('')}
                 
                 <!-- Scatter points -->
                 ${data.map((d, i) => {
                     const x = scaleX(d[xAxisField] || 0);
                     const y = scaleY(d[yAxisField] || 0);
                     const size = scaleSize(sizeField ? (d[sizeField] || 0) : 8);
                     const color = colors[i % colors.length];
                     const label = d[labelField] || `Point ${i + 1}`;
                     
                     return `
                         <circle cx="${x}" cy="${y}" r="${size}" 
                                 fill="${color}" opacity="0.7" 
                                 stroke="${color}" stroke-width="2"/>
                         <text x="${x}" y="${y - size - 5}" 
                               fill="#64748b" font-size="10" text-anchor="middle">${label}</text>
                     `;
                 }).join('')}
                 
                 <!-- Title -->
                 <text x="300" y="30" fill="#1e293b" font-size="16" text-anchor="middle" font-weight="600">${yAxisField.charAt(0).toUpperCase() + yAxisField.slice(1)} vs ${xAxisField.charAt(0).toUpperCase() + xAxisField.slice(1)}</text>
             </svg>
         `;
     }

     // Keep old function for backwards compatibility
     generateScatterChart() {
         return this.generateDynamicScatterChart(this.getCurrentChartData());
     }

             updateDynamicLegend(data, chartType) {
         const legendContainer = document.querySelector('.chart-legend');
         if (!legendContainer) return;

         const { xField, yFields, colors } = this.analyzeDataStructure(data);
         
         let legendHTML = '';
         
         if (chartType === 'pie') {
             // For pie charts, show different legend format
             if (data[0]?.hasOwnProperty('value') && data[0]?.hasOwnProperty('label')) {
                 legendHTML = data.map((d, i) => `
                     <span class="legend-item">
                         <span class="legend-color" style="background: ${d.color || colors[i % colors.length]};"></span>
                         ${d.label}
                     </span>
                 `).join('');
             } else {
                 legendHTML = yFields.map((field, i) => `
                     <span class="legend-item">
                         <span class="legend-color" style="background: ${colors[i]};"></span>
                         ${field.charAt(0).toUpperCase() + field.slice(1)}
                     </span>
                 `).join('');
             }
         } else if (chartType === 'scatter') {
             // For scatter charts, show the axes being compared
             if (yFields.length >= 2) {
                 legendHTML = `
                     <span class="legend-item">
                         <span class="legend-color" style="background: ${colors[0]};"></span>
                         X: ${yFields[0].charAt(0).toUpperCase() + yFields[0].slice(1)}
                     </span>
                     <span class="legend-item">
                         <span class="legend-color" style="background: ${colors[1]};"></span>
                         Y: ${yFields[1].charAt(0).toUpperCase() + yFields[1].slice(1)}
                     </span>
                 `;
             }
         } else {
             // For line and bar charts, show all numeric fields
             legendHTML = yFields.map((field, i) => `
                 <span class="legend-item">
                     <span class="legend-color" style="background: ${colors[i]};"></span>
                     ${field.charAt(0).toUpperCase() + field.slice(1)}
                 </span>
             `).join('');
         }
         
         legendContainer.innerHTML = legendHTML;
     }

     refreshAllMetrics() {
        this.simulateDataUpdate();
        this.showNotification('Dashboard updated successfully', 'success');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = 'dashboard-notification';
        notification.textContent = message;
        
        if (type === 'success') {
            notification.style.background = '#10b981';
        } else if (type === 'error') {
            notification.style.background = '#ef4444';
        } else {
            notification.style.background = '#3b82f6';
        }
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    showWelcomeMessage() {
        setTimeout(() => {
            this.showNotification('Interactive Dashboard Loaded! 🎉', 'success');
            
            // Final fallback to ensure chart interactivity
            this.ensureChartInteractivity();
        }, 1000);
    }

    ensureChartInteractivity() {
        console.log('Ensuring chart interactivity...');
        
        // Force initialize chart
        const chartContainer = document.querySelector('.line-chart');
        if (chartContainer && !chartContainer.hasAttribute('data-initialized')) {
            console.log('Force initializing chart...');
            this.updateChart('line');
            chartContainer.setAttribute('data-initialized', 'true');
        }
        
        // Ensure all chart buttons have click handlers
        const chartBtns = document.querySelectorAll('.chart-btn');
        console.log('Found chart buttons:', chartBtns.length);
        
        chartBtns.forEach((btn, index) => {
            if (!btn.hasAttribute('data-chart-listener')) {
                console.log('Adding listener to button', index, btn.textContent);
                btn.addEventListener('click', (e) => {
                    console.log('Chart button clicked:', e.target.textContent);
                    this.handleChartTypeChange(e);
                });
                btn.setAttribute('data-chart-listener', 'true');
            }
        });
    }

    // Method to update chart data externally
    setChartData(newData) {
        console.log('Setting new chart data:', newData);
        this.chartData = newData;
        
        // Re-render current chart with new data
        const activeBtn = document.querySelector('.chart-btn.active');
        if (activeBtn) {
            const chartType = activeBtn.getAttribute('data-chart') || 'line';
            this.updateChart(chartType, newData);
        }
    }

    // Get current chart data (with fallback)
    getChartData() {
        return this.chartData || this.getCurrentChartData();
    }

    loadDashboardData() {
        console.log('Loading dashboard data...');
        this.simulateDataUpdate();
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

    updateEmergencyLoad(data) {
        if (this.metrics.emergencyLoad) {
            this.metrics.emergencyLoad.data = data;
            this.metrics.emergencyLoad.animate(data);
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
}

// Initialize dashboard
window.hospitalDashboard = new HospitalDashboard();

// Global function to update chart data
window.updateChartData = function(newData) {
    if (window.hospitalDashboard) {
        window.hospitalDashboard.setChartData(newData);
        console.log('Chart data updated globally');
    }
};

// Additional immediate initialization for chart interactivity
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, setting up chart interactivity immediately...');
    
    // Wait a moment for Gradio to finish rendering
    setTimeout(() => {
        // Find chart buttons and add click handlers directly
        const chartButtons = document.querySelectorAll('.chart-btn');
        console.log('Direct setup: Found', chartButtons.length, 'chart buttons');
        
        chartButtons.forEach((btn, index) => {
            console.log('Setting up button', index, ':', btn.textContent);
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const chartType = this.getAttribute('data-chart') || this.textContent.toLowerCase();
                console.log('Direct click handler - Chart type:', chartType);
                
                // Update active state
                chartButtons.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                // Update chart
                if (window.hospitalDashboard) {
                    window.hospitalDashboard.updateChart(chartType);
                    window.hospitalDashboard.showNotification(`📊 Switched to ${this.textContent} view`, 'info');
                }
            });
        });
        
        // Initialize with line chart
        if (window.hospitalDashboard) {
            console.log('Direct initialization with line chart');
            window.hospitalDashboard.updateChart('line');
        }
    }, 2000);
});