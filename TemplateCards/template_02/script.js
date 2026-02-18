// Make some blocks editable quickly for live edits
// Click any text to edit; click outside to save changes to localStorage
(function () {
  const editableSelectors = [
    ".couple-names",
    ".surname",
    ".big-title",
    ".date-number",
    ".date-info",
    ".desc",
    ".rsvp div:first-child",
    ".rsvp div:last-child",
  ];
  editableSelectors.forEach((sel) => {
    const el = document.querySelector(sel);
    if (!el) return;
    el.setAttribute("contenteditable", "true");
    el.classList.add("editable");
    // load saved
    const key = "invitation_" + sel;
    const saved = localStorage.getItem(key);
    if (saved) el.innerHTML = saved;
    el.addEventListener("blur", () => localStorage.setItem(key, el.innerHTML));
  });
})();
