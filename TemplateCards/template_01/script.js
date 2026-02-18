// Auto-save editable text
document.querySelectorAll(".editable").forEach((el, index) => {
  const key = "invitation_field_" + index;
  const saved = localStorage.getItem(key);
  if (saved) el.innerHTML = saved;

  el.addEventListener("blur", () => {
    localStorage.setItem(key, el.innerHTML);
  });
});
