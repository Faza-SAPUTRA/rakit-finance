(function () {
  if (!window.gsap) return;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reducedMotion) return;

  gsap.registerPlugin(ScrollTrigger);

  const landingPage = document.querySelector(".hero-surface");
  if (landingPage) {
    const root = document.documentElement;
    let currentY = window.scrollY;
    let targetY = currentY;
    let maxY = 0;
    const clamp = (value) => Math.max(0, Math.min(value, maxY));
    const refreshBounds = () => {
      maxY = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
      targetY = clamp(targetY);
      currentY = clamp(currentY);
    };

    root.classList.add("smooth-scroll-active");
    refreshBounds();

    window.addEventListener(
      "wheel",
      (event) => {
        if (event.ctrlKey) return;
        event.preventDefault();
        targetY = clamp(targetY + event.deltaY * 0.92);
      },
      { passive: false }
    );

    window.addEventListener("resize", () => {
      refreshBounds();
      ScrollTrigger.refresh();
    });
    window.addEventListener("load", refreshBounds);
    ScrollTrigger.addEventListener("refresh", refreshBounds);

    window.addEventListener("keydown", (event) => {
      const activeTag = document.activeElement?.tagName;
      if (["INPUT", "TEXTAREA", "SELECT"].includes(activeTag)) return;

      const moves = {
        ArrowDown: 96,
        ArrowUp: -96,
        PageDown: window.innerHeight * 0.82,
        PageUp: window.innerHeight * -0.82,
        Home: -Infinity,
        End: Infinity,
      };
      if (!(event.key in moves)) return;

      event.preventDefault();
      const move = moves[event.key];
      targetY = move === Infinity ? maxY : move === -Infinity ? 0 : clamp(targetY + move);
    });

    document.querySelectorAll('a[href^="#"]').forEach((link) => {
      link.addEventListener("click", (event) => {
        const target = document.querySelector(link.getAttribute("href"));
        if (!target) return;
        event.preventDefault();
        targetY = clamp(target.getBoundingClientRect().top + window.scrollY - 84);
      });
    });

    gsap.ticker.add(() => {
      const delta = targetY - currentY;
      currentY += delta * 0.085;
      if (Math.abs(delta) < 0.35) currentY = targetY;
      window.scrollTo(0, currentY);
      ScrollTrigger.update();
    });
  }

  gsap.utils.toArray(".reveal").forEach((element) => {
    if (element.matches(".feature-card-3d, .how-step-card")) return;
    gsap.from(element, {
      opacity: 0,
      y: 28,
      duration: 0.8,
      ease: "power3.out",
      scrollTrigger: { trigger: element, start: "top 88%" },
    });
  });

  const featureGrid = document.querySelector(".feature-grid-3d");
  const featureCards = gsap.utils.toArray(".feature-card-3d");
  if (featureGrid && featureCards.length) {
    gsap.set(featureGrid, { transformPerspective: 1100 });
    gsap.fromTo(
      featureCards,
      {
        opacity: 0,
        y: 34,
        rotationY: (index) => (index % 2 === 0 ? 35 : -35),
        rotationX: 8,
        z: -80,
        transformOrigin: "50% 50%",
      },
      {
        opacity: 1,
        y: 0,
        rotationY: 0,
        rotationX: 0,
        z: 0,
        duration: 0.95,
        ease: "power3.out",
        stagger: { each: 0.08, from: "start" },
        scrollTrigger: { trigger: featureGrid, start: "top 78%" },
      }
    );
  }

  const howSection = document.querySelector("#how");
  const howCards = gsap.utils.toArray(".how-step-card");
  if (howSection && howCards.length) {
    const connectorPaths = gsap.utils.toArray(".how-connector-path");
    connectorPaths.forEach((path) => {
      const length = path.getTotalLength();
      gsap.set(path, { strokeDasharray: length, strokeDashoffset: length });
    });

    if (connectorPaths[0]) {
      gsap.to(connectorPaths[0], {
        strokeDashoffset: 0,
        ease: "none",
        scrollTrigger: {
          trigger: howSection,
          start: "top 70%",
          end: "center 55%",
          scrub: 0.9,
        },
      });
    }

    if (connectorPaths[1]) {
      gsap.to(connectorPaths[1], {
        strokeDashoffset: 0,
        ease: "none",
        scrollTrigger: {
          trigger: howSection,
          start: "center 58%",
          end: "bottom 42%",
          scrub: 0.9,
        },
      });
    }

    gsap.set(".how-steps-3d", { transformPerspective: 1100 });
    gsap.fromTo(
      howCards,
      {
        opacity: 0,
        y: 28,
        rotationX: 24,
        z: -90,
      },
      {
        opacity: 1,
        y: 0,
        rotationX: 0,
        z: 0,
        duration: 0.85,
        ease: "power3.out",
        stagger: 0.1,
        scrollTrigger: { trigger: howSection, start: "top 78%" },
      }
    );

    howCards.forEach((card, index) => {
      const direction = index - 1;
      gsap.to(card, {
        z: 70 - index * 18,
        rotationY: direction * -5,
        rotationX: 4 + index * 2,
        y: direction * -12,
        ease: "none",
        scrollTrigger: {
          trigger: howSection,
          start: "top bottom",
          end: "bottom top",
          scrub: true,
        },
      });
    });
  }

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
