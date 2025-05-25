// User Menu Toggle Functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('User menu script loaded!');

    // User menu dropdown for authenticated users
    const userMenuButton = document.getElementById('user-menu-button');
    const userDropdown = document.getElementById('user-dropdown');

    if (userMenuButton && userDropdown) {
        console.log('Found authenticated user menu elements');
        userMenuButton.addEventListener('click', function(event) {
            console.log('User menu button clicked');
            event.stopPropagation();
            userDropdown.classList.toggle('hidden');
            
            // Close user type dropdown if open
            const userTypeDropdown = document.getElementById('user-type-dropdown');
            if (userTypeDropdown && !userTypeDropdown.classList.contains('hidden')) {
                userTypeDropdown.classList.add('hidden');
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            if (!userMenuButton.contains(event.target) && !userDropdown.contains(event.target)) {
                userDropdown.classList.add('hidden');
            }
        });
    }
    
    // User type dropdown for non-authenticated users
    const userTypeButton = document.getElementById('user-type-button');
    const userTypeDropdown = document.getElementById('user-type-dropdown');
    
    console.log('User type button:', userTypeButton);
    console.log('User type dropdown:', userTypeDropdown);
    
    if (userTypeButton && userTypeDropdown) {
        console.log('Found user type dropdown elements');
        
        userTypeButton.addEventListener('click', function(event) {
            console.log('User type button clicked');
            event.stopPropagation();
            event.preventDefault();
            userTypeDropdown.classList.toggle('hidden');
            userTypeButton.setAttribute('aria-expanded', userTypeDropdown.classList.contains('hidden') ? 'false' : 'true');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            if (!userTypeButton.contains(event.target) && !userTypeDropdown.contains(event.target)) {
                userTypeDropdown.classList.add('hidden');
                userTypeButton.setAttribute('aria-expanded', 'false');
            }
        });
        
        // Make sure links work without interference
        const typeDropdownLinks = userTypeDropdown.querySelectorAll('a');
        typeDropdownLinks.forEach(link => {
            link.addEventListener('click', function(event) {
                // Don't prevent default navigation behavior
                console.log("Navigating to:", this.href);
            });
        });
    } else {
        console.log('User type dropdown elements not found');
    }

    // Log all user-related elements for debugging
    console.log('All buttons with ID containing "user":');
    document.querySelectorAll('[id*="user"]').forEach(el => {
        console.log(el.id, el);
    });
});
