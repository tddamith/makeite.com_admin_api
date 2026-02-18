// Example: Add simple fade-in effect on load
document.addEventListener("DOMContentLoaded", () => {
  document.querySelector(".invitation-card").style.opacity = 0;
  setTimeout(() => {
    document.querySelector(".invitation-card").style.transition = "1.5s";
    document.querySelector(".invitation-card").style.opacity = 1;
  }, 200);
});
