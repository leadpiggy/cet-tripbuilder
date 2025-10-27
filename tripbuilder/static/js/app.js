// TripBuilder Custom JavaScript

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert:not(.alert-info)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Form validation
    const forms = document.querySelectorAll('form[method="POST"]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Initialize filter functionality if on trips list page
    if (document.getElementById('filterForm')) {
        initTripFilters();
    }
});

// Confirm delete actions
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this? This action cannot be undone.');
}

/**
 * Initialize trip search and filter functionality
 */
function initTripFilters() {
    const filterForm = document.getElementById('filterForm');
    const filterPanel = document.getElementById('filterPanel');
    const searchInput = document.getElementById('search');
    const clearBtn = document.querySelector('a[href*="trip_list"]:not([href*="?"])');
    
    // Store filter state in URL for bookmarking and sharing
    const updateURL = () => {
        const formData = new FormData(filterForm);
        const params = new URLSearchParams();
        
        for (const [key, value] of formData.entries()) {
            if (value.trim() !== '') {
                params.append(key, value);
            }
        }
        
        const newURL = params.toString() ? 
            `${window.location.pathname}?${params.toString()}` : 
            window.location.pathname;
        
        window.history.replaceState({}, '', newURL);
    };
    
    // Auto-submit on Enter key in search fields
    const textInputs = filterForm.querySelectorAll('input[type="text"], input[type="date"], input[type="number"]');
    textInputs.forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                filterForm.submit();
            }
        });
    });
    
    // Auto-submit on select/dropdown changes
    const selects = filterForm.querySelectorAll('select');
    selects.forEach(select => {
        select.addEventListener('change', function() {
            // Optional: Auto-submit on dropdown change
            // Uncomment the line below to enable
            // filterForm.submit();
        });
    });
    
    // Focus on search field with keyboard shortcut (Ctrl/Cmd + K)
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            searchInput.focus();
            searchInput.select();
        }
    });
    
    // Show filter count badge
    const activeFilters = Array.from(filterForm.elements)
        .filter(el => el.value && el.name && el.name !== 'search')
        .length;
    
    if (activeFilters > 0) {
        const filterHeader = document.querySelector('.card-header h5');
        if (filterHeader && !filterHeader.querySelector('.badge')) {
            const badge = document.createElement('span');
            badge.className = 'badge bg-primary ms-2';
            badge.textContent = `${activeFilters} active`;
            filterHeader.appendChild(badge);
        }
    }
    
    // Animate trip cards on load
    const tripCards = document.querySelectorAll('.trip-card');
    tripCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.3s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 50);
    });
    
    // Add loading state to form submission
    filterForm.addEventListener('submit', function() {
        const submitBtn = filterForm.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
        }
    });
    
    // Show helpful tooltips
    if (searchInput) {
        searchInput.setAttribute('title', 'Press Ctrl+K (Cmd+K on Mac) to focus');
    }
}

/**
 * Debounce function for optimizing event handlers
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
