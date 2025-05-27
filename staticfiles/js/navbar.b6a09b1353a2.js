document.addEventListener("DOMContentLoaded", () => {
    const dropdown = document.querySelector(".dropdown");
    dropdown.addEventListener("click", (e) => {
        const content = dropdown.querySelector(".dropdown-content");
        content.classList.toggle("show");
    });
});
