export function initNavbar() {
  const contactBtn = document.getElementById("contactBtn");
  const contactMenu = document.getElementById("contactMenu");
  const emailCopyBtn = document.getElementById("emailCopy");

  if (!contactBtn || !contactMenu) return;

  function closeMenu() {
    contactMenu.classList.remove("open");
    contactBtn.setAttribute("aria-expanded", "false");
  }

  contactBtn.addEventListener("click", (e) => {
    e.preventDefault();
    const isOpen = contactMenu.classList.toggle("open");
    contactBtn.setAttribute("aria-expanded", String(isOpen));
  });

  document.addEventListener("click", (e) => {
    if (!e.target.closest(".dropdown")) closeMenu();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeMenu();
  });

  if (emailCopyBtn) {
    const email = "mlw0135@auburn.edu";
    const originalText = emailCopyBtn.textContent;

    emailCopyBtn.addEventListener("click", async () => {
      await navigator.clipboard.writeText(email);

      emailCopyBtn.textContent = "Copied!";
      emailCopyBtn.disabled = true;

      setTimeout(() => {
        emailCopyBtn.textContent = originalText;
        emailCopyBtn.disabled = false;
        closeMenu();
      }, 900);
    });
  }
}
