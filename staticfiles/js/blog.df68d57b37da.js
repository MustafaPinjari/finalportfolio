function likeComment(commentId) {
    // Find all like buttons for this comment (there might be multiple instances)
    const likeBtns = document.querySelectorAll(`[data-comment-id="${commentId}"]`);
    
    fetch(`/comment/${commentId}/like/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Update all instances of the like button for this comment
        likeBtns.forEach(likeBtn => {
            const likesCount = likeBtn.querySelector('.likes-count');
            const heartIcon = likeBtn.querySelector('i');
            
            // Update the likes count
            likesCount.textContent = data.likes_count;
            
            // Update the heart icon
            if (data.liked) {
                heartIcon.classList.remove('far');
                heartIcon.classList.add('fas');
                likeBtn.classList.add('text-coral');
                likeBtn.classList.remove('text-gray-400');
            } else {
                heartIcon.classList.remove('fas');
                heartIcon.classList.add('far');
                likeBtn.classList.remove('text-coral');
                likeBtn.classList.add('text-gray-400');
            }
            
            // Add a subtle animation
            heartIcon.style.transform = 'scale(1.2)';
            setTimeout(() => {
                heartIcon.style.transform = 'scale(1)';
            }, 200);
        });
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function toggleFavorite(postId) {
    // Fix the URL path - it should be relative to the site root
    fetch(`/blog/post/${postId}/favorite/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin' // Important for including cookies
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Find all favorite buttons for this post (there might be multiple instances)
        const favButtons = document.querySelectorAll(`.favorite-btn[data-post-id="${postId}"]`);
        
        favButtons.forEach(button => {
            const icon = button.querySelector('i');
            const label = button.querySelector('.favorite-label');
            
            // Update icon and text based on favorite status
            if (data.is_favorite) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                if (label) label.textContent = 'Saved';
                button.classList.add('is-favorite');
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
                if (label) label.textContent = 'Save';
                button.classList.remove('is-favorite');
            }
            
            // Add a subtle animation
            icon.style.transform = 'scale(1.2)';
            setTimeout(() => {
                icon.style.transform = 'scale(1)';
            }, 200);
        });
    })
    .catch(error => {
        console.error('Error toggling favorite:', error);
        alert('There was an error saving this post. Please try again.');
    });
}

function getCookie(name) {
    // First try to get the token from cookies
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    
    // If not found in cookies, try to get it from meta tag
    if (!cookieValue) {
        const csrfToken = document.querySelector('meta[name="csrf-token"]');
        if (csrfToken) {
            cookieValue = csrfToken.getAttribute('content');
        }
    }
    
    return cookieValue;
}

// Handle comment form submission via AJAX
document.addEventListener('DOMContentLoaded', function() {
    const commentForm = document.getElementById('comment-form');
    
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent default form submission
            
            const formData = new FormData(commentForm);
            const postSlug = window.location.pathname.split('/').filter(segment => segment).pop();
            
            fetch(window.location.pathname, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Clear the comment form
                    commentForm.reset();
                    
                    // Reload the page to show the new comment
                    // This is a simple approach - for a more sophisticated solution,
                    // you could dynamically add the new comment to the DOM
                    window.location.reload();
                }
            })
            .catch(error => {
                console.error('Error submitting comment:', error);
            });
        });
    }
});