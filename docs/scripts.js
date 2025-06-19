/**
 * ND-Script v2.0.0 Documentation Scripts
 * Enhanced with performance optimizations and accessibility improvements
 */

// Performance optimized scroll handling with IntersectionObserver
class NavigationManager {
    constructor() {
        this.sections = [];
        this.navLinks = [];
        this.observer = null;
        this.init();
    }

    init() {
        this.setupSections();
        this.setupIntersectionObserver();
        this.setupEventListeners();
    }

    setupSections() {
        this.sections = Array.from(document.querySelectorAll('.content-section[id]'));
        this.navLinks = Array.from(document.querySelectorAll('.nav-link'));
    }

    setupIntersectionObserver() {
        // Check if IntersectionObserver is supported
        if (!window.IntersectionObserver) {
            console.warn('IntersectionObserver not supported, falling back to scroll listener');
            this.setupScrollListener();
            return;
        }

        const options = {
            root: null,
            rootMargin: '-20% 0px -70% 0px',
            threshold: [0, 0.1, 0.5, 1.0]
        };

        this.observer = new IntersectionObserver((entries) => {
            // Find the entry with the highest intersection ratio
            let mostVisible = null;
            let highestRatio = 0;

            entries.forEach(entry => {
                if (entry.isIntersecting && entry.intersectionRatio > highestRatio) {
                    highestRatio = entry.intersectionRatio;
                    mostVisible = entry;
                }
            });

            if (mostVisible) {
                this.updateActiveNavLink(mostVisible.target.id);
                // Update URL without triggering page reload
                if (window.location.hash !== '#' + mostVisible.target.id) {
                    history.replaceState(null, null, '#' + mostVisible.target.id);
                }
            }
        }, options);

        this.sections.forEach(section => {
            this.observer.observe(section);
        });
    }

    // Fallback scroll listener for older browsers
    setupScrollListener() {
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }

            scrollTimeout = setTimeout(() => {
                const scrollPosition = window.scrollY + 150;
                let currentSection = '';

                this.sections.forEach(section => {
                    const sectionTop = section.offsetTop;
                    const sectionBottom = sectionTop + section.offsetHeight;

                    if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                        currentSection = section.getAttribute('id');
                    }
                });

                if (currentSection) {
                    this.updateActiveNavLink(currentSection);
                }
            }, 16); // ~60fps
        }, { passive: true });
    }

    updateActiveNavLink(activeId) {
        // Remove active class from all links
        this.navLinks.forEach(link => link.classList.remove('active'));
        
        // Add active class to current link
        const activeLink = document.querySelector(`[href="#${activeId}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }

    setupEventListeners() {
        // Smooth scroll for navigation links
        this.navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    this.smoothScrollTo(targetElement);
                    // Update URL without page reload
                    history.pushState(null, null, `#${targetId}`);
                }
            });
        });

        // Handle browser back/forward navigation
        window.addEventListener('popstate', () => {
            this.handlePageLoad();
        });
    }

    smoothScrollTo(element) {
        const headerOffset = 100;
        const elementPosition = element.offsetTop;
        const offsetPosition = elementPosition - headerOffset;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }

    handlePageLoad() {
        const hash = window.location.hash;
        if (hash) {
            const targetId = hash.substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                setTimeout(() => {
                    this.smoothScrollTo(targetElement);
                    this.updateActiveNavLink(targetId);
                }, 100);
            }
        } else {
            // Default to overview section
            const overviewLink = document.querySelector('[href="#overview"]');
            if (overviewLink) {
                overviewLink.classList.add('active');
            }
        }
    }
}

// Enhanced clipboard functionality with error handling
class ClipboardManager {
    constructor() {
        this.setupCopyButtons();
    }

    setupCopyButtons() {
        // Add copy buttons to code blocks
        document.querySelectorAll('.code-block').forEach(codeBlock => {
            if (!codeBlock.querySelector('.copy-btn')) {
                const copyBtn = this.createCopyButton();
                codeBlock.style.position = 'relative';
                codeBlock.appendChild(copyBtn);
            }
        });
    }

    createCopyButton() {
        const button = document.createElement('button');
        button.className = 'copy-btn';
        button.innerHTML = '<i class="fas fa-copy" aria-hidden="true"></i>';
        button.setAttribute('aria-label', 'Copy code to clipboard');
        button.setAttribute('title', 'Copy code');
        
        button.addEventListener('click', (e) => {
            this.copyCode(e.target.closest('.code-block'));
        });
        
        return button;
    }

