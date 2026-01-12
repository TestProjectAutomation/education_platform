// Dashboard specific JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts
    initCharts();
    
    // Initialize data tables
    initDataTables();
    
    // Initialize form validations
    initFormValidations();
    
    // Initialize tooltips
    initTooltips();
});

// Chart.js initialization
function initCharts() {
    // Visitor Chart
    const visitorCtx = document.getElementById('visitorChart');
    if (visitorCtx) {
        const visitorChart = new Chart(visitorCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Visitors',
                    data: [1200, 1900, 1500, 2500, 2200, 3000],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
    
    // Revenue Chart
    const revenueCtx = document.getElementById('revenueChart');
    if (revenueCtx) {
        const revenueChart = new Chart(revenueCtx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Revenue',
                    data: [5000, 7000, 6500, 8000, 9000, 12000],
                    backgroundColor: '#10b981',
                    borderColor: '#10b981',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
    
    // Content Distribution Chart
    const contentCtx = document.getElementById('contentChart');
    if (contentCtx) {
        const contentChart = new Chart(contentCtx, {
            type: 'doughnut',
            data: {
                labels: ['Courses', 'Articles', 'Books', 'Scholarships'],
                datasets: [{
                    data: [40, 25, 20, 15],
                    backgroundColor: [
                        '#3b82f6',
                        '#10b981',
                        '#8b5cf6',
                        '#f59e0b'
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// DataTables initialization
function initDataTables() {
    const tables = document.querySelectorAll('table[data-table]');
    tables.forEach(table => {
        // Add sortable functionality
        const headers = table.querySelectorAll('th[data-sortable]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                const column = this.getAttribute('data-sortable');
                const isAscending = this.getAttribute('data-sort') === 'asc';
                
                // Update sort indicators
                headers.forEach(h => h.removeAttribute('data-sort'));
                this.setAttribute('data-sort', isAscending ? 'desc' : 'asc');
                
                // Sort table
                sortTable(table, column, isAscending);
            });
        });
    });
}

// Table sorting function
function sortTable(table, column, isAscending) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aValue = a.querySelector(`td:nth-child(${column})`).textContent.trim();
        const bValue = b.querySelector(`td:nth-child(${column})`).textContent.trim();
        
        // Try to parse as number
        const aNum = parseFloat(aValue.replace(/[^0-9.-]+/g, ''));
        const bNum = parseFloat(bValue.replace(/[^0-9.-]+/g, ''));
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        } else {
            // Compare as strings
            return isAscending 
                ? aValue.localeCompare(bValue)
                : bValue.localeCompare(aValue);
        }
    });
    
    // Clear and re-append rows
    rows.forEach(row => tbody.appendChild(row));
}

// Form validations
function initFormValidations() {
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const inputs = this.querySelectorAll('input[required], textarea[required], select[required]');
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('border-red-500');
                    
                    // Add error message
                    if (!input.nextElementSibling || !input.nextElementSibling.classList.contains('error-message')) {
                        const errorMsg = document.createElement('p');
                        errorMsg.className = 'error-message text-red-600 dark:text-red-400 text-sm mt-1';
                        errorMsg.textContent = 'This field is required';
                        input.parentNode.appendChild(errorMsg);
                    }
                } else {
                    input.classList.remove('border-red-500');
                    
                    // Remove error message
                    const errorMsg = input.parentNode.querySelector('.error-message');
                    if (errorMsg) {
                        errorMsg.remove();
                    }
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                
                // Scroll to first error
                const firstError = this.querySelector('.border-red-500');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstError.focus();
                }
            }
        });
    });
}

// Tooltips
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        const tooltipText = element.getAttribute('data-tooltip');
        
        element.addEventListener('mouseenter', function(e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'absolute z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded-lg shadow-lg';
            tooltip.textContent = tooltipText;
            tooltip.style.top = (e.clientY - 40) + 'px';
            tooltip.style.left = (e.clientX + 10) + 'px';
            tooltip.id = 'tooltip-' + Date.now();
            
            document.body.appendChild(tooltip);
            
            // Update position on mouse move
            this.addEventListener('mousemove', function(e) {
                tooltip.style.top = (e.clientY - 40) + 'px';
                tooltip.style.left = (e.clientX + 10) + 'px';
            });
        });
        
        element.addEventListener('mouseleave', function() {
            const tooltips = document.querySelectorAll('[id^="tooltip-"]');
            tooltips.forEach(t => t.remove());
        });
    });
}

// Real-time updates
function initRealTimeUpdates() {
    // Simulate real-time updates
    setInterval(() => {
        // Update visitor count
        const visitorCount = document.querySelector('[data-visitor-count]');
        if (visitorCount) {
            const currentCount = parseInt(visitorCount.textContent.replace(/,/g, ''));
            const newCount = currentCount + Math.floor(Math.random() * 10);
            visitorCount.textContent = newCount.toLocaleString();
        }
        
        // Update notification badge
        const notificationBadge = document.querySelector('[data-notification-badge]');
        if (notificationBadge) {
            const currentCount = parseInt(notificationBadge.textContent);
            if (Math.random() > 0.7) { // 30% chance of new notification
                notificationBadge.textContent = currentCount + 1;
                notificationBadge.classList.remove('hidden');
            }
        }
    }, 10000); // Update every 10 seconds
}

// Export functionality
function exportData(format) {
    const data = {
        // Your data here
    };
    
    let blob;
    let filename;
    
    if (format === 'csv') {
        const csv = convertToCSV(data);
        blob = new Blob([csv], { type: 'text/csv' });
        filename = 'export.csv';
    } else if (format === 'json') {
        const json = JSON.stringify(data, null, 2);
        blob = new Blob([json], { type: 'application/json' });
        filename = 'export.json';
    }
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Helper function to convert data to CSV
function convertToCSV(data) {
    const headers = Object.keys(data[0] || {});
    const rows = data.map(row => 
        headers.map(header => JSON.stringify(row[header] || '')).join(',')
    );
    return [headers.join(','), ...rows].join('\n');
}