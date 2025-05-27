const menu = document.querySelector("#sidemenu");
const body = document.querySelector("body");
const navbar = document.querySelector("#navbar");
const menubar = document.querySelector("#menubar");
function openMenu() {
  const backdrop = document.getElementById('mobile-backdrop');
  const sidemenu = document.getElementById('sidemenu');
  
  // Show the menu and backdrop
  sidemenu.classList.add('translate-x-0');
  sidemenu.classList.remove('translate-x-full');
  backdrop.classList.remove('hidden');
  
  // Prevent body scrolling
  document.body.classList.add('overflow-hidden');
  
  // Add event listeners for escape key
  document.addEventListener('keydown', closeMenuOnEscape);
}

function closeMenu() {
  const backdrop = document.getElementById('mobile-backdrop');
  const sidemenu = document.getElementById('sidemenu');
  
  // Hide the menu and backdrop
  sidemenu.classList.remove('translate-x-0');
  sidemenu.classList.add('translate-x-full');
  backdrop.classList.add('hidden');
  
  // Allow body scrolling again
  document.body.classList.remove('overflow-hidden');
  
  // Remove event listeners
  document.removeEventListener('keydown', closeMenuOnEscape);
}

function closeMenuOnEscape(e) {
  if (e.key === 'Escape') {
    closeMenu();
  }
}
// Initialize mobile menu when the page loads
document.addEventListener('DOMContentLoaded', function() {
  // Initialize mobile menu variables
  const sidemenu = document.getElementById('sidemenu');
  const backdrop = document.getElementById('mobile-backdrop');
  const closeButton = document.getElementById('close-menu');
  const openButton = document.getElementById('open-menu');
  
  // Ensure menu starts in the correct state
  if (sidemenu) {
    sidemenu.classList.add('translate-x-full');
  }
  
  // Add click handlers to all mobile menu links that should close the menu
  const mobileMenuLinks = document.querySelectorAll('#sidemenu a[onclick="closeMenu()"]');
  mobileMenuLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      // Keep the link's default behavior but also close the menu
      closeMenu();
    });
  });
});

window.addEventListener("scroll", () => {
  if (scrollY < 50) {
    navbar.classList.remove(
      "bg-white",
      "bg-opacity-50",
      "backdrop-blur-lg",
      "shadow-sm",
      "dark:bg-darkTheme",
      "dark:shadow-white/20",
    );
    menubar.classList.add(
      "bg-opacity-50",
      "shadow-sm",
      "dark:border-white/50",
      "border",
    );
  } else {
    navbar.classList.add(
      "bg-white",
      "bg-opacity-50",
      "backdrop-blur-lg",
      "shadow-sm",
      "dark:bg-darkTheme",
      "dark:shadow-white/20",
    );
    menubar.classList.remove(
      "bg-opacity-50",
      "shadow-sm",
      "dark:border-white/50",
      "border",
    );
  }
});
if (
  localStorage.theme === "dark" ||
  (!("theme" in localStorage) &&
    window.matchMedia("(prefers-color-scheme: dark)").matches)
) {
  document.documentElement.classList.add("dark");
} else {
  document.documentElement.classList.remove("dark");
}
function toggleTheme() {
  document.documentElement.classList.toggle("dark");
  if (document.documentElement.classList.contains("dark")) {
    localStorage.theme = "dark";
  } else {
    localStorage.theme = "light";
  }
}

// call back function for handling token of recaptcha
function validateRecaptcha() {
  var recaptchaResponse = document.getElementById("g-recaptcha-response").value;
  if (recaptchaResponse.length === 0) {
    document.getElementById("recaptcha-error").style.display = "block";
    return false;
  }
  return true;
}

function recaptchaCallback(response) {
  document.getElementById("g-recaptcha-response").value = response;
  document.getElementById("recaptcha-error").style.display = "none";
}

document
  .getElementById("form-submit")
  .addEventListener("submit", function (event) {
    if (!validateRecaptcha()) {
      event.preventDefault();
    }
  });

document.addEventListener('DOMContentLoaded', function() {
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.classList.add('lazy-image');
                
                img.onload = () => {
                    img.classList.add('loaded');
                };
                
                observer.unobserve(img);
            }
        });
    });
    
    lazyImages.forEach(img => imageObserver.observe(img));
});
