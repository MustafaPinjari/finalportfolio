document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const notificationButton = document.getElementById('notification-button');
    const notificationDropdown = document.getElementById('notification-dropdown');
    const notificationList = document.getElementById('notification-list');
    const notificationBadge = document.getElementById('notification-badge');

    // Toggle notification dropdown
    if (notificationButton) {
        notificationButton.addEventListener('click', function(e) {
            e.preventDefault();
            notificationDropdown.classList.toggle('hidden');
            if (!notificationDropdown.classList.contains('hidden')) {
                // Load notifications when dropdown is opened
                loadNotifications();
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!notificationButton.contains(e.target) && !notificationDropdown.contains(e.target)) {
                notificationDropdown.classList.add('hidden');
            }
        });
    }

    // Function to load notifications
    function loadNotifications() {
        fetch('/notifications/user/recent/')
            .then(response => response.json())
            .then(data => {
                renderNotifications(data.notifications);
            })
            .catch(error => {
                console.error('Error loading notifications:', error);
                notificationList.innerHTML = `
                    <div class="px-4 py-3 text-center text-sm text-gray-500 dark:text-gray-400">
                        <p>Error loading notifications</p>
                    </div>
                `;
            });
    }

    // Function to render notifications
    function renderNotifications(notifications) {
        if (notifications.length === 0) {
            notificationList.innerHTML = `
                <div class="px-4 py-3 text-center text-sm text-gray-500 dark:text-gray-400">
                    <p>No notifications</p>
                </div>
            `;
            return;
        }

        let html = '';
        notifications.forEach(notification => {
            const isUnread = notification.status !== 'read';
            html += `
                <div class="notification-item border-b border-gray-100 dark:border-gray-700 ${isUnread ? 'bg-purple-50 dark:bg-purple-900/10' : ''}">
                    <a href="${notification.url || '#'}" class="block px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                        <div class="flex justify-between">
                            <p class="text-sm font-medium text-gray-900 dark:text-white">${notification.title}</p>
                            <p class="text-xs text-gray-500 dark:text-gray-400">${notification.time_ago}</p>
                        </div>
                        <p class="mt-1 text-xs text-gray-500 dark:text-gray-400 line-clamp-2">${notification.message}</p>
                    </a>
                </div>
            `;
        });

        notificationList.innerHTML = html;
    }

    // Function to update notification count
    function updateNotificationCount() {
        fetch('/notifications/user/count/')
            .then(response => response.json())
            .then(data => {
                const count = data.count;
                if (notificationBadge) {
                    if (count > 0) {
                        notificationBadge.textContent = count > 99 ? '99+' : count;
                        notificationBadge.classList.remove('d-none');
                    } else {
                        notificationBadge.classList.add('d-none');
                    }
                }
            })
            .catch(error => {
                console.error('Error updating notification count:', error);
            });
    }

    // Update count on page load
    updateNotificationCount();

    // Setup refresh interval
    setInterval(updateNotificationCount, 60000); // Every minute
});
