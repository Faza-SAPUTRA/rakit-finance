(function () {
  if (!window.gsap || !window.ScrollTrigger) return;

  const section = document.querySelector(".scroll-stack-section");
  const pin = document.querySelector(".scroll-stack-pin");
  const cards = gsap.utils.toArray("[data-stack-card]");
  if (!section || !pin || cards.length === 0) return;

  gsap.registerPlugin(ScrollTrigger);

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function revealStaticCards() {
    cards.forEach((card) => {
      card.style.position = "relative";
      card.style.transform = "none";
      card.style.opacity = "1";
    });
    pin.style.display = "grid";
    pin.style.gap = "20px";
    pin.style.minHeight = "auto";

    if (!reducedMotion) {
      gsap.from(cards, {
        opacity: 0,
        y: 28,
        duration: 0.7,
        ease: "power3.out",
        stagger: 0.08,
        scrollTrigger: { trigger: section, start: "top 82%" },
      });
    }
  }

  if (reducedMotion || window.matchMedia("(max-width: 767px)").matches) {
    revealStaticCards();
    return;
  }

  gsap.set(pin, { minHeight: 620 });
  gsap.set(cards, {
    position: "absolute",
    top: 0,
    left: 0,
    zIndex: (index) => index + 1,
    y: (index) => 360 + index * 44,
    scale: 0.92,
    opacity: 0,
    rotateX: 10,
    transformOrigin: "top center",
  });

  const timeline = gsap.timeline({
    defaults: { ease: "none" },
    scrollTrigger: {
      trigger: section,
      start: "top top",
      end: () => `+=${cards.length * 520}`,
      scrub: 0.85,
      pin,
      anticipatePin: 1,
      invalidateOnRefresh: true,
    },
  });

  cards.forEach((card, index) => {
    timeline.to(
      card,
      {
        y: index * 28,
        scale: 1 - index * 0.025,
        opacity: 1,
        rotateX: 0,
        duration: 0.8,
      },
      index * 0.72
    );

    if (index > 0) {
      timeline.to(
        cards.slice(0, index),
        {
          y: (cardIndex) => cardIndex * 22 - index * 4,
          scale: (cardIndex) => 1 - (index - cardIndex) * 0.032,
          duration: 0.55,
        },
        index * 0.72
      );
    }
  });

  ScrollTrigger.addEventListener("refreshInit", () => {
    cards.forEach((card) => {
      card.style.width = `${pin.clientWidth}px`;
    });
  });
  ScrollTrigger.refresh();
})();
