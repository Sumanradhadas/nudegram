/**
 * Celebrity Discovery Platform - Main JavaScript File
 */

// Global application state
const App = {
    searchTimeout: null,
    currentSuggestions: [],
    selectedSuggestionIndex: -1,
    
    // Initialize the application
    init() {
        this.initSearchFunctionality();
        this.initImageLazyLoading();
        this.initKeyboardNavigation();
        this.initTooltips();
        
        console.log('Celebrity Discovery Platform initialized');
    },
    
    // Initialize search functionality with autocomplete
    initSearchFunctionality() {
        const searchInput = document.getElementById('searchInput');
        const searchSuggestions = document.getElementById('searchSuggestions');
        
        if (!searchInput || !searchSuggestions) return;
        
        // Search input handler with debouncing
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            
            // Clear previous timeout
            if (this.searchTimeout) {
                clearTimeout(this.searchTimeout);
            }
            
            // Hide suggestions if query is too short
            if (query.length < 2) {
                this.hideSuggestions();
                return;
            }
            
            // Debounce search requests
            this.searchTimeout = setTimeout(() => {
                this.fetchSearchSuggestions(query);
            }, 300);
        });
        
        // Handle keyboard navigation in search
        searchInput.addEventListener('keydown', (e) => {
            this.handleSearchKeyNavigation(e);
        });
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !searchSuggestions.contains(e.target)) {
                this.hideSuggestions();
            }
        });
        
        // Focus search input when pressing '/' key
        document.addEventListener('keydown', (e) => {
            if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
                e.preventDefault();
                searchInput.focus();
            }
        });
    },
    
    // Fetch search suggestions from API
    async fetchSearchSuggestions(query) {
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const suggestions = await response.json();
            this.displaySuggestions(suggestions, query);
            
        } catch (error) {
            console.error('Error fetching search suggestions:', error);
            this.hideSuggestions();
        }
    },
    
    // Display search suggestions
    displaySuggestions(suggestions, query) {
        const searchSuggestions = document.getElementById('searchSuggestions');
        
        if (!suggestions.length) {
            this.hideSuggestions();
            return;
        }
        
        this.currentSuggestions = suggestions;
        this.selectedSuggestionIndex = -1;
        
        searchSuggestions.innerHTML = '';
        
        suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
            item.setAttribute('data-index', index);
            
            // Highlight matching text
            const highlightedName = this.highlightText(suggestion.name, query);
            
            item.innerHTML = `
                <div>
                    <div class="fw-medium">${highlightedName}</div>
                    <small class="text-muted">${suggestion.profession}</small>
                </div>
                <i class="fas fa-arrow-right text-muted"></i>
            `;
            
            // Add click handler
            item.addEventListener('click', () => {
                this.selectSuggestion(suggestion);
            });
            
            searchSuggestions.appendChild(item);
        });
        
        searchSuggestions.style.display = 'block';
    },
    
    // Hide search suggestions
    hideSuggestions() {
        const searchSuggestions = document.getElementById('searchSuggestions');
        if (searchSuggestions) {
            searchSuggestions.style.display = 'none';
            this.currentSuggestions = [];
            this.selectedSuggestionIndex = -1;
        }
    },
    
    // Handle keyboard navigation in search suggestions
    handleSearchKeyNavigation(e) {
        const searchSuggestions = document.getElementById('searchSuggestions');
        
        if (!searchSuggestions || searchSuggestions.style.display === 'none') {
            return;
        }
        
        const items = searchSuggestions.querySelectorAll('.list-group-item');
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedSuggestionIndex = Math.min(
                    this.selectedSuggestionIndex + 1,
                    items.length - 1
                );
                this.updateSuggestionHighlight(items);
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this.selectedSuggestionIndex = Math.max(
                    this.selectedSuggestionIndex - 1,
                    -1
                );
                this.updateSuggestionHighlight(items);
                break;
                
            case 'Enter':
                if (this.selectedSuggestionIndex >= 0) {
                    e.preventDefault();
                    const suggestion = this.currentSuggestions[this.selectedSuggestionIndex];
                    this.selectSuggestion(suggestion);
                }
                break;
                
            case 'Escape':
                this.hideSuggestions();
                break;
        }
    },
    
    // Update visual highlight for keyboard navigation
    updateSuggestionHighlight(items) {
        items.forEach((item, index) => {
            item.classList.toggle('active', index === this.selectedSuggestionIndex);
        });
    },
    
    // Select a suggestion and navigate to profile
    selectSuggestion(suggestion) {
        window.location.href = `/profile/${suggestion.slug}`;
    },
    
    // Highlight matching text in suggestions
    highlightText(text, query) {
        if (!query) return text;
        
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark class="bg-warning text-dark">$1</mark>');
    },
    
    // Initialize image lazy loading with intersection observer
    initImageLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        this.loadImage(img);
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            // Observe all lazy loading images
            document.querySelectorAll('img[loading="lazy"]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    },
    
    // Load image with error handling
    loadImage(img) {
        const originalSrc = img.src;
        
        img.addEventListener('error', () => {
            console.warn(`Failed to load image: ${originalSrc}`);
            img.src = this.getPlaceholderImage();
            img.alt = 'Image not available';
        });
        
        img.addEventListener('load', () => {
            img.classList.add('loaded');
        });
    },
    
    // Get placeholder image URL
    getPlaceholderImage() {
        return 'data:image/svg+xml,' + encodeURIComponent(`
            <svg xmlns="http://www.w3.org/2000/svg" width="300" height="300" viewBox="0 0 300 300">
                <rect width="300" height="300" fill="#6c757d"/>
                <text x="150" y="150" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle" dominant-baseline="middle">
                    Image Not Available
                </text>
            </svg>
        `);
    },
    
    // Initialize keyboard navigation shortcuts
    initKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Global keyboard shortcuts
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'k': // Ctrl+K or Cmd+K to focus search
                        e.preventDefault();
                        const searchInput = document.getElementById('searchInput');
                        if (searchInput) {
                            searchInput.focus();
                            searchInput.select();
                        }
                        break;
                }
            }
            
            // Escape key to clear search
            if (e.key === 'Escape') {
                const searchInput = document.getElementById('searchInput');
                if (searchInput && searchInput === document.activeElement) {
                    searchInput.blur();
                    this.hideSuggestions();
                }
            }
        });
    },
    
    // Initialize Bootstrap tooltips
    initTooltips() {
        // Initialize tooltips if Bootstrap is available
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    },
    
    // Utility function to format numbers
    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    },
    
    // Utility function to show toast notifications
    showToast(message, type = 'info') {
        // Create toast element
        const toastContainer = document.querySelector('.toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Show toast using Bootstrap
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
            
            // Remove toast element after it's hidden
            toast.addEventListener('hidden.bs.toast', () => {
                toast.remove();
            });
        } else {
            // Fallback if Bootstrap is not available
            setTimeout(() => {
                toast.remove();
            }, 5000);
        }
    },
    
    // Create toast container if it doesn't exist
    createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1100';
        document.body.appendChild(container);
        return container;
    }
};

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

// Export App for global access
window.CelebrityDiscoveryApp = App;
