// Optional animation: gentle floating chick
document.addEventListener("DOMContentLoaded", () => {
  const chick = document.querySelector(".chick");
  let up = true;

  setInterval(() => {
    chick.style.transform = up
      ? "translate(-50%, -5px)"
      : "translate(-50%, 5px)";
    up = !up;
  }, 800);
});
