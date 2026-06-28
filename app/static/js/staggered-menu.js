(function () {
  const menu = document.getElementById("staggered-menu");
  if (!menu) return;

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const openButtons = document.querySelectorAll("#staggered-menu-open, #staggered-menu-open-mobile");
  const closeButton = document.getElementById("staggered-menu-close");
  const backdrop = menu.querySelector(".staggered-menu-backdrop");
  const panel = menu.querySelector(".staggered-menu-panel");
  const links = Array.from(menu.querySelectorAll(".staggered-menu-link"));
  const triggerLines = document.querySelectorAll(".staggered-menu-trigger .staggered-menu-icon span");
  let isOpen = false;
  let timeline = null;

  function setExpanded(value) {
    openButtons.forEach((button) => button.setAttribute("aria-expanded", String(value)));
    menu.setAttribute("aria-hidden", String(!value));
    document.documentElement.classList.toggle("menu-open", value);
    menu.classList.toggle("is-open", value);
  }

  function setPointerEvents(value) {
    menu.classList.toggle("pointer-events-none", !value);
  }

  if (!reducedMotion && window.gsap) {
    gsap.set(menu, { autoAlpha: 0 });
    gsap.set(panel, { xPercent: 100 });
    gsap.set(links, { autoAlpha: 0, x: 72 });

    timeline = gsap.timeline({
      paused: true,
      defaults: { ease: "power3.out" },
      onStart: () => {
        setPointerEvents(true);
        setExpanded(true);
      },
      onReverseComplete: () => {
        setPointerEvents(false);
        setExpanded(false);
      },
    });

    timeline
      .to(menu, { autoAlpha: 1, duration: 0.18 }, 0)
      .to(panel, { xPercent: 0, duration: 0.58 }, 0)
      .to(triggerLines, { scaleX: 0.72, duration: 0.18, stagger: 0.03 }, 0)
      .to(links, { autoAlpha: 1, x: 0, duration: 0.56, stagger: 0.075 }, 0.18);
  }

  function openMenu() {
    if (isOpen) return;
    isOpen = true;
    setPointerEvents(true);
    setExpanded(true);

    if (timeline) {
      timeline.play(0);
      return;
    }

    menu.style.opacity = "1";
    panel.style.transform = "translateX(0)";
    links.forEach((link) => {
      link.style.opacity = "1";
      link.style.transform = "translateX(0)";
    });
  }

  function closeMenu() {
    if (!isOpen) return;
    isOpen = false;

    if (timeline) {
      timeline.reverse();
      return;
    }

    menu.style.opacity = "0";
    panel.style.transform = "translateX(100%)";
    setPointerEvents(false);
    setExpanded(false);
  }

  openButtons.forEach((button) => button.addEventListener("click", openMenu));
  closeButton?.addEventListener("click", closeMenu);
  backdrop?.addEventListener("click", closeMenu);
  links.forEach((link) => link.addEventListener("click", closeMenu));

  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMenu();
  });
})();
