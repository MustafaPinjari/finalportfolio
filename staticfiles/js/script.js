const menu = document.querySelector("#sidemenu");
const body = document.querySelector("body");
const navbar = document.querySelector("#navbar");
const menubar = document.querySelector("#menubar");
function openMenu() {
  menu.style.transform = "translateX(-16rem)";
  // body.style.background = "black";
  // body.style.opacity = "0.1";
}
function closeMenu() {
  menu.style.transform = "translateX(16rem)";
  // body.style.background = "white";
  // body.style.opacity = "1";
}
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
