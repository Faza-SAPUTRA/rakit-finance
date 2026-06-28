(function () {
  if (!window.gsap) return;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reducedMotion) return;

  gsap.registerPlugin(ScrollTrigger);

  gsap.utils.toArray(".reveal").forEach((element) => {
    gsap.from(element, {
      opacity: 0,
      y: 28,
      duration: 0.8,
      ease: "power3.out",
      scrollTrigger: { trigger: element, start: "top 88%" },
    });
  });

  gsap.utils.toArray(".counter").forEach((element) => {
    const target = Number(element.dataset.target || 0);
    const prefix = element.dataset.prefix || "";
    const suffix = element.dataset.suffix || "";
    gsap.fromTo(
      element,
      { innerText: 0 },
      {
        innerText: target,
        duration: 1.2,
        ease: "power2.out",
        snap: { innerText: 1 },
        scrollTrigger: { trigger: element, start: "top 90%" },
        onUpdate: () => {
          element.textContent = `${prefix}${Number(element.innerText).toLocaleString("id-ID")}${suffix}`;
        },
      }
    );
  });
})();