    async copyCode(codeBlock) {
        const code = codeBlock.querySelector('code');
        if (!code) {
            console.warn('No code element found in code block');
            return;
        }

        const text = code.textContent || code.innerText;
        if (!text.trim()) {
            console.warn('No text content to copy');
            this.showCopyFeedback(codeBlock, 'Nothing to copy', true);
            return;
        }

        try {
            // Check for modern clipboard API support
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(text);
                this.showCopyFeedback(codeBlock, 'Copied!');
            } else {
                // Fallback for older browsers or non-secure contexts
                const success = this.fallbackCopyTextToClipboard(text);
                if (success) {
                    this.showCopyFeedback(codeBlock, 'Copied!');
                } else {
                    throw new Error('Fallback copy method failed');
                }
            }
        } catch (err) {
            console.error('Failed to copy text: ', err);
            this.showCopyFeedback(codeBlock, 'Copy failed', true);

            // Provide user feedback about the error
            if (err.name === 'NotAllowedError') {
                console.warn('Copy permission denied. User may need to interact with the page first.');
            } else if (!window.isSecureContext) {
                console.warn('Clipboard API requires HTTPS or localhost');
            }
        }
    }

    fallbackCopyTextToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;

        // Make the textarea invisible but accessible
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        textArea.style.width = '2em';
        textArea.style.height = '2em';
        textArea.style.padding = '0';
        textArea.style.border = 'none';
        textArea.style.outline = 'none';
        textArea.style.boxShadow = 'none';
        textArea.style.background = 'transparent';

        document.body.appendChild(textArea);

        try {
            textArea.focus();
            textArea.select();

            // For iOS Safari
            textArea.setSelectionRange(0, 99999);

            const successful = document.execCommand('copy');
            if (!successful) {
                throw new Error('execCommand copy failed');
            }
            return true;
        } catch (err) {
            console.error('Fallback copy failed:', err);
            return false;
        } finally {
            document.body.removeChild(textArea);
        }
    }

    showCopyFeedback(codeBlock, message, isError = false) {
        const copyBtn = codeBlock.querySelector('.copy-btn');
        if (!copyBtn) return;

        const originalContent = copyBtn.innerHTML;
        copyBtn.innerHTML = message;
        copyBtn.style.background = isError ? 'var(--error-color)' : 'var(--success-color)';
        
        setTimeout(() => {
            copyBtn.innerHTML = originalContent;
            copyBtn.style.background = '';
        }, 2000);
    }
}

// Mobile menu management
class MobileMenuManager {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.toggle = document.querySelector('.mobile-menu-toggle');
        this.isOpen = false;
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Toggle mobile menu
        if (this.toggle) {
            this.toggle.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleMenu();
            });
        }

        // Close menu when clicking outside (with debouncing)
        let clickTimeout;
        document.addEventListener('click', (event) => {
            if (clickTimeout) clearTimeout(clickTimeout);

            clickTimeout = setTimeout(() => {
                if (this.isOpen && this.sidebar && this.toggle &&
                    !this.sidebar.contains(event.target) &&
                    !this.toggle.contains(event.target)) {
                    this.closeMenu();
                }
            }, 10);
        });

        // Close mobile menu when clicking on nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                this.closeMenu();
            });
        });

        // Handle escape key and other accessibility keys
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeMenu();
                // Return focus to toggle button
                if (this.toggle) {
                    this.toggle.focus();
                }
            }
        });

        // Handle window resize with debouncing
        let resizeTimeout;
        window.addEventListener('resize', () => {
            if (resizeTimeout) clearTimeout(resizeTimeout);

            resizeTimeout = setTimeout(() => {
                // Close menu on desktop breakpoint
                if (window.innerWidth > 768 && this.isOpen) {
                    this.closeMenu();
                }

                // Adjust layout for very small screens
                this.adjustForSmallScreens();
            }, 100);
        });
    }

    adjustForSmallScreens() {
        const isVerySmall = window.innerWidth <= 320;
        const isExtraSmall = window.innerWidth <= 280;

        // Adjust font sizes for very small screens
        if (isExtraSmall) {
            document.documentElement.style.fontSize = '14px';
        } else if (isVerySmall) {
            document.documentElement.style.fontSize = '15px';
        } else {
            document.documentElement.style.fontSize = '16px';
        }

        // Adjust sidebar width for very small screens
        if (this.sidebar) {
            if (isExtraSmall) {
                this.sidebar.style.width = '260px';
            } else {
                this.sidebar.style.width = '280px';
            }
        }

        // Optimize touch targets for small screens
        if (isVerySmall) {
            const navLinks = document.querySelectorAll('.nav-link');
            navLinks.forEach(link => {
                link.style.minHeight = '44px'; // iOS recommended touch target
                link.style.display = 'flex';
                link.style.alignItems = 'center';
            });
        }
    }

    toggleMenu() {
        if (this.sidebar) {
            this.isOpen = !this.isOpen;
            this.sidebar.classList.toggle('open', this.isOpen);

            // Update ARIA attributes
            if (this.toggle) {
                this.toggle.setAttribute('aria-expanded', this.isOpen.toString());
            }

            // Manage focus for accessibility
            if (this.isOpen) {
                // Focus first nav link when menu opens
                const firstNavLink = this.sidebar.querySelector('.nav-link');
                if (firstNavLink) {
                    firstNavLink.focus();
                }
            }
        }
    }

    closeMenu() {
        if (this.sidebar && this.isOpen) {
            this.isOpen = false;
            this.sidebar.classList.remove('open');

            // Update ARIA attributes
            if (this.toggle) {
                this.toggle.setAttribute('aria-expanded', 'false');
            }
        }
    }
}

