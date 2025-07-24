// Brunnsbo Musikklasser Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initNavigation();
    initScrollEffects();
    initFormValidation();
    initSocialFeeds();
    initImageLazyLoading();
});

// Navigation functionality
function initNavigation() {
    const navbar = document.querySelector('.navbar');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    });
    
    // Active navigation highlighting
    navLinks.forEach(link => {
        if (link.href === window.location.href) {
            link.classList.add('active');
        }
    });
    
    // Mobile menu auto-close
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth < 992) {
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                        toggle: false
                    });
                    bsCollapse.hide();
                }
            });
        });
    }
}

// Scroll effects and animations
function initScrollEffects() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Fade in animation on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe cards and content blocks
    document.querySelectorAll('.card, .content-block, .process-step').forEach(el => {
        observer.observe(el);
    });
}

// Form validation enhancements
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
            }
            form.classList.add('was-validated');
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
        });
    });
    
    // Format inputs
    const personnummerInput = document.getElementById('student_personnummer');
    if (personnummerInput) {
        personnummerInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 8) {
                value = value.slice(0, 8) + '-' + value.slice(8, 12);
            }
            e.target.value = value;
        });
    }
    
    const postalCodeInput = document.getElementById('postal_code');
    if (postalCodeInput) {
        postalCodeInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 3) {
                value = value.slice(0, 3) + ' ' + value.slice(3, 5);
            }
            e.target.value = value;
        });
    }
}

// Social media feeds
function initSocialFeeds() {
    loadInstagramFeed();
    loadFacebookFeed();
}

function loadInstagramFeed() {
    const instagramContainer = document.getElementById('instagram-feed');
    if (!instagramContainer) return;
    
    // Simulate Instagram feed loading
    setTimeout(() => {
        instagramContainer.innerHTML = `
            <div class="text-center p-4">
                <div class="row">
                    <div class="col-6 mb-3">
                        <div class="instagram-post bg-light rounded p-3" style="aspect-ratio: 1;">
                            <div class="d-flex align-items-center mb-2">
                                <div class="bg-gold rounded-circle me-2" style="width: 30px; height: 30px;"></div>
                                <small class="fw-bold">brunnsbo_musikklasser</small>
                            </div>
                            <div class="bg-secondary rounded mb-2" style="height: 80px;"></div>
                            <small class="text-muted">Senaste inlägget från våra musikelever...</small>
                        </div>
                    </div>
                    <div class="col-6 mb-3">
                        <div class="instagram-post bg-light rounded p-3" style="aspect-ratio: 1;">
                            <div class="d-flex align-items-center mb-2">
                                <div class="bg-gold rounded-circle me-2" style="width: 30px; height: 30px;"></div>
                                <small class="fw-bold">brunnsbo_musikklasser</small>
                            </div>
                            <div class="bg-secondary rounded mb-2" style="height: 80px;"></div>
                            <small class="text-muted">Från vår senaste konsert...</small>
                        </div>
                    </div>
                </div>
                <p class="text-muted small mt-2">
                    <i class="fas fa-info-circle me-1"></i>
                    För att se vårt fullständiga Instagram-flöde, besök 
                    <a href="https://www.instagram.com/brunnsbo_musikklasser/" target="_blank" class="text-decoration-none">
                        @brunnsbo_musikklasser
                    </a>
                </p>
            </div>
        `;
    }, 1500);
}

function loadFacebookFeed() {
    const facebookContainer = document.getElementById('facebook-feed');
    if (!facebookContainer) return;
    
    // Simulate Facebook feed loading
    setTimeout(() => {
        facebookContainer.innerHTML = `
            <div class="text-center p-4">
                <div class="facebook-post bg-light rounded p-3 mb-3">
                    <div class="d-flex align-items-center mb-2">
                        <div class="bg-primary rounded-circle me-2" style="width: 30px; height: 30px;"></div>
                        <small class="fw-bold">Brunnsbo Musikklasser</small>
                    </div>
                    <div class="text-start">
                        <p class="small mb-2">Vilken fantastisk konsert vi hade igår! Tack till alla som kom och lyssnade på våra duktiga elever. 🎵</p>
                        <div class="bg-secondary rounded mb-2" style="height: 120px;"></div>
                        <small class="text-muted">För 2 dagar sedan</small>
                    </div>
                </div>
                <p class="text-muted small">
                    <i class="fas fa-info-circle me-1"></i>
                    För att se vårt fullständiga Facebook-flöde, besök vår 
                    <a href="https://www.facebook.com/BrunnsboMusikklasser/" target="_blank" class="text-decoration-none">
                        Facebook-sida
                    </a>
                </p>
            </div>
        `;
    }, 2000);
}

// Lazy loading for images
function initImageLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Utility functions
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
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
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // Don't show error messages to users in production
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        showToast('Ett JavaScript-fel uppstod. Kontrollera konsolen för mer information.', 'danger');
    }
});

// Performance monitoring
window.addEventListener('load', function() {
    if ('performance' in window) {
        const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
        console.log(`Page loaded in ${loadTime}ms`);
        
        // Report slow loading times
        if (loadTime > 3000) {
            console.warn('Page loading time is slow:', loadTime + 'ms');
        }
    }
});

// Accessibility enhancements
document.addEventListener('keydown', function(e) {
    // Skip to main content with Enter key on skip link
    if (e.target.classList.contains('skip-to-main') && e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('main-content')?.focus();
    }
    
    // Close modals with Escape key
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            modal?.hide();
        }
    }
});

// Service worker registration for PWA functionality
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed');
            });
    });
}

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initNavigation,
        initScrollEffects,
        initFormValidation,
        showToast
    };
}
