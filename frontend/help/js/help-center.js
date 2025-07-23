// Help Center JavaScript
class HelpCenter {
    constructor() {
        this.searchInput = document.getElementById('search-input');
        this.searchResults = document.getElementById('search-results');
        this.faqItems = document.querySelectorAll('.faq-item');
        
        // Search data for Fuse.js
        this.searchData = [
            {
                title: "How to Upload Your First Video",
                content: "Learn how to record and upload your basketball shots for analysis. Includes camera positioning, file formats, and upload process.",
                category: "Getting Started",
                url: "#getting-started",
                keywords: ["upload", "video", "first", "record", "shot", "camera", "file", "format"]
            },
            {
                title: "Creating Your Account",
                content: "Sign up for Basketball Analysis with email, Google, GitHub, or Microsoft. Free plan includes 1 video per day.",
                category: "Getting Started", 
                url: "#getting-started",
                keywords: ["account", "signup", "register", "google", "github", "microsoft", "free", "plan"]
            },
            {
                title: "Perfect Camera Positioning",
                content: "Proper camera setup for accurate analysis. Side view, chest height, 10-15 feet distance, stable tripod.",
                category: "Video Recording",
                url: "#video-recording",
                keywords: ["camera", "position", "setup", "side", "view", "distance", "tripod", "angle"]
            },
            {
                title: "Lighting and Environment", 
                content: "Optimal lighting conditions and background setup for best analysis results.",
                category: "Video Recording",
                url: "#video-recording", 
                keywords: ["lighting", "environment", "background", "indoor", "outdoor", "setup"]
            },
            {
                title: "Biomechanical Metrics Explained",
                content: "Understanding elbow angle, knee angle, release angle, and movement phases in your analysis.",
                category: "Understanding Analysis",
                url: "#understanding-analysis",
                keywords: ["biomechanical", "metrics", "elbow", "knee", "release", "angle", "phases", "analysis"]
            },
            {
                title: "Reading Feedback Reports",
                content: "How to interpret feedback categories, severity levels, and recommendations for improvement.",
                category: "Understanding Analysis", 
                url: "#understanding-analysis",
                keywords: ["feedback", "reports", "categories", "severity", "recommendations", "improvement"]
            },
            {
                title: "Analysis Processing Time",
                content: "Most analyses complete within 2-5 minutes. Email notification sent when ready.",
                category: "FAQ",
                url: "#faq",
                keywords: ["processing", "time", "analysis", "complete", "notification", "email", "ready"]
            },
            {
                title: "Supported Video Formats",
                content: "MP4, MOV, AVI, WebM formats supported. 100MB max file size. 1080p 30fps recommended.",
                category: "FAQ",
                url: "#faq", 
                keywords: ["video", "formats", "mp4", "mov", "avi", "webm", "file", "size", "resolution"]
            },
            {
                title: "Multiple Shots Analysis",
                content: "One shot per video for maximum accuracy. Pro users can batch upload multiple videos.",
                category: "FAQ",
                url: "#faq",
                keywords: ["multiple", "shots", "batch", "upload", "pro", "accuracy", "videos"]
            },
            {
                title: "Analysis Accuracy",
                content: "95%+ accuracy with proper setup. Trained on thousands of shots, validated by coaches.",
                category: "FAQ", 
                url: "#faq",
                keywords: ["accuracy", "setup", "trained", "shots", "coaches", "validation"]
            },
            {
                title: "Subscription Cancellation",
                content: "Cancel subscription anytime through account settings. Access retained until billing period ends.",
                category: "FAQ",
                url: "#faq",
                keywords: ["subscription", "cancel", "anytime", "account", "settings", "billing", "period"]
            }
        ];
        
        this.init();
    }
    
    init() {
        this.setupSearch();
        this.setupFAQ();
        this.setupScrollEffects();
        this.setupAnalytics();
    }
    