// Language switching functionality
class LanguageManager {
    constructor() {
        this.currentLang = 'en';
        this.setupLanguageToggle();
    }

    setupLanguageToggle() {
        const langButtons = document.querySelectorAll('.lang-btn');

        langButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const targetLang = e.target.getAttribute('data-lang');
                this.switchLanguage(targetLang);
            });
        });

        // Load saved language preference
        const savedLang = localStorage.getItem('nd-script-lang') || 'en';
        this.switchLanguage(savedLang);
    }

    switchLanguage(lang) {
        if (lang === this.currentLang) return;

        this.currentLang = lang;

        // Update button states
        document.querySelectorAll('.lang-btn').forEach(btn => {
            const isActive = btn.getAttribute('data-lang') === lang;
            btn.classList.toggle('active', isActive);
            btn.setAttribute('aria-pressed', isActive.toString());
        });

        // Update document direction
        document.documentElement.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');
        document.documentElement.setAttribute('lang', lang);

        // Save preference
        localStorage.setItem('nd-script-lang', lang);

        // Update content visibility based on language
        this.updateContentVisibility(lang);

        // Announce language change for screen readers
        this.announceLanguageChange(lang);
    }

    updateContentVisibility(lang) {
        // Show/hide language-specific content
        const englishElements = document.querySelectorAll('[lang="en"]');
        const arabicElements = document.querySelectorAll('[lang="ar"], .arabic-text');

        englishElements.forEach(el => {
            el.style.display = lang === 'en' ? '' : 'none';
        });

        arabicElements.forEach(el => {
            el.style.display = lang === 'ar' ? '' : 'none';
        });
    }

    announceLanguageChange(lang) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = lang === 'ar' ?
            'تم تغيير اللغة إلى العربية' :
            'Language changed to English';

        document.body.appendChild(announcement);

        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }
}

// Small screen optimization utilities
class SmallScreenOptimizer {
    constructor() {
        this.isSmallScreen = window.innerWidth <= 320;
        this.isExtraSmall = window.innerWidth <= 280;
        this.init();
    }

    init() {
        this.optimizeForSmallScreens();
        this.setupViewportOptimization();
    }

    optimizeForSmallScreens() {
        if (!this.isSmallScreen) return;

        // Reduce animations on small screens for better performance
        const style = document.createElement('style');
        style.textContent = `
            @media (max-width: 320px) {
                *, *::before, *::after {
                    animation-duration: 0.1s !important;
                    transition-duration: 0.1s !important;
                }

                .feature-card:hover {
                    transform: none !important;
                }

                .btn:hover {
                    transform: none !important;
                }
            }
        `;
        document.head.appendChild(style);

        // Optimize touch interactions
        this.optimizeTouchTargets();
    }

    optimizeTouchTargets() {
        // Ensure minimum touch target size (44px recommended)
        const touchElements = document.querySelectorAll('button, a, .nav-link, .btn');
        touchElements.forEach(element => {
            const rect = element.getBoundingClientRect();
            if (rect.height < 44) {
                element.style.minHeight = '44px';
                element.style.display = 'flex';
                element.style.alignItems = 'center';
                element.style.justifyContent = 'center';
            }
        });
    }

    setupViewportOptimization() {
        // Prevent zoom on input focus for iOS
        const viewport = document.querySelector('meta[name="viewport"]');
        if (viewport && this.isSmallScreen) {
            viewport.setAttribute('content',
                'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'
            );
        }

        // Add safe area support for notched devices
        if (CSS.supports('padding-top: env(safe-area-inset-top)')) {
            document.documentElement.style.paddingTop = 'env(safe-area-inset-top)';
            document.documentElement.style.paddingBottom = 'env(safe-area-inset-bottom)';
        }
    }
}

// Initialize all managers when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const navigationManager = new NavigationManager();
    const clipboardManager = new ClipboardManager();
    const mobileMenuManager = new MobileMenuManager();
    const languageManager = new LanguageManager();
    const smallScreenOptimizer = new SmallScreenOptimizer();

    // Handle initial page load
    navigationManager.handlePageLoad();

    // Initial small screen adjustments
    mobileMenuManager.adjustForSmallScreens();
});

// Handle page load event as well for better compatibility
window.addEventListener('load', () => {
    const navigationManager = new NavigationManager();
    navigationManager.handlePageLoad();
});
