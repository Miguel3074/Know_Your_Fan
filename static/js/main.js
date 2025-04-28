// main.js - Core site functionality

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 70, // Adjust for fixed navbar
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add active class to current navigation item
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (linkPath && currentLocation.includes(linkPath) && linkPath !== '/') {
            link.classList.add('active');
        } else if (linkPath === '/' && currentLocation === '/') {
            link.classList.add('active');
        }
    });

    // Profile navigation active state
    const profileNavLinks = document.querySelectorAll('.profile-nav-link');
    
    profileNavLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (linkPath && currentLocation.includes(linkPath)) {
            link.classList.add('active');
        }
    });

    // Flash message auto-dismiss
    const flashMessages = document.querySelectorAll('.alert-dismissible');
    
    flashMessages.forEach(message => {
        setTimeout(() => {
            const closeButton = message.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000); // 5 second auto-dismiss
    });

    // Animation on scroll
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    function checkScroll() {
        const windowHeight = window.innerHeight;
        const windowTop = window.pageYOffset;
        const windowBottom = windowTop + windowHeight;
        
        animatedElements.forEach(element => {
            const elementTop = element.offsetTop;
            const elementHeight = element.offsetHeight;
            const elementBottom = elementTop + elementHeight;
            
            if (windowBottom > elementTop && windowTop < elementBottom) {
                element.classList.add('animate__animated', 'animate__fadeIn');
            }
        });
    }
    
    window.addEventListener('scroll', checkScroll);
    checkScroll(); // Check on load

    // Initialize lightbox for document images
    document.querySelectorAll('.document-thumbnail').forEach(item => {
        item.addEventListener('click', event => {
            event.preventDefault();
            
            const imageUrl = item.getAttribute('href');
            const modalImage = document.getElementById('documentModalImage');
            const modal = new bootstrap.Modal(document.getElementById('documentModal'));
            
            if (modalImage && imageUrl) {
                modalImage.src = imageUrl;
                modal.show();
            }
        });
    });

    // Initialize Language Selector
    const languageSelector = document.getElementById('languageSelector');
    if (languageSelector) {
        languageSelector.addEventListener('change', function() {
            const language = this.value;
            // In a real app, this would update the page language
            console.log(`Language changed to: ${language}`);
            
            // For demo purposes, show a flash message
            const flashContainer = document.getElementById('flashMessages');
            if (flashContainer) {
                const alert = document.createElement('div');
                alert.className = 'alert alert-info alert-dismissible fade show';
                alert.role = 'alert';
                alert.innerHTML = `
                    Language changed to ${language === 'en' ? 'English' : 'Portuguese'}.
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                `;
                flashContainer.appendChild(alert);
                
                // Auto dismiss after 5 seconds
                setTimeout(() => {
                    alert.classList.remove('show');
                    setTimeout(() => {
                        flashContainer.removeChild(alert);
                    }, 150);
                }, 5000);
            }
        });
    }
});

// Toggle dark mode
function toggleDarkMode() {
    const htmlElement = document.documentElement;
    const isDarkMode = htmlElement.getAttribute('data-bs-theme') === 'dark';
    
    if (isDarkMode) {
        htmlElement.setAttribute('data-bs-theme', 'light');
        localStorage.setItem('theme', 'light');
    } else {
        htmlElement.setAttribute('data-bs-theme', 'dark');
        localStorage.setItem('theme', 'dark');
    }
}

// Check and set theme on page load
(function() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
})();