    setupSearch() {
        if (!this.searchInput || !this.searchResults) return;
        
        // Initialize Fuse.js for fuzzy search
        this.fuse = new Fuse(this.searchData, {
            keys: ['title', 'content', 'keywords'],
            threshold: 0.3,
            includeScore: true,
            includeMatches: true
        });
        
        // Search input event listeners
        this.searchInput.addEventListener('input', this.debounce(this.handleSearch.bind(this), 300));
        this.searchInput.addEventListener('focus', this.handleSearchFocus.bind(this));
        this.searchInput.addEventListener('blur', this.handleSearchBlur.bind(this));
        
        // Close search results when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                this.hideSearchResults();
            }
        });
        
        // Keyboard navigation for search results
        this.searchInput.addEventListener('keydown', this.handleSearchKeydown.bind(this));
    }
    
    handleSearch(e) {
        const query = e.target.value.trim();
        
        if (query.length < 2) {
            this.hideSearchResults();
            return;
        }
        
        const results = this.fuse.search(query);
        this.displaySearchResults(results.slice(0, 6)); // Show top 6 results
        
        // Track search analytics
        this.trackEvent('search', 'query', query);
    }
    
    displaySearchResults(results) {
        if (results.length === 0) {
            this.searchResults.innerHTML = `
                <div class="search-result">
                    <h4>No results found</h4>
                    <p>Try different keywords or browse our help categories above.</p>
                </div>
            `;
        } else {
            this.searchResults.innerHTML = results.map(result => {
                const item = result.item;
                return `
                    <div class="search-result" data-url="${item.url}">
                        <h4>${this.highlightMatches(item.title, result.matches)}</h4>
                        <p>${this.truncateText(item.content, 120)}</p>
                        <span class="search-category">${item.category}</span>
                    </div>
                `;
            }).join('');
            
            // Add click handlers to search results
            this.searchResults.querySelectorAll('.search-result[data-url]').forEach(result => {
                result.addEventListener('click', (e) => {
                    const url = e.currentTarget.dataset.url;
                    this.navigateToSection(url);
                    this.hideSearchResults();
                    this.searchInput.blur();
                });
            });
        }
        
        this.showSearchResults();
    }
    
    highlightMatches(text, matches) {
        if (!matches || matches.length === 0) return text;
        
        let highlightedText = text;
        matches.forEach(match => {
            if (match.key === 'title') {
                match.indices.forEach(([start, end]) => {
                    const before = highlightedText.substring(0, start);
                    const highlighted = highlightedText.substring(start, end + 1);
                    const after = highlightedText.substring(end + 1);
                    highlightedText = before + `<mark>${highlighted}</mark>` + after;
                });
            }
        });
        
        return highlightedText;
    }
    
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength).trim() + '...';
    }
    
    navigateToSection(url) {
        const element = document.querySelector(url);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
            
            // Highlight the section briefly
            element.style.transition = 'background-color 0.3s ease';
            element.style.backgroundColor = 'rgba(37, 99, 235, 0.1)';
            setTimeout(() => {
                element.style.backgroundColor = '';
            }, 2000);
        }
    }
    
    showSearchResults() {
        this.searchResults.style.display = 'block';
        setTimeout(() => {
            this.searchResults.style.opacity = '1';
        }, 10);
    }
    
    hideSearchResults() {
        this.searchResults.style.opacity = '0';
        setTimeout(() => {
            this.searchResults.style.display = 'none';
        }, 200);
    }
    
    handleSearchFocus() {
        if (this.searchInput.value.trim().length >= 2) {
            this.showSearchResults();
        }
    }
    
    handleSearchBlur() {
        // Delay hiding to allow clicks on results
        setTimeout(() => {
            this.hideSearchResults();
        }, 200);
    }
    
    handleSearchKeydown(e) {
        const visibleResults = this.searchResults.querySelectorAll('.search-result[data-url]');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            this.focusNextResult(visibleResults, 1);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            this.focusNextResult(visibleResults, -1);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            const focused = this.searchResults.querySelector('.search-result.focused');
            if (focused) {
                focused.click();
            }
        }
    }
    
    focusNextResult(results, direction) {
        const current = this.searchResults.querySelector('.search-result.focused');
        let index = -1;
        
        if (current) {
            index = Array.from(results).indexOf(current);
            current.classList.remove('focused');
        }
        
        index += direction;
        
        if (index < 0) index = results.length - 1;
        if (index >= results.length) index = 0;
        
        if (results[index]) {
            results[index].classList.add('focused');
        }
    }
    
    setupFAQ() {
        this.faqItems.forEach(item => {
            const question = item.querySelector('.faq-question');
            if (question) {
                question.addEventListener('click', () => {
                    const isActive = item.classList.contains('active');
                    
                    // Close all other FAQ items
                    this.faqItems.forEach(otherItem => {
                        if (otherItem !== item) {
                            otherItem.classList.remove('active');
                        }
                    });
                    
                    // Toggle current item
                    item.classList.toggle('active', !isActive);
                    
                    // Track FAQ analytics
                    if (!isActive) {
                        const questionText = question.querySelector('span').textContent;
                        this.trackEvent('faq', 'expand', questionText);
                    }
                });
            }
        });
    }
    
    setupScrollEffects() {
        // Animate elements as they come into view
        const observerOptions = {
            root: null,
            rootMargin: '0px 0px -50px 0px',
            threshold: 0.1
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animationDelay = '0s';
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);
        
        // Observe help articles and cards
        document.querySelectorAll('.help-article, .quick-link-card, .contact-option').forEach(el => {
            observer.observe(el);
        });
        
        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                    
                    // Update URL without jumping
                    history.pushState(null, null, link.getAttribute('href'));
                }
            });
        });
    }
    
    setupAnalytics() {
        // Track page view
        this.trackEvent('help_center', 'page_view', window.location.pathname);
        
        // Track section views
        const sections = document.querySelectorAll('.help-section');
        const sectionObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && entry.intersectionRatio > 0.5) {
                    const sectionId = entry.target.id;
                    if (sectionId) {
                        this.trackEvent('help_center', 'section_view', sectionId);
                    }
                }
            });
        }, {
            threshold: 0.5
        });
        
        sections.forEach(section => {
            sectionObserver.observe(section);
        });
        
        // Track external links
        document.querySelectorAll('a[href^="http"], a[href^="mailto:"]').forEach(link => {
            link.addEventListener('click', () => {
                this.trackEvent('help_center', 'external_link', link.href);
            });
        });
        
        // Track time spent on page
        this.startTime = Date.now();
        window.addEventListener('beforeunload', () => {
            const timeSpent = Math.round((Date.now() - this.startTime) / 1000);
            this.trackEvent('help_center', 'time_spent', timeSpent);
        });
    }
    
    trackEvent(category, action, label = null, value = null) {
        // Google Analytics 4
        if (typeof gtag !== 'undefined') {
            gtag('event', action, {
                event_category: category,
                event_label: label,
                value: value
            });
        }
        
        // Custom analytics endpoint
        if (typeof window.analytics !== 'undefined') {
            window.analytics.track(action, {
                category: category,
                label: label,
                value: value,
                page: 'help_center'
            });
        }
        
        // Console logging for development
        if (process.env.NODE_ENV === 'development') {
            console.log('Analytics Event:', { category, action, label, value });
        }
    }
    
    // Utility function for debouncing
    debounce(func, wait) {
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
}

