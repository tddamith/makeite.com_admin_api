// Smooth fade-in animation
document.addEventListener("DOMContentLoaded", () => {
  const card = document.querySelector(".invitation-card");
  card.style.opacity = 0;

  setTimeout(() => {
    card.style.transition = "1.2s ease";
    card.style.opacity = 1;
  }, 150);
});
