// User dropdown menu functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dropdown script loaded and running');
    
    // User dropdown for authenticated users
    const userMenuButton = document.getElementById('user-menu-button');
    const userDropdown = document.getElementById('user-dropdown');
    
    if (userMenuButton && userDropdown) {
        console.log('Found user menu elements');
        
        // Toggle dropdown when clicking the button
        userMenuButton.addEventListener('click', function(e) {
            console.log('User menu button clicked');
            e.stopPropagation();
            e.preventDefault(); // Prevent default only for the button
            userDropdown.classList.toggle('hidden');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!userMenuButton.contains(e.target) && !userDropdown.contains(e.target)) {
                userDropdown.classList.add('hidden');
            }
        });
        
        // Make sure links in dropdown work
        const dropdownLinks = userDropdown.querySelectorAll('a');
        dropdownLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                // Don't prevent default for links - allow normal navigation
                console.log('Dropdown link clicked:', this.href);
                // Optionally hide dropdown after link click
                userDropdown.classList.add('hidden');
            });
        });
    } else {
        console.log('User menu elements not found');
    }
});