// Additional utility functions
class HelpCenterUtils {
    static copyToClipboard(text) {
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            return new Promise((resolve, reject) => {
                if (document.execCommand('copy')) {
                    textArea.remove();
                    resolve();
                } else {
                    textArea.remove();
                    reject();
                }
            });
        }
    }
    
    static showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 1000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            max-width: 300px;
            word-wrap: break-word;
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
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
    
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    static validateVideoFile(file) {
        const allowedFormats = ['video/mp4', 'video/mov', 'video/quicktime', 'video/avi', 'video/webm'];
        const maxSize = 100 * 1024 * 1024; // 100MB
        
        if (!allowedFormats.includes(file.type)) {
            return {
                valid: false,
                error: 'Please upload a valid video file (MP4, MOV, AVI, or WebM)'
            };
        }
        
        if (file.size > maxSize) {
            return {
                valid: false,
                error: `File size must be less than ${this.formatFileSize(maxSize)}`
            };
        }
        
        return { valid: true };
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
    
    // Escape to close search results
    if (e.key === 'Escape') {
        const searchResults = document.getElementById('search-results');
        if (searchResults && searchResults.style.display === 'block') {
            searchResults.style.display = 'none';
            document.getElementById('search-input').blur();
        }
    }
});

// Service Worker for offline functionality
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => {
                console.log('Help Center SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('Help Center SW registration failed: ', registrationError);
            });
    });
}

// Initialize Help Center when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new HelpCenter();
    
    // Add CSS classes for animations
    const style = document.createElement('style');
    style.textContent = `
        .animate-in {
            animation: slideInUp 0.6s ease forwards;
        }
        
        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .search-result.focused {
            background-color: var(--bg-secondary);
            border-left: 3px solid var(--primary-color);
        }
        
        .search-category {
            font-size: 0.75rem;
            color: var(--primary-color);
            font-weight: 500;
            background: rgba(37, 99, 235, 0.1);
            padding: 2px 6px;
            border-radius: 4px;
            margin-top: 4px;
            display: inline-block;
        }
        
        mark {
            background: #fef08a;
            color: #92400e;
            padding: 1px 2px;
            border-radius: 2px;
        }
    `;
    document.head.appendChild(style);
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { HelpCenter, HelpCenterUtils };
}
